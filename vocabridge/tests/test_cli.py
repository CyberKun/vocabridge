import csv
import json

import pytest

from vocabridge.cli import keywords_for, main
from vocabridge.profiling import profile_file


@pytest.mark.parametrize("suffix,delimiter,override", [
    (".csv", ",", []), (".csv", ";", []), (".tsv", "\t", []),
    (".csv", "|", []), (".csv", ":", ["--delimiter", ":"]),
])
def test_end_to_end(tmp_path, suppliers_csv, vocab_path, capsys, suffix, delimiter, override):
    data = tmp_path / ("suppliers" + suffix)
    with suppliers_csv.open(newline="", encoding="utf-8") as source:
        rows = list(csv.reader(source))
    with data.open("w", newline="", encoding="utf-8") as target:
        csv.writer(target, delimiter=delimiter).writerows(rows)
    mapping = tmp_path / "out" / "mapping.json"
    mapping.parent.mkdir()

    assert main(["suggest", str(data), "--vocab", str(vocab_path),
                 "--base-iri", "https://ex.org/", "-o", str(mapping), *override]) == 0
    from pathlib import Path
    payload = json.loads(mapping.read_text())
    assert Path(payload["dataset"]).as_posix() == "../suppliers" + suffix
    assert payload["delimiter"] == delimiter

    # Generating before review must fail clearly.
    assert main(["generate", str(mapping), "-o", str(tmp_path / "x.ttl")]) == 2

    assert main(["review", str(mapping), "--accept-above", "0.9", "--reviewer", "t"]) == 0
    assert main(["review", str(mapping), "--accept", "country", "--reject", "notes",
                 "--reviewer", "t", "--report", str(tmp_path / "r.md")]) == 0
    assert "0 awaiting review" in (tmp_path / "r.md").read_text()

    out = tmp_path / "data.ttl"
    shapes = tmp_path / "shapes.ttl"
    assert main(["generate", str(mapping), "-o", str(out), "--shapes", str(shapes)]) == 0
    assert main(["validate", str(out), str(shapes)]) == 0


def test_review_unknown_field(tmp_path, suppliers_csv, vocab_path):
    mapping = tmp_path / "m.json"
    main(["suggest", str(suppliers_csv), "--vocab", str(vocab_path),
          "--base-iri", "https://ex.org/", "-o", str(mapping)])
    assert main(["review", str(mapping), "--accept", "does_not_exist"]) == 2


def test_profile_command(suppliers_csv, tmp_path):
    out = tmp_path / "p.json"
    assert main(["profile", str(suppliers_csv), "-o", str(out)]) == 0
    assert json.loads(out.read_text())["row_count"] == 5


def test_keywords_skip_generic_words(orders_csv):
    words = keywords_for(profile_file(orders_csv), ["procurement"])
    assert words[0] == "procurement"
    assert "purchase order" in words
    assert "vendor" in words and "currency" in words
    assert "id" not in words and "date" not in words


@pytest.mark.parametrize("command", ["profile", "suggest", "discover"])
def test_delimiter_option(command):
    from vocabridge.cli import build_parser
    arguments = [command, "data.csv", "--delimiter", ";"]
    if command == "suggest":
        arguments += ["--vocab", "v.ttl", "--base-iri", "https://ex.org/", "-o", "m.json"]
    assert build_parser().parse_args(arguments).delimiter == ";"
    with pytest.raises(SystemExit):
        build_parser().parse_args([*arguments, "--delimiter", "too long"])


def test_legacy_mapping_keeps_comma_delimiter(tmp_path, suppliers_csv, vocab_path):
    from vocabridge.generate import generate_rdf
    from vocabridge.hypotheses import MappingSet
    from vocabridge.suggest import suggest_mappings
    from vocabridge.vocab import load_vocabulary

    mapping = suggest_mappings(profile_file(suppliers_csv), load_vocabulary(vocab_path),
                               "https://ex.org/")
    for hypothesis in mapping.all():
        hypothesis.set_status("accepted" if hypothesis.term else "rejected")
    payload = mapping.to_dict()
    payload.pop("delimiter")
    restored = MappingSet.from_dict(payload)
    assert restored.delimiter == ","
    assert len(generate_rdf(restored, tmp_path / "mapping.json")) > 0
