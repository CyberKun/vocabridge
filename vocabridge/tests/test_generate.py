import pytest
from rdflib import RDF, Literal, URIRef

from vocabridge.generate import (
    MappingNotReadyError,
    build_graph,
    build_shapes,
    generate_rdf,
    resource_iri,
    validate,
)
from vocabridge.hypotheses import ACCEPTED
from vocabridge.profiling import profile_file, read_records
from vocabridge.suggest import suggest_mappings
from vocabridge.vocab import load_vocabulary

P = "https://example.org/vocabridge/procurement#"
XSD_DATE = URIRef("http://www.w3.org/2001/XMLSchema#date")


def accepted_mapping(csv_path, vocab_path, threshold=0.75):
    mapping = suggest_mappings(profile_file(csv_path), load_vocabulary(vocab_path),
                               "https://ex.org/")
    for h in mapping.all():
        if h.term and h.confidence >= threshold:
            h.set_status(ACCEPTED, "tester")
    return mapping


def test_nothing_generated_before_review(suppliers_csv, vocab_path):
    mapping = suggest_mappings(profile_file(suppliers_csv), load_vocabulary(vocab_path),
                               "https://ex.org/")
    with pytest.raises(MappingNotReadyError):
        build_graph(mapping, read_records(suppliers_csv))


def test_only_accepted_fields_are_written(suppliers_csv, vocab_path):
    mapping = accepted_mapping(suppliers_csv, vocab_path, threshold=0.9)  # country stays proposed
    graph = build_graph(mapping, read_records(suppliers_csv), provenance=False)
    s = URIRef("https://ex.org/supplier/S-1001")
    assert (s, RDF.type, URIRef(P + "Supplier")) in graph
    assert (s, URIRef(P + "preferredSupplier"), Literal(True)) in graph
    assert (s, URIRef(P + "registrationDate"), Literal("2021-03-15", datatype=XSD_DATE)) in graph
    assert not list(graph.triples((None, URIRef(P + "countryCode"), None)))


def test_references_line_up_across_datasets(orders_csv, vocab_path):
    mapping = accepted_mapping(orders_csv, vocab_path)
    graph = build_graph(mapping, read_records(orders_csv), provenance=False)
    order = URIRef("https://ex.org/purchaseorder/PO-24-0001")
    assert (order, URIRef(P + "orderedFrom"), URIRef("https://ex.org/supplier/S-1001")) in graph


def test_generated_data_conforms_to_generated_shapes(orders_csv, vocab_path):
    mapping = accepted_mapping(orders_csv, vocab_path)
    data = build_graph(mapping, read_records(orders_csv))
    shapes = build_shapes(mapping, profile_file(orders_csv))
    result = validate(data, shapes)
    assert result.conforms, result.report_text


def test_shapes_catch_bad_data(orders_csv, vocab_path):
    mapping = accepted_mapping(orders_csv, vocab_path)
    shapes = build_shapes(mapping, profile_file(orders_csv))
    records = read_records(orders_csv)
    records[0]["total_amount"] = "twelve thousand"  # wrong datatype
    records[1]["order_date"] = ""  # required value missing
    result = validate(build_graph(mapping, records), shapes)
    assert not result.conforms
    assert "totalAmount" in result.report_text
    assert "orderDate" in result.report_text


def test_generate_rdf_resolves_dataset_relative_to_mapping(tmp_path, suppliers_csv, vocab_path):
    import shutil

    (tmp_path / "data").mkdir()
    (tmp_path / "out").mkdir()
    shutil.copy(suppliers_csv, tmp_path / "data" / "suppliers.csv")
    mapping = accepted_mapping(tmp_path / "data" / "suppliers.csv", vocab_path)
    mapping.dataset = "../data/suppliers.csv"
    mapping_file = tmp_path / "out" / "m.json"
    mapping.save(mapping_file)
    assert len(generate_rdf(mapping, mapping_file, provenance=False)) > 0


def test_resource_iri_is_escaped():
    iri = resource_iri("https://ex.org/", P + "PurchaseOrder", "A 1/2")
    assert str(iri) == "https://ex.org/purchaseorder/A%201%2F2"
