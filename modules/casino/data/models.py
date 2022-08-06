from enum import Enum

JACKPOT_BASE = 1000


class SlotMachineSizes(Enum):
    sml = 1
    med = 25
    lrg = 100

    @property
    def generate_key(self) -> str:
        return "777" + str(self.value)
