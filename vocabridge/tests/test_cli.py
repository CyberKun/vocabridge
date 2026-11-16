import json
import shutil

from vocabridge.cli import keywords_for, main
from vocabridge.profiling import profile_file


def test_end_to_end(tmp_path, suppliers_csv, vocab_path, capsys):
    data = tmp_path / "suppliers.csv"
    shutil.copy(suppliers_csv, data)
    mapping = tmp_path / "out" / "mapping.json"
    mapping.parent.mkdir()

    assert main(["suggest", str(data), "--vocab", str(vocab_path),
                 "--base-iri", "https://ex.org/", "-o", str(mapping)]) == 0
    assert json.loads(mapping.read_text())["dataset"] == "../suppliers.csv"

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
