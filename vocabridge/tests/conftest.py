from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "procurement"


@pytest.fixture
def vocab_path() -> Path:
    return EXAMPLE / "ontology" / "procurement.ttl"


@pytest.fixture
def suppliers_csv() -> Path:
    return EXAMPLE / "data" / "suppliers.csv"


@pytest.fixture
def orders_csv() -> Path:
    return EXAMPLE / "data" / "purchase_orders.csv"
