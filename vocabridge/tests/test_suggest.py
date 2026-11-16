import pytest

from vocabridge.hypotheses import IRI, PROPOSED
from vocabridge.profiling import profile_file
from vocabridge.suggest import choose_id_field, suggest_mappings
from vocabridge.vocab import load_vocabulary

P = "https://example.org/vocabridge/procurement#"


@pytest.fixture
def terms(vocab_path):
    return load_vocabulary(vocab_path)


def test_suppliers(suppliers_csv, terms):
    mapping = suggest_mappings(profile_file(suppliers_csv), terms, "https://ex.org/d")
    assert mapping.base_iri == "https://ex.org/d/"
    assert mapping.subject.term == P + "Supplier"
    assert mapping.id_field == "supplier_id"
    got = {h.field: h.term for h in mapping.fields}
    assert got["supplier_id"] == P + "supplierId"
    assert got["name"] == P + "supplierName"  # matched with class context
    assert got["registered_on"] == P + "registrationDate"  # matched via skos:altLabel
    assert got["is_preferred"] == P + "preferredSupplier"
    assert got["notes"] is None  # no shared word: no guess
    assert all(h.status == PROPOSED for h in mapping.all())


def test_purchase_orders_reference(orders_csv, terms):
    mapping = suggest_mappings(profile_file(orders_csv), terms, "https://ex.org/d/")
    assert mapping.subject.term == P + "PurchaseOrder"
    vendor = mapping.hypothesis("vendor_id")
    # "vendor_id" and "supplier" share no characters worth trusting; the altLabel "vendor"
    # on orderedFrom is what links them, and the value becomes a reference (IRI).
    assert vendor.term == P + "orderedFrom"
    assert vendor.value_kind == IRI
    assert vendor.target_class == P + "Supplier"
    assert any(e.kind == "alt-label-match" for e in vendor.evidence)
    assert mapping.hypothesis("approved_by").term is None


def test_every_suggestion_explains_itself(orders_csv, terms):
    mapping = suggest_mappings(profile_file(orders_csv), terms, "https://ex.org/d/")
    for h in mapping.all():
        assert h.evidence, f"{h.field} has no evidence"
        assert 0.0 <= h.confidence <= 1.0
        assert h.method == "lexical-baseline"


def test_range_mismatch_lowers_confidence(tmp_path, terms):
    from vocabridge.profiling import profile_records

    good = profile_records([{"order_date": "2024-01-01"}], "x", "purchase_orders")
    bad = profile_records([{"order_date": "next tuesday"}], "x", "purchase_orders")
    g = suggest_mappings(good, terms, "https://ex.org/").hypothesis("order_date")
    b = suggest_mappings(bad, terms, "https://ex.org/").hypothesis("order_date")
    assert b.confidence < g.confidence
    assert any(e.kind == "range" and e.weight < 0 for e in b.evidence)


def test_choose_id_field_falls_back_to_unique_field():
    from vocabridge.profiling import profile_records

    profile = profile_records([{"email": "a@x", "team": "red"}, {"email": "b@x", "team": "red"}],
                              "x", "people")
    assert choose_id_field(profile) == "email"


def test_no_vocabulary_is_an_error(suppliers_csv):
    with pytest.raises(ValueError):
        suggest_mappings(profile_file(suppliers_csv), [], "https://ex.org/")
