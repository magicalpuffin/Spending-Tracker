import pandas as pd

from process_spending.test.config import FIDELITY_EXAMPLE, FIDELITY_EXAMPLE_CLEAN
from process_spending.utils import clean_fidelity_data


def test_clean_fidelity_data():
    target = pd.read_csv(FIDELITY_EXAMPLE_CLEAN, index_col="Id")
    value = clean_fidelity_data(pd.read_csv(FIDELITY_EXAMPLE))

    assert value.equals(target)
