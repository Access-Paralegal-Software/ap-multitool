"""AP-eDiscovery local search appliance and BLAKE3 deduplication engine.

Maintainer: Strictly Alan Woodyard.
"""

from ap_ediscovery.engine import (
    CONCORDANCE_STANDARD_FIELDS,
    DELIM_FIELD,
    DELIMITER_COLUMN,
    DELIMITER_MULTI,
    DELIMITER_QUALIFIER,
    DELIMITER_QUOTE,
    OpticonDocument,
    OpticonEntry,
    ProductionRecord,
    QUAL_TEXT,
    STANDARD_FIELDS,
    UTF8_BOM_BYTES,
    build_opticon_for_documents,
    build_opticon_from_document_tuples,
    escape_dat_value,
    format_dat_field,
    format_opticon_line,
    generate_concordance_dat,
    generate_concordance_dat_bytes,
    generate_opticon_opt,
    generate_opticon_opt_bytes,
    parse_concordance_dat,
    parse_concordance_line,
    parse_opticon_opt,
    unescape_dat_value,
)

__version__ = "0.1.0"
__maintainer__ = "Alan Woodyard"
__author__ = "Alan Woodyard"

__all__ = [
    "CONCORDANCE_STANDARD_FIELDS",
    "DELIM_FIELD",
    "DELIMITER_COLUMN",
    "DELIMITER_MULTI",
    "DELIMITER_QUALIFIER",
    "DELIMITER_QUOTE",
    "OpticonDocument",
    "OpticonEntry",
    "ProductionRecord",
    "QUAL_TEXT",
    "STANDARD_FIELDS",
    "UTF8_BOM_BYTES",
    "build_opticon_for_documents",
    "build_opticon_from_document_tuples",
    "escape_dat_value",
    "format_dat_field",
    "format_opticon_line",
    "generate_concordance_dat",
    "generate_concordance_dat_bytes",
    "generate_opticon_opt",
    "generate_opticon_opt_bytes",
    "parse_concordance_dat",
    "parse_concordance_line",
    "parse_opticon_opt",
    "unescape_dat_value",
]
