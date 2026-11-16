from vocabridge.text import local_name, tokens
from vocabridge.vocab import CLASS, DATATYPE_PROPERTY, OBJECT_PROPERTY, load_vocabulary


def test_tokens():
    assert tokens("supplier_id") == ["supplier", "id"]
    assert tokens("supplierName") == ["supplier", "name"]
    assert tokens("PO-Number") == ["po", "number"]
    assert tokens("purchase_orders") == ["purchase", "order"]
    assert tokens("status") == ["status"]
    assert tokens("approved_by") == ["approved"]


def test_local_name():
    assert local_name("https://ex.org/v#Thing") == "Thing"
    assert local_name("https://ex.org/v/thing") == "thing"


def test_load_vocabulary(vocab_path):
    terms = {t.iri.split("#")[1]: t for t in load_vocabulary(vocab_path)}
    assert terms["Supplier"].kind == CLASS
    assert "Vendor" in terms["Supplier"].alt_labels
    assert terms["supplierName"].kind == DATATYPE_PROPERTY
    ordered_from = terms["orderedFrom"]
    assert ordered_from.kind == OBJECT_PROPERTY
    assert ordered_from.ranges == ["https://example.org/vocabridge/procurement#Supplier"]
    assert terms["registrationDate"].range_is_datatype


def test_rdf_property_kind_inferred_from_range(tmp_path):
    path = tmp_path / "v.ttl"
    path.write_text(
        "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n"
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n"
        "<http://ex.org/age> a rdf:Property ; rdfs:range xsd:integer .\n"
        "<http://ex.org/knows> a rdf:Property ; rdfs:range <http://ex.org/Person> .\n"
        "<http://ex.org/note> a rdf:Property .\n"
    )
    kinds = {t.iri: t.kind for t in load_vocabulary(path)}
    assert kinds["http://ex.org/age"] == DATATYPE_PROPERTY
    assert kinds["http://ex.org/knows"] == OBJECT_PROPERTY
    assert kinds["http://ex.org/note"] == "property"
