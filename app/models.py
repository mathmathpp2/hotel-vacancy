from pynamodb.attributes import (
    JSONAttribute,
    NumberAttribute,
    UnicodeAttribute,
    UTCDateTimeAttribute,
)
from pynamodb.models import Model


class PlanModel(Model):
    class Meta:
        table_name = "plan"
        region = "ap-northeast-1"

    plan_id = UnicodeAttribute(hash_key=True)

    acm_id = UnicodeAttribute()
    acm_name = UnicodeAttribute()
    pref_name = UnicodeAttribute()
    area_name = UnicodeAttribute()
    small_area_name = UnicodeAttribute()
    score = NumberAttribute()
    acm_url = UnicodeAttribute()

    plan_name = UnicodeAttribute()
    catch_copy = UnicodeAttribute()
    point_rate = NumberAttribute()
    stay_time = NumberAttribute()
    credit = NumberAttribute()
    rooms = JSONAttribute()
    cheapest_room_name = UnicodeAttribute()
    cheapest_room_type = UnicodeAttribute()
    cheapest_area = NumberAttribute()
    cheapest_meal = UnicodeAttribute()
    cheapest_price = NumberAttribute()

    search_url = UnicodeAttribute()
    create_at = UTCDateTimeAttribute()
    last_check_at = UTCDateTimeAttribute()
