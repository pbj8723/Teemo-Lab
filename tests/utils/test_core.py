import pytest

from teemolab.utils import core


def test_safe_division():

    assert core.safe_division(1, 2) == pytest.approx(0.5)
    assert core.safe_division(1, 0) == None
    assert core.safe_division(0, 1) == pytest.approx(0.0)
    assert core.safe_division(0, 0) == None
