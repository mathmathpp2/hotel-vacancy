import logging
from datetime import datetime
from time import sleep

from pynamodb.exceptions import UpdateError

from app.config import Config, load_config
from app.finder import SiteBFinder
from app.models import PlanModel

logger = logging.getLogger(__name__)


def main(configs: list[Config]) -> None:
    finder = SiteBFinder()
    for config in configs:
        if not config.enabled:
            continue

        logger.info(f"START: {config.name}")
        acm, plans, metadata = finder.find(config)
        if not plans:
            logger.info(f"No plans found for {acm.acm_name} {acm.acm_url}")

        for plan in plans:
            now = datetime.utcnow()
            try:
                existing_plan = PlanModel.get(plan.plan_id)
                logger.info(f"Updating the existing plan: {plan.plan_id}")
                try:
                    existing_plan.update(
                        actions=[
                            PlanModel.plan_name.set(plan.plan_name),
                            PlanModel.point_rate.set(plan.point_rate),
                            PlanModel.stay_time.set(plan.stay_time),
                            PlanModel.credit.set(plan.credit),
                            PlanModel.rooms.set(plan.rooms),
                            PlanModel.cheapest_room_name.set(plan.cheapest_room_name),
                            PlanModel.cheapest_room_type.set(plan.cheapest_room_type),
                            PlanModel.cheapest_area.set(plan.cheapest_area),
                            PlanModel.cheapest_meal.set(plan.cheapest_meal),
                            PlanModel.cheapest_price.set(plan.cheapest_price),
                            PlanModel.last_check_at.set(datetime.utcnow()),
                        ],
                        condition=(PlanModel.cheapest_price != plan.cheapest_price)
                        | (PlanModel.point_rate != plan.point_rate)
                        | (PlanModel.stay_time != plan.stay_time)
                        | (PlanModel.credit != plan.credit),
                    )
                except UpdateError:
                    logger.info("Not updated since the condition is not met")
            except PlanModel.DoesNotExist:
                logger.info(f"Saving new plan: {plan.plan_id}")
                plan_model = PlanModel(
                    plan_id=plan.plan_id,
                    acm_id=acm.acm_id,
                    acm_name=acm.acm_name,
                    pref_name=acm.pref_name,
                    area_name=acm.area_name,
                    small_area_name=acm.small_area_name,
                    score=acm.score,
                    acm_url=acm.acm_url,
                    plan_name=plan.plan_name,
                    catch_copy=plan.catch_copy,
                    point_rate=plan.point_rate,
                    stay_time=plan.stay_time,
                    credit=plan.credit,
                    rooms=plan.rooms,
                    cheapest_room_name=plan.cheapest_room_name,
                    cheapest_room_type=plan.cheapest_room_type,
                    cheapest_area=plan.cheapest_area,
                    cheapest_meal=plan.cheapest_meal,
                    cheapest_price=plan.cheapest_price,
                    search_url=metadata.search_url,
                    create_at=now,
                    last_check_at=now,
                )
                plan_model.save()

        sleep(5)


def lambda_handler(event, context) -> None:
    configs = load_config("./app/config.yml")
    main(configs)


if __name__ == "__main__":
    configs = load_config("./app/config.yml")
    main(configs)
