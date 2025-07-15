from enum import Enum

class Equilibrium(str, Enum):
    """평형(면적) 구간을 나타내는 Enum – Java 버전 그대로 이식"""

    UNDER_5      = "UNDER_5"
    BETWEEN_6_10 = "BETWEEN_6_10"
    BETWEEN_11_15 = "BETWEEN_11_15"
    OVER_16      = "OVER_16"

    _DESCRIPTIONS = {
        UNDER_5: "5평 이하",
        BETWEEN_6_10: "6~10평",
        BETWEEN_11_15: "11~15평",
        OVER_16: "16평 이상",
    }

    @property
    def description(self) -> str:
        """Java enum.getDescription() 과 동일한 역할"""
        return self._DESCRIPTIONS[self]
