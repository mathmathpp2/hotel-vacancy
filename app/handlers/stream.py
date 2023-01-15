import logging
import os
from typing import Any

from app.config import Config, load_config
from app.models import PlanModel
from app.notifier import (
    TEMPLATE_INSERT,
    TEMPLATE_MODIFY,
    LineNotifier,
    SlackWebhookNotifier,
)

logger = logging.getLogger(__name__)

notifier_type = os.environ.get("NOTIFIER", "SLACK")


def main(configs: list[Config], records: list[dict[Any, Any]]):
    conditions = {config.acm_id: config.conditions for config in configs}

    if notifier_type == "SLACK":
        notifier = SlackWebhookNotifier(os.environ["SLACK_WEBHOOK"])
    elif notifier_type == "LINE":
        notifier = LineNotifier(os.environ["LINE_TOKEN"])
    else:
        raise ValueError(f"Unknown notifier: {notifier_type}")

    for record in records:
        event_name = record["eventName"]
        if event_name not in ["INSERT", "MODIFY"]:
            continue

        plan = PlanModel.from_raw_data(record["dynamodb"]["NewImage"])
        logger.info(f"START: {plan.plan_id=}, {event_name=}")

        params = {
            "plan": plan,
            "conditions": conditions[plan.acm_id],
        }

        if event_name == "INSERT":
            template = TEMPLATE_INSERT
        elif event_name == "MODIFY":
            template = TEMPLATE_MODIFY
            params["old_plan"] = PlanModel.from_raw_data(record["dynamodb"]["OldImage"])

        message = template.render(params)
        notifier.notify(message)


def lambda_handler(event, context) -> None:
    configs = load_config("./app/config.yml")
    main(configs=configs, records=event["Records"])
