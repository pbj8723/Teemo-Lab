from typing import Optional


def safe_division(numerator, denominator) -> Optional[float]:
    try:
        return numerator / denominator
    except ZeroDivisionError:
        return None
