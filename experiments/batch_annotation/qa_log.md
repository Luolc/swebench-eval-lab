# Batch annotation — manual QA log

Random-sampled instances annotated with the finalized pipeline (3 samples +
aggregate). Each is QA'd by hand as it lands: a brief note if fine, a detailed
one if something is wrong. Outputs live under `annotations/swebench_pro/<id>/`
(committed as the deliverable). Sampling seed: `20260706`
(`round{1,2,3}_ids.txt`).

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

## Round 2

_Tuned prompt (coverage line). Lighter QA: valid + gold-code coverage per example._

| # | instance | lang | agg snippets | valid | existing-gold covered | note |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | flipt-io/flipt `1737085` | go | 8 | ✅ | 2/2 | cand 6/7/9 |
| 4 | future-architect/vuls `dc49646` | go | 8 | ✅ | 4/4 | cand 6/6/7 |
| 2 | future-architect/vuls `73f0ada` | go | 12 | ✅ | 4/4 | cand 11/13/12 |
| 5 | element-hq/element-web `72a8f8f` | js | 5 | ✅ | 2/2 | cand 5/5/5 |
| 3 | protonmail/webclients `7e54526` | js | 19 | ✅ | 11/11 | cand 18/17/14 |
| 8 | qutebrowser `1af602b` | python | 6 | ✅ | 1/1 code (only miss = changelog.asciidoc doc, correctly excluded) | cand 6/6/4 |
| 6 | internetarchive/openlibrary `b67138b` | python | 17 | ⚠️ | 5/6 existing code; missed parse_xml.py (MARC parser, relevant) | cand 15/15/16 |
| 7 | qutebrowser `e5340c4` | python | 11 | ✅ | 7/7 | cand 9/9/11 |
| 11 | flipt-io/flipt `381b90f` | go | 9 | ✅ | 7/7 | cand 9/9/9 |
| 9 | future-architect/vuls `f0b3a8b` | go | 6 | ✅ | 4/4 code (only miss = go.mod/go.sum deps) | cand 7/5/8 |
| 10 | qutebrowser `5e0d6dc` | python | 7 | ✅ | 3/3 | cand 7/7/7 |
| 14 | NodeBB/NodeBB `da0211b` | js | 5 | ✅ | 2/2 | cand 5/4/4 |
| 15 | qutebrowser `8d05f02` | python | 11 | ✅ (recovered) | one sample ended without writing output (MissingOutputError) → whole pipeline died. Root cause: error raised after the retry loop. Fixed (retry no-output samples + pipeline tolerates a failed sample); re-run succeeded, cand 11/10/11. |
| 13 | ansible/ansible `42355d1` | python | 16 | ✅ (recovered) | pre-fix no-output failure; re-run with the fix succeeded, 3 candidates 13/13/15, existing-gold 5/5 |
| 12 | ansible/ansible `d58e69c` | python | 15 | ✅ | 3/3 | cand 14/16/16 |
| 16 | future-architect/vuls `fd18df1` | go | 8 | ✅ | 3/3 code (only miss = go.mod/go.sum) | cand 8/10/10 |
| 18 | internetarchive/openlibrary `77c16d5` | python | 8 | ✅ | 7/7 | cand 8/8/8 |
| 17 | gravitational/teleport `4d0117b` | go | 17 | ✅ | 3/3 | cand 17/17/18 |
| 19 | tutao/tutanota `1ff82aa` | ts | 9 | ✅ | 3/3 | cand 10/10/9 |
| 20 | internetarchive/openlibrary `62d2243` | python | 11 | ✅ | 2/2 | cand 11/7/7 |

### Round 2 summary

20/20 valid & complete; **19 ✅ / 1 ⚠️ / 0 ❌** (both no-output failures recovered
after the robustness fix). The tuned prompt (existing-file coverage line) held up.

- **Coverage.** Every *existing* gold-patch code file is covered except one
  (below). A whole-repo self-check of all aggregates on disk found the only
  "missed" files to be legitimately-excluded non-code: docs (`.rst`
  porting-guide, `.asciidoc` changelogs), dependency lockfiles (`go.mod` /
  `go.sum` / `go.work.sum`), and **generated** protobuf (`*.pb.go`). None are
  readable source a solver would open.
- **The one genuine gap (#6):** `openlibrary/catalog/marc/parse_xml.py` (a MARC
  parser the fix touches) was omitted by all three candidates despite the
  coverage line — a single-file miss on one instance, core logic + tests still
  covered. Minor, not severe.
- **Robustness validated in the field.** Two samples (#13, #15) hit the flaky
  MissingOutputError; the fix (`df22a2f` — retry no-output samples + aggregate
  the survivors) recovered both on re-run, with no pipeline deaths afterward.
- **No severe problems.** Proceeding to round 3 (41–60) with the same setup.
