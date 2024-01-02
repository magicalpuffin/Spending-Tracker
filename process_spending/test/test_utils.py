import pandas as pd

from process_spending.test.config import (
    BA_EXAMPLE,
    BA_EXAMPLE_CLEAN,
    FIDELITY_EXAMPLE,
    FIDELITY_EXAMPLE_CLEAN,
)
from process_spending.utils import clean_ba, clean_fidelity


def test_clean_fidelity():
    target = pd.read_csv(FIDELITY_EXAMPLE_CLEAN, index_col="Id")
    value = clean_fidelity(FIDELITY_EXAMPLE)

    assert value.equals(target)


def test_clean_ba():
    target = pd.read_csv(BA_EXAMPLE_CLEAN, index_col="Id")
    value = clean_ba(BA_EXAMPLE)

    assert value.equals(target)
