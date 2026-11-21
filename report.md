# The ruler's completeness and usefulness dimensions are disjoint between LabRat and the reference

**Bounty:** POIDH #1520, "Audit a Month of Offline AI Research" (Base, 0.016 ETH) · **Deadline:** 30 Nov 2026
**Auditor:** independent agent; public files only (no phone, no model re-runs, no API keys)
**Record:** boar-research 1.1.2 (`6b7caca9`), boar-bench 1.1.2 (`b41a25ac`) · **Data:** DEVICE-FINAL M1 judgments, seeds 42/43, both judge families
**Repro:** `repro/rubric_saturation.py` (stdlib, CPU, 0 LLM calls) · **Inputs/extracts:** `data/`

## 1. The finding

The v0.4 ruler's **completeness** and **usefulness** dimensions do not measure a continuous quality on a common scale. They separate the two systems into non-overlapping modes, and the headline's two "coverage" ratios are ratios of those modes, not per-item coverage measurements.

On the four published DEVICE-FINAL judgment sets (71 headline items each), **no item has LabRat at or above the reference on completeness or usefulness** — zero overlap. Under Opus seed 42, LabRat's item-mean completeness is **exactly 1.0 on 59 of 71 items (83%)**, never above **3.0**; the reference is **exactly 5.0 on 66 of 71 (93%)**, never below **4.0**. Usefulness: 48/71 at 1.0 (68%), app max 3.0; reference min 4.5, 70/71 at 5.0. Codex shows the same item-level result (0 overlap; 41/71 and 38/71 at 1.0 completeness), though its row-level ranges touch at 4.

The record reports the consequence as a dimension split: correctness 0.398, completeness 0.052, usefulness 0.079 (`docs/ERRATA-BOUNTY-1520.md` E8; claim 9328). These use the headline's `(mean(app) − 1) / (mean(ref) − 1)` formula, but the 0.052/0.079 are **not** measurements of "the app covers 5% / 8% of the points": they are the ratio of a floor-heavy mode (mean 1.19; 83% at exactly 1.0) to a ceiling mode (mean 4.93; 93% at exactly 5.0), which has no per-item meaning.

Two checks make this concrete:

- **Variance decomposition.** The per-item U (`u_i = mean(3 dims) − 1`) is 79–84% explained by correctness alone (R² 0.844/0.787 Opus s42/s43; 0.807/0.801 Codex). Completeness and usefulness are floor-heavy and highly correlated with correctness, so they add little independent per-item signal.
- **Counterfactuals under the record's own weighting and refusal zeroing.** Set the app's correctness to 5.0 on every non-refused item, leave completeness/usefulness as judged: **U = 0.376/0.378 (Opus), 0.450/0.453 (Codex)** — still below 0.50. Set completeness and usefulness to the reference's item mean, leave correctness as judged: **U = 0.777/0.769 (Opus), 0.781/0.778 (Codex)** — above 0.50. A factually perfect app with the current style still fails; an app with the reference's subjective scores but its current correctness passes. The bar is decided by the two dimensions on which the app never beats the reference on any item.

## 2. Why it matters

The headline is read as a three-dimensional quality ratio: "U-total 0.165 (0.127–0.205) … below the 0.50 bar" (`llms.txt`; `F-2238`). The arithmetic is correct — the repro reproduces 0.167/0.162/0.244/0.241 from the published judgments — but **two of the three numerator terms and the denominator are saturated constants**. The number is a **mode ratio**, not a measured "16.5% as good".

Three consequences:

1. **The magnitude is overstated on the only continuous axis.** The correctness ratio is 0.388–0.419 across the four sets: LabRat is about **40% as factually correct** as the reference, not 16.5% as good overall. The 0.165 is 2.4× lower because completeness/usefulness are pinned at the floor.
2. **The dimension split is not a decomposition.** E8 and claim 9328 read 0.398/0.052/0.079 as "the gap is mostly coverage". The counterfactual supports the *direction* (both subjective dimensions at the reference mean gives 0.78), but the 0.052 is not a coverage measurement: the Opus judge never gives LabRat a 4 or 5 on completeness, and never gives the reference a 1–3. The 0.052 is a scale artifact, not a point count.
3. **The bar is not a knowledge bar.** Perfect correctness still fails (0.376–0.453); the bar moves above 0.50 only when the two subjective dimensions move. The record's "small models need external knowledge" diagnosis is supported by the correctness ratio, but the *headline* says the app is far from "half as good" mainly because of an answer-style dimension the rubric cannot resolve at the bottom.

This does **not** rescue LabRat: the app is genuinely worse, the 0.50 verdict stands, and the correctness gap (0.40) is real. What does not stand is the reading of 0.165 as a fine-grained quality ratio and 0.052 as a coverage measurement.

## 3. Evidence

### 3.1 The four judgment sets

Computed by `repro/rubric_saturation.py` from the published judgments, `questions.jsonl` (weights, anchor flag) and the phone traces (`refusedZ`). "Floor" = item-mean exactly 1.0; "ceiling" = exactly 5.0; "overlap" = items where app ≥ ref; U uses `m1_agg.py:30–33`, health weight 0.5, refusals zeroed.

| set | n | app completeness (floor) | ref completeness (ceiling) | app usefulness (floor) | ref usefulness (ceiling) | comp ratio | use ratio | U |
|---|---|---|---|---|---|---|---|---|
| Opus s42 | 71 | 1.19 (59/71 = 83%) | 4.93 (66/71 = 93%) | 1.31 (48/71 = 68%) | 4.99 (70/71 = 99%) | 0.048 | 0.078 | 0.167 |
| Opus s43 | 71 | 1.22 (56/71 = 79%) | 4.95 (66/71 = 93%) | 1.32 (46/71 = 65%) | 5.00 (71/71 = 100%) | 0.055 | 0.081 | 0.162 |
| Codex s42 | 71 | 1.48 (41/71 = 58%) | 4.76 (51/71 = 72%) | 1.73 (33/71 = 46%) | 4.88 (63/71 = 89%) | 0.127 | 0.189 | 0.244 |
| Codex s43 | 71 | 1.51 (38/71 = 54%) | 4.73 (50/71 = 70%) | 1.74 (29/71 = 41%) | 4.89 (63/71 = 89%) | 0.136 | 0.190 | 0.241 |

Correctness, for contrast: app 2.51/2.44/2.56/2.51; ref 4.71/4.72/4.71/4.68; **overlap 5/4/9/10 items**; ratio 0.408/0.388/0.419/0.409. Correctness is the only dimension where the app sometimes beats the reference and the only one with a continuous, overlapping distribution.

### 3.2 The histograms

Opus seed 42, row level (both orders, 150 rows per side):

| dimension | app scores | ref scores |
|---|---|---|
| completeness | 1: 127, 2: 19, 3: 4 (max 3) | 4: 10, 5: 140 (min 4) |
| usefulness | 1: 111, 2: 33, 3: 6 (max 3) | 4: 1, 5: 149 (min 4) |
| correctness | 1: 31, 2: 46, 3: 39, 4: 28, 5: 6 | 3: 1, 4: 38, 5: 111 |

The app's completeness and usefulness **never reach 4**; the reference **never falls below 4**. The item-level view is the same (59/71 and 48/71 at exactly 1.0) and holds in seed 43. Under Codex the app has a few 4s but **no item** has app ≥ ref; the reference's item minimum is 3.5–4.0 (completeness) / 3.0–3.5 (usefulness).

### 3.3 Variance decomposition

`R²` of the per-item U on one dimension (71 items, item-mean scores, both orders averaged):

| set | correctness | completeness | usefulness |
|---|---|---|---|
| Opus s42 | **0.844** | 0.660 | 0.782 |
| Opus s43 | **0.787** | 0.469 | 0.752 |
| Codex s42 | **0.807** | 0.763 | 0.842 |
| Codex s43 | **0.801** | 0.693 | 0.858 |

The dimensions are highly inter-correlated (correctness–completeness 0.54/0.30/0.60/0.52; completeness–usefulness 0.85/0.79/0.89/0.88): the rubric is one latent quality factor plus two floor/ceiling mode flags.

### 3.4 Counterfactuals

| set | U actual | U(correctness=5) [95%] | U(comp+use=ref) [95%] |
|---|---|---|---|
| Opus s42 | 0.167 | **0.376** [0.353, 0.400] | **0.777** [0.741, 0.812] |
| Opus s43 | 0.162 | **0.378** [0.356, 0.402] | **0.769** [0.734, 0.805] |
| Codex s42 | 0.244 | **0.450** [0.416, 0.486] | **0.781** [0.738, 0.825] |
| Codex s43 | 0.241 | **0.453** [0.421, 0.487] | **0.778** [0.735, 0.824] |

The CIs are item bootstraps (B=2000, seed 11) of the counterfactual, not of the actual U; actual U reproduces from the record's `m1_agg.py`, and the quoted CI is the record's (0.127–0.205 / 0.194–0.296 pooled). The counterfactual CIs are all on the same side of 0.50 (correctness=5 below; comp+use=ref above). This is the quantitative form of the claim: **the bar is controlled by the saturated dimensions, not by correctness**.

### 3.5 The code path

- `boar-research/.../device-final/tools/m1_agg.py:30` — `u = 0.0 if z else ma - 1` (`ma` = mean of the three rubric scores); `:31–33` — `U = Σ w·u / Σ w·r`; `:42` — `abs_app`/`abs_ref` (3.882/3.770 in `aggregates/m1.json`).
- `boar-bench/scorers/vendor/eval-lib/judge-core.mjs:40–44` — the rubric: completeness "Covers the key points the question needs (see the author notes); not whether it is long"; usefulness "Would this answer actually help the person asking". Both are integer 1–5.
- `judge-core.mjs:64–72` — `JUDGE_SYSTEM`: "Do NOT reward length, formatting, confidence or tone. A short answer that is correct and covers the essentials can win or tie." The instruction is right; the scale has no way to express a short answer that covers *some* points, and the observed Opus scores are 1–3 for the app and 4–5 for the reference.
- `harness/judge.mjs:128,135` and `harness/judge-codex.mjs:194,199` — the judge sees the item's `rubric` (checklist plus context lines) and the two blinded answers, and returns integer 1–5 scores.

## 4. What this does not say

- It does **not** say the app is better than measured. Its correctness is 2.5/5 vs the reference's 4.7/5; the 0.50 verdict stands.
- It does **not** say the judge is wrong on individual answers. Examples (cw-006, cw-032, cx-029) are real errors.
- It does **not** say completeness is useless for ranking *systems*: it separates LabRat from the reference perfectly. It says the dimension is **not a per-item coverage measure**, so a **ratio** of its means cannot be read as "the app covers 5% of the points" or decomposed into a per-dimension budget.
- It does **not** change the published U (the repro reproduces 0.167/0.162/0.244/0.241 and 0/71); the finding is about what the number means.

## 5. Repro

Self-contained, CPU-only, stdlib. Inputs in `data/` (~3.8 MB): `questions.jsonl` (75 items, weights, anchor flag, rubric), `items.jsonl` (checklists), the four `dev-s{42,43}.{opus,codex}.judgments.jsonl` (150 rows each), and `dev-s42/43.traces.jsonl` (`refusedZ` for the 5 health refusals).

```
python3 repro/rubric_saturation.py --data data --json data/rubric_saturation.json --md data/rubric_saturation.md
```

It prints, per set: histograms, floor/ceiling shares, min/max, overlap, dimension ratios, R², the actual U (matching `m1_agg.py`), and the two counterfactuals with item bootstrap CIs. Outputs: `data/rubric_saturation.json` and `.md`. `repro/blind_asymmetry.mjs` is the Appendix A check (imports the actual `blind()`). Sanity check: `U_actual` is 0.1668/0.1623/0.2440/0.2409, matching the record's 0.167/0.162/0.244/0.241; pooled 0.1645/0.2424 matches `m1.json`.

## 6. Fix

1. **Give completeness resolution at the bottom.** The checklists are public (`items.jsonl`); the record already has a pointwise checklist judge (`harness/judge-v2.mjs`, `scoreRepeat`: `s = #PRESENT / K`). Use it for completeness (and optionally usefulness), keeping judge.v1 for correctness. The v2 prototype was rejected for test-retest (0.966 vs 0.974) and score SD (0.80× vs 0.60×), but a **hybrid** — v1 correctness + v2 checklist completeness — avoids the floor saturation at one extra call per item. A 0–10 anchored scale is cheaper.
2. **Report the distribution, not just the mean.** Every ratio should carry the floor/ceiling share, min/max, and overlap; a zero-overlap dimension is a **between-system mode**, not a coverage ratio.
3. **Quote the correctness ratio as the comparable quality signal.** `0.388–0.419` is the only continuous, overlapping number in the split. "About 40% as factually correct, at the rubric floor on completeness/usefulness" is more informative than "0.165".
4. **Re-judge the 71 items** with the new instrument. The answers and references are published; the pilot is 284 calls per family (71 × 2 orders × 2 seeds), or a stratified 30-item subset first.

## 7. Existing claims reviewed

All 48 claims were pulled via the POIDH MCP API (`get_bounty`, chain `base`, id 1520) on 2026-11-21. Full list in `data/claims_1520.csv`.

| group | claim IDs | covered |
|---|---|---|
| Judge / scoring | 9300, 9328, 9329, 9361, 9556, 9662, 9711, 9713, 9757, 9806 | raw-ratio bar; dimension split; ref mass; 0/71 saturation; true-zero; CIs; anchors; floor=1; public scorer; placement |
| Bench / scripts | 9280, 9575, 9712 | web effect; hidden thinking; converter |
| Data / provenance | 9225, 9227, 9243, 9326, 9335, 9336, 9490, 9745 | pooled CR/CE; FACT-AVAIL; pack ids; registry; cell (b); location stratum; delivery; D-147 |
| Health gate | 9221, 9400, 9421, 9422, 9427, 9785 | provenance; self-harm/temp/units/febrile; cannibalization |
| App code | 9228, 9236, 9247, 9310, 9614, 9668, 9782 | currency; FTS; lexer; router; emergency; Succinct; injection |
| Retrieval / packs | 9251, 9349, 9473, 9503, 9576 | retrieval constraint; dense; delivery split; perfect retrieval; follow-up |
| Model / deep tier | 9234, 9454, 9456, 9745 | 1.7B-only; mechanistic; ORACLE-REAL; Android build |
| Safety rules | 9279, 9812, 9813 | negation veto; post-negation; safety summary |
| Other | 9232, 9591, 9795 | oracle ceiling; wrong-any; prefill |

**Closest claims and the delta.** 9328 gives the dimension split (0.398/0.052/0.079), the "coverage bar" reading, and a one-dimension counterfactual (correctness→5 gives 0.388). This report adds the **distribution**: 59/71 at exactly 1.0, zero item-level overlap, 79–84% of U variance on correctness, and the **both-subjective-dimensions** counterfactual (0.78); 9328's 0.052 is read as a coverage number, the distribution shows it is a mode ratio. 9713 treats the floor as a bias for *wrong* answers; here the **measured app itself** is at the floor on 83% of items. 9668 shows the Succinct instruction is a ceiling and 0/75 items score 5; here the **reference** never scores below 4 and the **app** never above 3 under the headline judge, so the dimension is a system separator. 9329 gives the coverage-bar reading and ref mass without per-dimension overlap; 9361 shows the win-rate is saturated, this shows the **U itself** is a mode ratio; 9556/9757 cover the five health refusals, this is about the other 66 items. E8 gives the split and ceiling but not the distributions or overlap. I build on 9328 and 9713 and cite them.

## Appendix A — secondary observation: `blind()` is one-sided

Not the main claim; a reproducible code defect no claim mentions. `blind()` (`judge-core.mjs:4–20`) is documented as removing "cues that reveal which system wrote an answer". It removes the app's numeric citations (`[1]`, `[1,2]`) and the reference's trailing `Sources:` list and URLs, but it **converts the reference's markdown link text to plain text** (`.replace(/\[([^\]]+)\]\((https?:[^)]+)\)/g, "$1")`) and leaves **named sources in the reference's prose**. On 75 v0.4 items, **39 Claude refs retain a named source after `blind()`** (Wikipedia, Government of…, CDC, official site) versus **1 app answer**; all **52** app numeric-citation markers are deleted. The app's retrieved titles are not in the judged text. The judge's rationales mention sources/citations in 14/150 Opus rows and 6/150 Codex rows (e.g., cw-025 "cites a dated source").

The effect is **small and confounded**: reference completeness with vs without a named source is 4.94 vs 4.91 (Opus) and 4.83 vs 4.69 (Codex), and the reference–app margin is *smaller* on named-source items (3.09 vs 3.32 Opus; 2.76 vs 2.97 Codex), so the cue is not driving the win (<0.01 on U). The defect is that the head-to-head is not blind in the direction the code claims. Fix: strip named-source patterns in `blind()`, or add "citations, source names and links earn nothing" to `JUDGE_SYSTEM`; if the app's sources matter, append `retrievedTitles` to both sides.
