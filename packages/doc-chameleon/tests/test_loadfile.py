from pathlib import Path
from doc_chameleon.bates.loadfile import (
    generate_concordance_dat,
    generate_opticon_opt,
    generate_production_manifest_csv,
    generate_production_loadfiles,
    CONCORDANCE_QUOTE,
    CONCORDANCE_DELIM,
)

def test_concordance_dat_generation(tmp_path: Path):
    docs = [
        {"doc_id": 1, "beg_bates": "ABC001", "end_bates": "ABC003", "page_count": 3, "file_name": "motion.pdf", "file_size": 1024},
        {"doc_id": 2, "beg_bates": "ABC004", "end_bates": "ABC004", "page_count": 1, "file_name": "exhibit.pdf", "file_size": 2048},
    ]
    dat_file = tmp_path / "VOL001.dat"
    generate_concordance_dat(docs, dat_file)

    content = dat_file.read_text(encoding="utf-8")
    assert CONCORDANCE_QUOTE in content
    assert CONCORDANCE_DELIM in content
    assert "ABC001" in content
    assert "ABC004" in content

def test_opticon_opt_generation(tmp_path: Path):
    docs = [
        {
            "dest_file": "doc1.pdf",
            "page_count": 2,
            "pages": [{"bates_id": "ABC001"}, {"bates_id": "ABC002"}]
        },
        {
            "dest_file": "doc2.pdf",
            "page_count": 1,
            "pages": [{"bates_id": "ABC003"}]
        }
    ]
    opt_file = tmp_path / "VOL001.opt"
    generate_opticon_opt(docs, opt_file, volume="VOL001")

    lines = opt_file.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 3
    # Check first page of doc1 has boundary 'Y' and page count 2
    assert "ABC001,VOL001,IMAGES\\doc1.pdf,Y,,,2" in lines[0]
    # Check second page has no break and no page count
    assert "ABC002,VOL001,IMAGES\\doc1.pdf,,,," in lines[1]
    # Check doc2 has boundary 'Y' and count 1
    assert "ABC003,VOL001,IMAGES\\doc2.pdf,Y,,,1" in lines[2]

def test_generate_production_loadfiles_creates_all(tmp_path: Path):
    docs = [
        {
            "doc_id": 1,
            "beg_bates": "ABC001",
            "end_bates": "ABC002",
            "dest_file": "doc1.pdf",
            "file_name": "doc1.pdf",
            "page_count": 2,
            "file_size": 500,
            "pages": [{"bates_id": "ABC001"}, {"bates_id": "ABC002"}]
        }
    ]
    res = generate_production_loadfiles(docs, tmp_path, volume="PROD01")
    assert res["dat"].exists()
    assert res["opt"].exists()
    assert res["csv"].exists()
