from typing import List, Dict
from enum import Enum
import random

from emoji import emojize


class StatusEffects(Enum):
    poisoned = 1
    stunned = 2
    immobile = 3
    sleeping = 4
    feeble = 5
    strengthened = 6


class Stats(Enum):
    mgt = 0
    swt = 1
    vit = 2
    smt = 3
    ins = 4

    # Not sure if this will be useful
    @property
    def get_stat_str(self) -> str:
        if self.value == Stats.mgt.value:
            return "mgt"
        elif self.value == Stats.swt.value:
            return "swt"
        elif self.value == Stats.vit.value:
            return "vit"
        elif self.value == Stats.smt.value:
            return "smt"
        else:
            return "ins"


class Pet:
    name: str
    level: int
    xp: int
    pet_stats: List[int]
    max_hp: int
    current_hp: int
    status_effects: List[StatusEffects]
    armor: int
    shield: int
    weapon: int
    hat: int

    def __init__(self, name: str):
        self.name = name
        self.level = 1
        self.xp = 0

        stat_bonuses = [0] * 5
        stat_bonuses[random.randint(0, 4)] += 2
        for _ in range(2):
            stat_bonuses[random.randint(0, 4)] += 1

        for i in range(5):
            self.pet_stats[i] = 1 + stat_bonuses[i]

        self.max_hp = 5 + ((self.pet_stats[Stats.vit.value] - 1) * 3)
        self.current_hp = self.max_hp

    def stat_inc(self, stat_to_inc: int, amount=1):
        self.pet_stats[stat_to_inc] += amount
