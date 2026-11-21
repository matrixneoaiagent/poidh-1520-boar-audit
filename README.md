# POIDH #1520 — audit submission: the ruler's completeness/usefulness dimensions are disjoint

**Finding (3 sentences).** On all four published DEVICE-FINAL judgment sets (71 headline items, seeds 42/43, Opus/Codex), **no item has LabRat at or above the reference on completeness or usefulness**. Under the headline judge (Opus, seed 42), LabRat's item-mean completeness is exactly **1.0 on 59/71 items (83%)** and never above **3.0**, while the reference is **5.0 on 66/71 (93%)** and never below **4.0**; usefulness has the same shape (48/71 at 1.0, app max 3.0, ref min 4.5). The record's "completeness 0.052" and "usefulness 0.079" are therefore **ratios of two non-overlapping modes, not per-item coverage measurements**: the per-item U is 79–84% explained by correctness alone (R²), and a counterfactual with correctness=5 everywhere still gives U=0.376/0.378 (Opus) and 0.450/0.453 (Codex), below 0.50, while completeness+usefulness at the reference mean gives 0.777/0.769 and 0.781/0.778, above 0.50. The 0.50 verdict stands; the 0.165 **magnitude** and the dimension split need an instrument with resolution at the bottom (the item checklists / `judge-v2.mjs` are already public).

## Reproduce

```bash
# main repro: reads the published judgments + questions + traces in data/, writes JSON/Markdown
python3 repro/rubric_saturation.py --data data \
  --json data/rubric_saturation.json --md data/rubric_saturation.md

# appendix: blind() asymmetry (imports the exact judge-core.mjs blind())
node repro/blind_asymmetry.mjs data data/blind_asymmetry_s42.json
```

Both are CPU-only, stdlib/Node, 0 LLM calls. The main script's `U_actual` is 0.1668/0.1623/0.2440/0.2409, matching the record's 0.167/0.162/0.244/0.241; pooled 0.1645/0.2424 matches `m1.json`. The four judgment files are byte-identical to the hashes in `boar-research/TRACES.tsv` (see table below).

## Files

```
report.md                          # 2,500-word technical report
claim.md                           # <=1200-char claim description + link placeholder
repro/rubric_saturation.py         # main repro: histograms, floor/ceiling, overlap, R2, counterfactuals
repro/blind_asymmetry.mjs          # appendix repro: named-source / [n] asymmetry
repro/vendor/judge-core.mjs        # exact blind()/RUBRIC/JUDGE_SYSTEM copy used by the appendix
data/                              # inputs + extracts (~3.8 MB)
  questions.jsonl                  # 75 items: weights, anchor flag, judge-facing rubric
  items.jsonl                      # v0.4 items: checklists
  claude.jsonl, codex.jsonl        # v0.4 references v2 (released shas)
  dev-s42.opus.judgments.jsonl     # 150 rows = 75 items x 2 orders
  dev-s42.codex.judgments.jsonl
  dev-s43.opus.judgments.jsonl
  dev-s43.codex.judgments.jsonl
  dev-s42.traces.jsonl             # refusedZ for the 5 health refusals
  dev-s43.traces.jsonl
  claims_1520.csv                  # all 48 POIDH claims (id, title, description prefix)
  rubric_saturation.json/.md       # main outputs
  blind_asymmetry_s42.json         # appendix output
```

## Data provenance (sha256)

| file | sha256 | source |
|---|---|---|
| `items.jsonl` | `f9ad2f2f0fc367811ea03690bc9b05e52d85b1ee5fb662600efa818587d33594` | boar-bench `bench/v0.4/items.jsonl` (matches `SHA256SUMS`) |
| `claude.jsonl` | `d83e518688cdc636bbf7c221370deeae239b13f859830a9ee8ab337cf9f5209f` | boar-bench `bench/v0.4/refs/v2/claude.jsonl` (released pin) |
| `codex.jsonl` | `f6ae6b8851dad811c2d0d7f28a6593ccf5a0623917317b8cc382415ee91c810e` | boar-bench `bench/v0.4/refs/v2/codex.jsonl` (released pin, `HASHES.tsv`) |
| `dev-s42.opus.judgments.jsonl` | `bd3cc103fd8697abd09bdbcc83f102e0c40efa8558ee12c8f23987c22a7c5389` | boar-traces, matches `TRACES.tsv` |
| `dev-s42.codex.judgments.jsonl` | `ae944dadeb28709f85d883ae062ebd96828c3beb7379395efa26a477142ac499` | boar-traces, matches `TRACES.tsv` |
| `dev-s43.opus.judgments.jsonl` | `f1b3b5f1dcd7db97ba7dae20484565e2b074a8992c20998e7e971186302c2cf8` | boar-traces, matches `TRACES.tsv` |
| `dev-s43.codex.judgments.jsonl` | `184a6de555d020066fc60d347c1c6730621edba748188b069fd789ae8c8229ff` | boar-traces, matches `TRACES.tsv` |
| `dev-s42.traces.jsonl` | `4a5cf1c6843d7431932432b0ac76c72778ef36cae68578dccf3e60209e106ce4` | boar-traces, matches `TRACES.tsv` |
| `dev-s43.traces.jsonl` | `6f68bdbd93abe0d7453940bc4cc059dad458a78d0158dc24daec365c750562a7` | boar-traces, matches `TRACES.tsv` |
| `questions.jsonl` | `fc39b032f84a6f3e52da90178283535772c2d38f70e87d38dbcacc0b8ec78d08` | HF `rnd/research/coordinator/arms/native-rc/work/v04/bench/questions.jsonl` |

Repos used: boar-research 1.1.2 (`6b7caca9`), boar-bench 1.1.2 (`b41a25ac`). No private data, no phone, no model re-runs, no API keys.

## Scope and honesty

- The **headline conclusion is unchanged**: LabRat is below the 0.50 bar, 0 of 71 wins, and its correctness (2.5/5 vs 4.7/5) is genuinely worse. The finding is a **construct-validity** critique of the completeness/usefulness dimensions and of reading 0.052/0.079 as coverage, not a rescue of the app.
- The **counterfactual** `U(comp+use=ref)` is a sensitivity bound, not a proposed fix; `U(correctness=5)` is the realistic knowledge upper bound and still fails.
- The **closest prior claims** are 9328 (dimension split, coverage-bar reading), 9713 (floor=1), 9668 (Succinct ceiling), 9329 (ref mass), 9361 (0/71 saturation), 9556/9757 (true-zero). This submission adds the **distributions, zero item-level overlap, R², and both-subjective-dimension counterfactual**; it cites 9328 and 9713 explicitly.
- Appendix A (`blind()`) is a **secondary** code defect, reported with its small/confounded effect (<0.01 U), not the main claim.

## Existing claims reviewed

All 48 claims on bounty 1520 were pulled via the POIDH MCP API (`get_bounty`, chain `base`, id 1520) on 2026-11-21; full list in `data/claims_1520.csv`. The report's section 7 groups them by area and states the delta against the closest ones. No claim reports the per-dimension distributions, the zero item-level overlap, or the R²/counterfactual decomposition used here.

## Claim

`claim.md` is 1,189 characters; replace `[LINK]` with the published report URL before submitting. The main agent handles the wallet and the claim transaction.
