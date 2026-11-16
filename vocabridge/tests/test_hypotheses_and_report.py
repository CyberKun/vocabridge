import pytest

from vocabridge.hypotheses import ACCEPTED, REJECTED, MappingSet
from vocabridge.profiling import profile_file
from vocabridge.report import render_report
from vocabridge.suggest import suggest_mappings
from vocabridge.vocab import load_vocabulary


@pytest.fixture
def mapping(suppliers_csv, vocab_path):
    return suggest_mappings(profile_file(suppliers_csv), load_vocabulary(vocab_path),
                            "https://ex.org/")


def test_round_trip(mapping, tmp_path):
    mapping.hypothesis("name").set_status(ACCEPTED, "tester", "looks right")
    path = tmp_path / "m.json"
    mapping.save(path)
    loaded = MappingSet.load(path)
    assert loaded == mapping
    assert loaded.hypothesis("name").review.reviewer == "tester"


def test_cannot_accept_without_term(mapping):
    with pytest.raises(ValueError):
        mapping.hypothesis("notes").set_status(ACCEPTED)
    mapping.hypothesis("notes").set_status(REJECTED)  # rejecting is always allowed


def test_unknown_status_and_field(mapping):
    with pytest.raises(ValueError):
        mapping.hypothesis("name").set_status("maybe")
    with pytest.raises(KeyError):
        mapping.hypothesis("nope")


def test_future_format_rejected(mapping):
    data = mapping.to_dict()
    data["format_version"] = 99
    with pytest.raises(ValueError):
        MappingSet.from_dict(data)


def test_report(mapping):
    mapping.hypothesis("country").set_status(ACCEPTED, "tester", "ISO codes")
    text = render_report(mapping)
    assert "1 accepted, 0 rejected, 6 awaiting review" in text
    assert "Decision: accepted by tester" in text
    assert "`notes` | _no suggestion_" in text
