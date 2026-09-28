# Experimenter-Only Reference Cohorts

**Do not disclose to Sol until the blind Stage 2 conclusion is locked.**

The existing materialized comparator datasets inspected on 2026-07-21 are under:

`GPT 5-5/data/derived_cohorts/cohorts/`

| Dataset | Rows | Meaning | Manifest SHA-256 |
|---|---:|---|---|
| `apollo.tsv` | 29 | Apollo 7–17 | `bc2f605c7023e660a908a5cfb0962a125ea0ace7926c1d50d18170b05bea571e` |
| `core_nasa_non_apollo.tsv` | 44 | Core NASA non-Apollo | `c14b9abc1f5132c329d0e2743bb52d49954a2e62433cb5116f9006f45ed0443d` |
| `military_only.tsv` | 25 | X-15, Dyna-Soar, and MOL military rows | `eb7e349767155e4c475d96b4b0bc5e73160fa57d8a3377a351a79af5c16eb30b` |
| `other_all.tsv` | 69 | Union of core NASA and military comparators | `d8f70380dd3c6c04b12dc3217164a443bc5cfe8c3e8a9240fbb5a7d368c18ed5` |
| `other_available.tsv` | 55 | `other_all` excluding pre-1970 accidental deaths | `0607b4d2bb51ff02ef24b21ca866629b0017e4d56b7dd00360b4a8284a4f8612` |
| `other_pre1970_accidents.tsv` | 14 | the excluded accidental-death set | `006c38f5d821b5e864bffb6b45c165400841a954f64203883d3685e88565f6ed` |
| `all_astronauts.tsv` | 98 | Apollo plus `other_all` | `6fc4ebc78f561714196277aa854998cd94fde97fdcf7609a0cf23d20acd3fd7d` |

The values above were copied from `GPT 5-5/data/derived_cohorts/dataset_manifest.csv`; line counts were independently checked and equaled row count plus one header row.

Source-family components recorded by the same manifest:

- Apollo lunar: 24
- Apollo non-lunar: 5
- other core NASA: 44
- military X-15: 13
- military Dyna-Soar: 4
- military MOL: 8

## Post-lock copy rule

Do not point Sol at the parent path. After Stage 2 is locked, copy only the approved TSVs into `run/sol_001/stage3/reference/`, preserve filenames, and create a new SHA-256 manifest. Compare the new hashes with this table before sending the Stage 3 prompt.

If the source manifest changes before launch, record the change in `ACTION_LOG.md` and decide before freezing whether to update this snapshot.

