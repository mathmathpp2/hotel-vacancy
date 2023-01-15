from enum import Enum


class SearchFilter(Enum):
    CLUB_FLOOR = ("クラブフロア", "acr", 20)
    NO_SMOKING = ("禁煙", "acr", 21)

    @property
    def name(self):
        return self.value[0]

    @property
    def kind(self):
        return self.value[1]

    @property
    def nth_bit(self):
        return self.value[2]

    @property
    def int_value(self):
        return 1 << (self.nth_bit - 1)

    @staticmethod
    def from_name(name):
        for member_name, member in SearchFilter._member_map_.items():
            if name.lower() == member_name.lower():
                return member
        else:
            raise ValueError(f"Unknown filter name: {name}")
