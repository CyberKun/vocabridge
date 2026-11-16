import json

import pytest

from vocabridge.profiling import infer_type, profile_file, profile_records, read_records


@pytest.mark.parametrize(
    "values, expected",
    [
        (["1", "2", "-3"], "integer"),
        (["1.5", "2", "3e2"], "decimal"),
        (["yes", "No", "TRUE"], "boolean"),
        (["2024-01-01", "2023-12-31"], "date"),
        (["2024-13-01"], "string"),
        (["abc", "1"], "string"),
        (["", "  "], "string"),
        (["1", "", "2"], "integer"),
    ],
)
def test_infer_type(values, expected):
    assert infer_type(values) == expected


def test_profile_csv(suppliers_csv):
    profile = profile_file(suppliers_csv)
    assert profile.name == "suppliers"
    assert profile.row_count == 5
    sid = profile.field("supplier_id")
    assert sid.is_complete and sid.is_unique
    assert profile.field("registered_on").inferred_type == "date"
    assert profile.field("is_preferred").inferred_type == "boolean"
    notes = profile.field("notes")
    assert notes.missing_count == 2 and not notes.is_complete


def test_profile_json(tmp_path):
    path = tmp_path / "items.json"
    path.write_text(json.dumps([{"id": 1, "ok": True}, {"id": 2, "ok": None, "extra": "x"}]))
    records = read_records(path)
    assert records[0] == {"id": "1", "ok": "true"}
    profile = profile_records(records, source=str(path), name="items")
    assert [f.name for f in profile.fields] == ["id", "ok", "extra"]
    assert profile.field("ok").missing_count == 1
    assert profile.field("extra").missing_count == 1


def test_profile_round_trip(suppliers_csv):
    from vocabridge.profiling import DatasetProfile

    profile = profile_file(suppliers_csv)
    assert DatasetProfile.from_dict(profile.to_dict()) == profile


def test_unsupported_format(tmp_path):
    path = tmp_path / "data.xml"
    path.write_text("<x/>")
    with pytest.raises(ValueError):
        read_records(path)
