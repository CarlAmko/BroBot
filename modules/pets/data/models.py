from typing import List
from enum import Enum

from emoji import emojize


class Status(Enum):
    poisoned = 1
    stunned = 2
    immobile = 3
    sleeping = 4
    feeble = 5
    strengthened = 6


class StatSet:
    mgt: int
    swt: int
    vit: int
    smt: int
    ins: int


class Pet:
    level: int
    xp_to_level: int
    current_xp: int
    stats: StatSet
    max_hp: int
    current_hp: int
    status_effects: List[Status]
    armor: int
    shield: int
    weapon: int
    hat: int
