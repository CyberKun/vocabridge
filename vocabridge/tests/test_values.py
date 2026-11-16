import json
import shutil

import pytest

from vocabridge.cli import main
from vocabridge.hypotheses import IRI, MappingSet
from vocabridge.values import containment, detect_pattern, load_linked

P = "https://example.org/vocabridge/procurement#"


@pytest.mark.parametrize(
    "values, expected",
    [
        (["GB", "NL", "IN"], "upper-code-2"),
        (["GBP", "EUR", ""], "upper-code-3"),
        (["a@x.org", "b@y.com"], "email"),
        (["https://a.org/x", "http://b.org"], "url"),
        (["PO-24-0001", "PO-24-0002"], "prefixed-identifier"),
        (["Northwind Ltd", "Blue Harbor"], None),
        (["GB"], None),  # too few values to judge
    ],
)
def test_detect_pattern(values, expected):
    assert detect_pattern(values) == expected


@pytest.fixture
def workspace(tmp_path, suppliers_csv, orders_csv, vocab_path):
    """Reviewed suppliers and orders mappings, ready to be linked to."""
    data = tmp_path / "data"
    data.mkdir()
    for src in (suppliers_csv, orders_csv, suppliers_csv.parent / "invoices.csv"):
        shutil.copy(src, data / src.name)
    out = tmp_path / "out"
    out.mkdir()
    for name in ("suppliers", "purchase_orders"):
        mapping = out / f"{name}.mapping.json"
        assert main(["suggest", str(data / f"{name}.csv"), "--vocab", str(vocab_path),
                     "--base-iri", "https://ex.org/", "-o", str(mapping)]) == 0
        assert main(["review", str(mapping), "--accept", "__subject__",
                     "--report", str(tmp_path / "r.md")]) == 0
    return tmp_path


def test_load_linked_requires_accepted_subject(tmp_path, suppliers_csv, vocab_path):
    mapping = tmp_path / "m.json"
    main(["suggest", str(suppliers_csv), "--vocab", str(vocab_path),
          "--base-iri", "https://ex.org/", "-o", str(mapping)])
    with pytest.raises(ValueError):
        load_linked(mapping)


def test_containment(workspace):
    link = load_linked(workspace / "out" / "suppliers.mapping.json")
    assert link.class_iri == P + "Supplier" and link.id_field == "supplier_id"
    assert containment(["S-1001", "S-1002", "S-1001", ""], link) == (1.0, 2, 2)
    assert containment(["S-1001", "X-1"], link)[0] == 0.5
    assert containment([], link) == (0.0, 0, 0)


def test_values_link_fields_that_names_cannot(workspace, vocab_path):
    invoices = workspace / "data" / "invoices.csv"
    out = workspace / "out"

    plain = out / "plain.json"
    main(["suggest", str(invoices), "--vocab", str(vocab_path), "--base-iri",
          "https://ex.org/", "-o", str(plain)])
    assert MappingSet.load(plain).hypothesis("payee_ref").term is None

    linked = out / "linked.json"
    assert main(["suggest", str(invoices), "--vocab", str(vocab_path), "--base-iri",
                 "https://ex.org/", "-o", str(linked),
                 "--link", str(out / "suppliers.mapping.json"),
                 "--link", str(out / "purchase_orders.mapping.json")]) == 0
    mapping = MappingSet.load(linked)

    payee = mapping.hypothesis("payee_ref")
    assert payee.term == P + "billedBy"
    assert payee.value_kind == IRI and payee.target_class == P + "Supplier"
    overlap = [e for e in payee.evidence if e.kind == "value-overlap"]
    assert overlap and overlap[0].weight > 0 and "100%" in overlap[0].detail

    order = mapping.hypothesis("po_ref")
    assert order.term == P + "billsOrder" and order.target_class == P + "PurchaseOrder"

    # Pattern evidence shows up on literal fields too.
    currency = mapping.hypothesis("currency")
    assert any(e.kind == "value-pattern" for e in currency.evidence)


def test_disjoint_values_count_against(workspace, vocab_path, tmp_path):
    bad = tmp_path / "data" / "bad_invoices.csv"
    bad.write_text("invoice_number,payee_ref\nI-1,Z-9\nI-2,Z-8\n")
    out = tmp_path / "out" / "bad.json"
    main(["suggest", str(bad), "--vocab", str(vocab_path), "--base-iri", "https://ex.org/",
          "-o", str(out), "--link", str(tmp_path / "out" / "suppliers.mapping.json")])
    data = json.loads(out.read_text())
    payee = next(f for f in data["fields"] if f["field"] == "payee_ref")
    assert payee["term"] is None


def test_link_to_unreviewed_mapping_is_an_error(tmp_path, suppliers_csv, vocab_path):
    mapping = tmp_path / "m.json"
    main(["suggest", str(suppliers_csv), "--vocab", str(vocab_path),
          "--base-iri", "https://ex.org/", "-o", str(mapping)])
    assert main(["suggest", str(suppliers_csv), "--vocab", str(vocab_path),
                 "--base-iri", "https://ex.org/", "-o", str(tmp_path / "x.json"),
                 "--link", str(mapping)]) == 2
