# AP Multitool Consolidation Provenance

This record identifies the source tips absorbed by the
`refactor/ap-multitool-monorepo-consolidation` branch and their rewritten
equivalents in the monorepo.

| Member | Source default tip | Rewritten tip | Monorepo location |
|---|---|---|---|
| `ap-multitool` | `751b260febe8ff21741e133a62b007d24da744b0` | unchanged | repository root, with application code reorganized |
| `doc-chameleon` | `50b57167b7d98b28273341340aff3270d11ebd91` | `608eadc6ef0a8f8fb8ea786e413e4cb9d02ebde1` | `packages/doc-chameleon/` |
| `ap-multitool-portal` | `4a259cfb6c22b560949f159b54ca7c6455805a39` | `a9c7c0f3bbd8de32c79fb1fa626fb0821af34db1` | `web/portal/` |

The rewritten member tips were merged by
`87fcb1d43ebfb91e33f0745f68316d6c081304c8` and
`44ef6d39ab7a0c9fc22e89c1d27e5e70e4e4d3d4`. The initial workspace conversion
completed at `fb1c6a32b960bbb28204dc324e578b818afaa815`.

Portal history intentionally excludes generated `pages/`,
`Landing_Pages_Inventory.csv`, `sitemap.xml`, `squarespace_ab_tests/`, `blog/`,
and `faq/` paths before rewriting into `web/portal/`.

On 2026-08-29, the rewritten `doc-chameleon` and portal subtrees matched their
source tips exactly. Each standalone repository subsequently added only a
README deprecation banner (`23d1b14b4fb386cb713348da8d5ab795200a9287` and
`887cf7c002ae22d61899e628d2573288ff7dda6e`, respectively). Those lifecycle-only
deltas are intentionally not copied into the active monorepo packages.
