import logging
import os
import re
from abc import ABC
from collections import defaultdict
from copy import copy
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse

import requests
from pydantic import BaseModel

from app.config import Conditions, Config
from app.search_filter import SearchFilter

logger = logging.getLogger(__name__)


CREDIT_REGEX = re.compile(r"([\d一二三四五六七八九])万")


class Plan(BaseModel):
    plan_id: str
    plan_name: str
    catch_copy: str
    point_rate: float
    stay_time: float
    credit: float
    rooms: list[dict[str, Any]]
    cheapest_room_name: str
    cheapest_room_type: str
    cheapest_area: int
    cheapest_meal: str
    cheapest_price: int

    def meets_condition(self, cond: Conditions) -> bool:
        if cond.point_rate is not None and self.point_rate >= cond.point_rate:
            return True

        if cond.stay_time is not None and self.stay_time >= cond.stay_time:
            return True

        if cond.credit is not None and self.credit >= cond.credit:
            return True

        return False


class Acm(BaseModel):
    acm_id: str
    acm_name: str
    pref_name: str
    area_name: str
    small_area_name: str
    score: float
    acm_url: str


class Metadata(BaseModel):
    search_url: str


class Finder(ABC):
    site = None
    endpoint = None
    authority = None
    point_rate_field = None

    def _search(self, acm_id, filters):
        headers = {
            "authority": self.authority,
            "accept": "*/*",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "accept-language": "ja,en-US;q=0.9,en;q=0.8",
        }

        params = {
            "adc": "1",
            "aid": acm_id,
            "discsort": "1",
            "ipb": "1",
            "lc": "1",
            "mtc": "001",
            "ppc": "2",
            "rc": "1",
            "si": "8",
            "st": "1",
        }

        if not filters:
            filters = {}

        filter_params = defaultdict(int)
        for f in [SearchFilter.from_name(name) for name in filters]:
            filter_params[f.kind] |= f.int_value
        params.update(filter_params)

        return requests.get(self.endpoint, params=params, headers=headers)

    def _parse_room(self, room):
        return {
            "room_name": room["RmNm"],
            "square_meter_from": int(room["SquareMeterFrom"]),
            "square_meter_to": int(room["SquareMeterTo"]),
            "room_id": room["RmId"],
            "amount": int(room["Amount"]),
            "point_rate_local": int(room["PointRateLocal"]),
            "point_rate_card": int(room["PointRateCard"]),
            "point_rate": room[self.point_rate_field],
            "checkin_time_from": room["CheckinTmFrom"],
            "checkout_time": room["CheckoutTm"],
            "meal_name": room["MealNm"],
            "room_type_name": room["RmTypeNm"],
        }

    def _parse_plan(self, plan):
        def extract_point_rate(rooms):
            if rooms:
                return int(rooms[0]["point_rate"])
            else:
                return None

        def extract_stay_time(plan):
            checkin_time_from = plan["CheckinTmFrom"]
            checkout_time = plan["CheckoutTm"]
            return int(checkout_time[:2]) + 24 - int(checkin_time_from[:2])

        def extract_credit(plan):
            catch_copy = plan["CatchCopy"]
            credit_match = CREDIT_REGEX.search(catch_copy)
            if credit_match:
                return int(credit_match.group(1)) * 10000
            else:
                return 0

        rooms = []
        for room in plan["RmList"]:
            rooms.append(self._parse_room(room))

        rooms_noplan = []
        for room in rooms:
            room_noplan = copy(room)
            del room_noplan["point_rate_local"]
            del room_noplan["point_rate_card"]
            del room_noplan["point_rate"]
            del room_noplan["checkin_time_from"]
            del room_noplan["checkout_time"]
            rooms_noplan.append(room_noplan)

        cheapest_room = sorted(rooms, key=lambda x: x["amount"])[0]
        return Plan(
            plan_id=plan["PlnId"],
            plan_name=plan["PlnNm"],
            catch_copy=plan["CatchCopy"],
            point_rate=extract_point_rate(rooms),
            stay_time=extract_stay_time(plan),
            credit=extract_credit(plan),
            cheapest_room_name=cheapest_room["room_name"],
            cheapest_room_type=cheapest_room["room_type_name"],
            cheapest_area=cheapest_room["square_meter_from"],
            cheapest_meal=cheapest_room["meal_name"],
            cheapest_price=cheapest_room["amount"],
            rooms=rooms_noplan,
        )

    def _parse_acm(self, acm):
        return Acm(
            acm_id=acm["AcmId"],
            acm_name=acm["AcmNm"],
            pref_name=acm["PrefNm"],
            area_name=acm["AreaNm"],
            small_area_name=acm["SmallAreaNm"],
            score=acm["EvaluationScore"],
            acm_url=f"{self.site.rstrip('/')}/{acm['AcmId']}/",
        )

    def find(self, config: Config) -> tuple[Acm, list[Plan], Metadata]:
        def build_search_url(response):
            params = parse_qs(urlparse(response.request.url).query)
            del params["aid"]
            for k, v in params.items():
                params[k] = v[0]
            return os.path.join(self.site, acm.acm_id, "?" + urlencode(params))

        response = self._search(config.acm_id, config.filters)
        assert response.status_code == 200

        data = response.json()
        assert len(data["AcmList"]) == 1

        logger.debug(f"Request: {response.request.url}")

        plans = []
        for raw_plan in data["AcmList"][0]["PlnList"]:
            plan = self._parse_plan(raw_plan)
            if plan.meets_condition(config.conditions):
                plans.append(plan)

        acm = self._parse_acm(data["AcmList"][0])

        metadata = Metadata(
            search_url=build_search_url(response),
        )

        return acm, plans, metadata


class SiteAFinder(Finder):
    site = ""
    endpoint = ""
    authority = ""
    point_rate_field = ""


class SiteBFinder(Finder):
    site = ""
    endpoint = ""
    authority = ""
    point_rate_field = ""
