from abc import ABC, abstractmethod

import requests
from jinja2 import BaseLoader, Environment
from slackweb import Slack

_TEMPLATE_STRING_INSERT = """
New Availability:

{{ plan.acm_name }}
{{ plan.plan_name }}
{{ plan.search_url }}
"""

_TEMPLATE_STRING_MODIFY = """
Availability Updated:

{{ plan.acm_name }}
{{ plan.plan_name }}
{{ plan.search_url }}
"""

TEMPLATE_INSERT = Environment(loader=BaseLoader, autoescape=False).from_string(
    _TEMPLATE_STRING_INSERT
)
TEMPLATE_MODIFY = Environment(loader=BaseLoader, autoescape=False).from_string(
    _TEMPLATE_STRING_MODIFY
)


class Notifer(ABC):
    @abstractmethod
    def notify(self, message: str) -> None:
        raise NotImplementedError


class LineNotifier(Notifer):
    def __init__(self, secret):
        self.secret = secret

    def notify(self, message: str) -> None:
        headers = {"Authorization": f"Bearer {self.secret}"}
        params = {"message": message}
        requests.post(
            "https://notify-api.line.me/api/notify", headers=headers, params=params
        )


class SlackWebhookNotifier(Notifer):
    def __init__(self, webhook_url):
        self.client = Slack(url=webhook_url)

    def notify(self, message: str) -> None:
        self.client.notify(text=message)
