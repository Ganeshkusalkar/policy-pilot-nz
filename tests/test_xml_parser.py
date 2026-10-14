
import pytest

from app.ingestion.xml_parser import parse_legislation


def test_parse_provision_and_nested_subprovision(tmp_path):
    xml = """<?xml version="1.0"?>
    <act>
      <prov id="section-1">
        <label>1</label>
        <heading>Short Title</heading>
        <prov.body>
          <text>This Act may be cited by its short title.</text>
          <subprov>
            <label-para>(1)</label-para>
            <para>It commences on the appointed date.</para>
          </subprov>
        </prov.body>
      </prov>
    </act>
    """

    path = tmp_path / "sample.xml"
    path.write_text(xml, encoding="utf-8")

    provisions = parse_legislation(path)

    assert len(provisions) == 1
    assert provisions[0]["label"] == "1"
    assert provisions[0]["heading"] == "Short Title"
    assert "This Act may be cited" in provisions[0]["text"]
    assert "appointed date" in provisions[0]["text"]
    assert "Short Title" not in provisions[0]["text"]


def test_parser_rejects_xml_without_provision_bodies(tmp_path):
    path = tmp_path / "empty.xml"
    path.write_text("<act><prov><label>1</label></prov></act>", encoding="utf-8")

    with pytest.raises(ValueError, match="prov.body"):
        parse_legislation(path)
