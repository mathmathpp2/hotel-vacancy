import logging
from typing import Optional

import yaml
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class Conditions(BaseModel):
    point_rate: Optional[int] = None
    stay_time: Optional[int] = None
    credit: Optional[int] = None


class GlobalConfig(BaseModel):
    filters: Optional[list[str]] = None
    conditions: Optional[Conditions] = None

    def __post_init__(self):
        if not self.filters:
            self.filters = []

        if not self.conditions:
            self.conditions = {}


class Config(BaseModel):
    acm_id: str
    name: Optional[str] = None
    sitea_url: Optional[str] = None
    siteb_url: Optional[str] = None
    filters: Optional[list[str]] = None
    conditions: Optional[Conditions] = None
    enabled: bool = True


def load_config(config_path: str) -> list[Config]:
    with open(config_path) as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)

    globals_ = GlobalConfig(**data["globals"])
    configs = []
    for hotel in data["hotels"]:
        config = Config(
            acm_id=hotel.get("acm_id"),
            name=hotel.get("name"),
            sitea_url=hotel.get("sitea_url"),
            siteb_url=hotel.get("siteb_url"),
            filters=globals_.filters + hotel.get("filters", []),
            conditions=globals_.conditions.dict() | hotel.get("conditions", {}),
            enabled=hotel.get("enabled"),
        )
        logger.debug(f"Config: {config}")
        configs.append(config)

    logger.debug(f"Loaded {len(configs)} configs")
    return configs
