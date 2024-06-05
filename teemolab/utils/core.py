from typing import Optional


def safe_division(numerator, denominator) -> Optional[float]:
    """
    Safely divide two numbers, returning None if the denominator is zero.

    :param numerator: The numerator of the division.
    :param denominator: The denominator of the division.
    :return: The result of the division, or None if the denominator is zero.
    """
    try:
        return numerator / denominator
    except ZeroDivisionError:
        return None
