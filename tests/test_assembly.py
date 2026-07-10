"""Tests for make_assembly adapter selection and hub baseUri stamping."""

from jbrowse_anywidget import make_assembly
from jbrowse_anywidget import _stamp_base_uri


def _adapter(assembly):
    return assembly["sequence"]["adapter"]


def test_make_assembly_emits_flat_uri_shorthand():
    # the flat { name, uri } shorthand: no adapter type or sequence track is
    # chosen in Python; jbrowse-core expands it and infers the adapter from the
    # extension at load time (covered by the sequence plugin's guesser tests)
    a = make_assembly("volvox", "https://x.org/volvox.fa")
    assert a == {
        "name": "volvox",
        "aliases": [],
        "uri": "https://x.org/volvox.fa",
    }
    assert "sequence" not in a


def test_make_assembly_bgzipped_and_2bit_also_flat_uri():
    assert make_assembly("hg38", "https://x.org/hg38.fa.gz")["uri"] == (
        "https://x.org/hg38.fa.gz"
    )
    assert make_assembly("hg38", "https://x.org/hg38.2bit")["uri"] == (
        "https://x.org/hg38.2bit"
    )


def test_make_assembly_custom_index_widens_to_adapter_form():
    # a non-sibling index has no home in the flat shape, so it falls back to the
    # sequence.adapter form (the bare uri there still infers the adapter type)
    a = make_assembly(
        "hg38", "https://x.org/hg38.fa.gz", fai_uri="https://x.org/i.fai"
    )
    assert "uri" not in a
    assert _adapter(a) == {
        "uri": "https://x.org/hg38.fa.gz",
        "faiLocation": {"uri": "https://x.org/i.fai"},
    }


def test_make_assembly_refname_aliases_bare_uri_shorthand():
    a = make_assembly(
        "hg38",
        "https://x.org/hg38.fa.gz",
        refname_aliases_uri="https://x.org/aliases.txt",
    )
    assert a["refNameAliases"] == {"uri": "https://x.org/aliases.txt"}


def test_stamp_base_uri_fills_absent_base():
    config = {"adapter": {"uri": "seq.fa"}}
    _stamp_base_uri(config, "https://host/config.json")
    assert config["adapter"]["baseUri"] == "https://host/config.json"


def test_stamp_base_uri_replaces_explicit_null():
    # a node carrying baseUri=None must still be stamped; a bare `in` check would
    # wrongly skip it (the divergence stampBaseUri.ts guards against)
    config = {"adapter": {"uri": "seq.fa", "baseUri": None}}
    _stamp_base_uri(config, "https://host/config.json")
    assert config["adapter"]["baseUri"] == "https://host/config.json"


def test_stamp_base_uri_preserves_existing_base():
    config = {"adapter": {"uri": "seq.fa", "baseUri": "https://other/"}}
    _stamp_base_uri(config, "https://host/config.json")
    assert config["adapter"]["baseUri"] == "https://other/"
