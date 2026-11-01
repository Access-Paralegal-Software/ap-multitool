"""
tests.test_production
Validates Concordance .DAT delimiters, UTF-8 BOM encoding, and Opticon .OPT tables.
"""

from pathlib import Path
from ap_ediscovery.engine.production import (
    generate_concordance_dat,
    generate_opticon_opt,
    DELIM_FIELD,
    QUAL_TEXT,
)

def test_concordance_dat_delimiters_and_bom():
    records = [
        {
            "DOCID": "ABC00000001",
            "BEGBATES": "ABC00000001",
            "ENDBATES": "ABC00000003",
            "BEGATTACH": "ABC00000001",
            "ENDATTACH": "ABC00000005",
            "PARENTDOC": "",
            "CUSTODIAN": "Doe, John",
            "ALL_CUSTODIANS": "Doe, John; Smith, Jane",
            "RECORD_TYPE": "Email",
            "FILE_NAME": "settlement_offer.eml",
            "FILE_EXT": "eml",
            "HASH_BLAKE3": "010203040506",
            "HASH_SHA256": "abcdef123456",
            "TEXT_PATH": r"TEXT\001\ABC00000001.txt",
            "NATIVE_PATH": r"NATIVES\001\ABC00000001.eml"
        }
    ]
    raw_dat = generate_concordance_dat(records)
    
    # 1. Assert UTF-8 BOM presence
    assert raw_dat.startswith(b"\xef\xbb\xbf")
    
    # 2. Assert Thorn qualifiers and Pilcrow column separators
    decoded = raw_dat[3:].decode("utf-8")
    lines = decoded.split("\r\n")
    assert len(lines) >= 3  # Header, Record, Empty trailing
    
    header = lines[0]
    data_row = lines[1]
    
    assert f"{QUAL_TEXT}DOCID{QUAL_TEXT}" in header
    assert DELIM_FIELD in header
    assert f"{QUAL_TEXT}ABC00000001{QUAL_TEXT}" in data_row
    assert f"{QUAL_TEXT}Doe, John; Smith, Jane{QUAL_TEXT}" in data_row

def test_opticon_opt_structure():
    opt_records = [
        {"IMAGE_ID": "ABC00000001", "VOLUME": "VOL001", "FILE_PATH": r"IMAGES\001\ABC00000001.TIF", "IS_DOC_BREAK": True, "PAGE_COUNT": 2},
        {"IMAGE_ID": "ABC00000002", "VOLUME": "VOL001", "FILE_PATH": r"IMAGES\001\ABC00000002.TIF", "IS_DOC_BREAK": False},
        {"IMAGE_ID": "ABC00000003", "VOLUME": "VOL001", "FILE_PATH": r"IMAGES\001\ABC00000003.TIF", "IS_DOC_BREAK": True, "PAGE_COUNT": 1},
    ]
    opt_text = generate_opticon_opt(opt_records)
    lines = [l for l in opt_text.split("\r\n") if l]
    
    assert len(lines) == 3
    assert lines[0] == r"ABC00000001,VOL001,IMAGES\001\ABC00000001.TIF,Y,,,2"
    assert lines[1] == r"ABC00000002,VOL001,IMAGES\001\ABC00000002.TIF,,,,"
    assert lines[2] == r"ABC00000003,VOL001,IMAGES\001\ABC00000003.TIF,Y,,,1"
