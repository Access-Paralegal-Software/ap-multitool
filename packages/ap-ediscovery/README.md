# AP-eDiscovery

SQLite FTS5 local search appliance and BLAKE3 deduplication engine for AP-Suite.

## Features
- **BLAKE3 Content & Family Hashing**: Fast cryptographic deduplication of email families and documents.
- **SQLite FTS5 Local Search**: External content FTS5 table with unicode61 diacritic normalization and proximity searches (e.g. `NEAR(...)`).
- **Synchronized Triggers**: Automatic FTS indexing across inserts, updates, and deletes.
- **O(1) Tag Counters**: Pre-computed tag counts automatically maintained via SQLite database triggers.
