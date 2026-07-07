# Batch annotation — manual QA log

Random-sampled instances annotated with the finalized pipeline (3 samples +
aggregate). Each is QA'd by hand as it lands: a brief note if fine, a detailed
one if something is wrong. Outputs live under `annotations/swebench_pro/<id>/`
(gitignored during QA). Sampling seed: `20260706` (`round{1,2}_ids.txt`).

Legend: ✅ good · ⚠️ minor · ❌ problem.

## Round 1

_In progress. Rolling window of 4 concurrent pipelines (8-core / 16 GB box)._

| # | instance | lang | agg snippets | valid | note |
| --- | --- | --- | --- | --- | --- |
| 4 | protonmail/webclients `da91f08` | js | 5 | ✅ | on-target: all 4 gold-patch files + `dom.ts` helper; candidates 5/5/5 |
| 1 | internetarchive/openlibrary `25858f9` | python | 11 | ✅ | update_work/edition + retry helper + test; the "missed" `solr/utils.py` is a NEW file (correctly excluded — can't read what doesn't exist yet); cand 11/11/10 |
| 3 | qutebrowser `ff1c025` | python | 11 | ✅ | all 3 code gold files + tests; correctly drops changelog doc; cand 10/10/10 |
| 2 | future-architect/vuls `83bcca6` | go | 12 | ✅ | all 7 gold files + a test; cand 11/12/11 |
| 7 | internetarchive/openlibrary `c05ccf2` | python | 8 | ✅ | gold file + callers/helpers + tests; cand 8/8/8 |
| 6 | gravitational/teleport `1a77b79` | go | 4 | ✅ | gold file (3 focused ranges) + test; cand 4/4/4 |
| 5 | gravitational/teleport `e6d8629` | go | 8 | ✅ | all 4 gold files + access_checker context + test; cand 7/7/6 |
| 8 | future-architect/vuls `b8db2e0` | go | 11 | ✅ | all 9 gold files + test; similar-pattern impls tagged well; cand 10/10/11 |
| 9 | ansible/ansible `be59caa` | python | 5 | ✅ | iptables.py (3 ranges) + tests; correctly drops changelog fragment; cand 5/5/5 |
| 11 | internetarchive/openlibrary `6072570` | python | 4 | ⚠️ | core model method + account.py + test; missed 2 template files of 4 gold (UI layer); cand 3/4/4 |
| 10 | element-hq/element-web `33299af` | js | 13 | ✅ | all 3 gold files (incl. CSS) + RightPanelStore/hooks/test; cand 10/13/11 |
| 14 | ansible/ansible `de01db0` | python | 4 | ✅ | pip.py (3 ranges) + test; correctly drops changelog + porting-guide docs; cand 4/4/4 |
| 13 | ansible/ansible `502270c` | python | 5 | ✅ | hostname.py core + test + _utils; one broad 230-667 similar-pattern range (strategy classes; relevant but large); cand 5/8/4 |
| 15 | navidrome/navidrome `27875ba` | go | 8 | ✅ | consts/serve_index/config/embed + test; both "missed" gold files are NEW (loader + yaml), correctly excluded; cand 8/7/7 |
| 12 | ansible/ansible `b748ede` | python | 9 | ✅ | all 4 existing gold code files (galaxy/api, urls, uri, action/uri) + test; missed only changelog (NEW); cand 6/8/9 |
| 16 | flipt-io/flipt `7161f7b` | go | 5 | ✅ | both code gold files + tests; missed only go.work.sum (checksum/lock, correctly excluded); cand 5/5/5 |
| 17 | qutebrowser `bf045f7` | python | 5 | ✅ | gold file (webenginetab) + base class browsertab + debug + tests; no misses; cand 5/5/6 |
| 18 | element-hq/element-web `a692fe2` | js | 8 | ✅ | all 4 existing gold code files + test; missed only shouldForceDisableEncryption.ts (NEW); cand 10/7/9 |
| 19 | navidrome/navidrome `97434c1` | go | 10 | ✅ | all 8 gold code files + request + test; missed only new migration + go.mod/go.sum (deps, correctly excluded); cand 9/10/10 |
| 20 | navidrome/navidrome `6b3b4d8` | go | 3 | ✅ | both existing gold code files (walk_dir_tree revert + tag_scanner) + test; missed only utils/paths.go (NEW); cand 4/4/3 |

### Round 1 summary

20/20 valid & complete; **19 ✅ / 1 ⚠️ / 0 ❌**. Cost $34.62 (80 agent calls).

- The annotator reliably covers the **existing** gold-patch code files + relevant
  tests, and correctly excludes: files the patch *creates* (new files), docs
  (changelog / porting-guide / `.asciidoc`), and dependency manifests
  (`go.mod` / `go.sum` / `go.work.sum`). Candidates were very consistent.
- The one genuine gap (**#11**): two **existing** UI template files (`*.html`)
  the fix modifies were omitted, while core logic + tests were covered.
- **No severe problems.** Refinement for round 2: a prompt line to ensure every
  *existing* file the gold patch modifies is covered (not files it creates).
