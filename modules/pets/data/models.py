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
    emoji: str
    level: int
    xp_to_level: int
    current_xp: int
    pet_stats: List[int]
    max_hp: int
    current_hp: int
    status_effects: List[StatusEffects]
    armor: int
    shield: int
    weapon: int
    hat: int

    def __init__(self, desired_emoji: str):
        self.emoji = emojize(f":{desired_emoji}:")
        self.level = 1
        self.xp_to_level = 10
        self.current_xp = 0

        stat_bonuses = [0] * 5
        stat_bonuses[random.randint(0, 4)] += 2
        for _ in range(2):
            stat_bonuses[random.randint(0, 4)] += 1

        i = 0
        for stat in self.pet_stats:
            stat = 1 + stat_bonuses[i]
            i += 1

        self.max_hp = 5 + ((self.pet_stats[Stats.vit.value] - 1) * 3)
        self.current_hp = self.max_hp

    def stat_inc(self, stat_to_inc: str, amount=1):
        if stat_to_inc == "mgt":
            self.pet_stats[Stats.mgt.value] += amount
        elif stat_to_inc == "swt":
            self.pet_stats[Stats.swt.value] += amount
        elif stat_to_inc == "vit":
            self.pet_stats[Stats.vit.value] += amount
        elif stat_to_inc == "smt":
            self.pet_stats[Stats.smt.value] += amount
        elif stat_to_inc == "ins":
            self.pet_stats[Stats.ins.value] += amount
        else:
            print(f"Invalid Stat {stat_to_inc}")
            # TODO Error for invalid stat
