from enum import Enum

class Equilibrium(str, Enum):
    """
    평형(면적) 구간을 나타내는 Enum – Java 버전 그대로 이식
    """

    UNDER_5      = "UNDER_5"
    BETWEEN_6_10 = "BETWEEN_6_10"
    BETWEEN_11_15 = "BETWEEN_11_15"
    OVER_16      = "OVER_16"

    @property
    def description(self) -> str:
        descriptions = {
            "UNDER_5": "5-pyeong (≈ 16.53 m²)",
            "BETWEEN_6_10": "10-pyeong (≈ 33.06 m²)",
            "BETWEEN_11_15": "15-pyeong (≈ 49.59 m²)",
            "OVER_16": "20-pyeong (≈ 66.12 m²)",
        }
        return descriptions[self.value]
