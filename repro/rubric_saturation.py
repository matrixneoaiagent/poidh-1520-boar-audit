#!/usr/bin/env python3
"""Repro: the v0.4 ruler's completeness and usefulness dimensions are disjoint between
LabRat and the reference. CPU-only, stdlib only, no LLM calls.

Reads the published DEVICE-FINAL judgments (seeds 42/43, Opus/Codex), the v0.4
questions (weights, anchor flag) and the phone traces (refusedZ).

Computes, per judgment set:
  * row-level and item-level histograms of the app and reference scores
  * the app's floor share (exactly 1.0) and the reference's ceiling share (exactly 5.0)
  * the min/max and the number of items where app >= ref (the overlap)
  * the floor-adjusted dimension ratios used by the record
  * R^2 of the per-item U on each dimension
  * counterfactual U with (a) correctness=5 everywhere, (b) completeness at the
    reference mean, (c) usefulness at the reference mean, (d) both subjective
    dimensions at the reference mean
  * an item bootstrap (B=2000, seed 11) for U and the counterfactuals

Outputs JSON to stdout and optionally to --json; a Markdown table to --md.
Usage:
  python3 repro/rubric_saturation.py [--data data] [--json out.json] [--md out.md]
"""
import argparse, collections, json, math, random, statistics as stt

DIM = ["correctness", "completeness", "usefulness"]
MEAN = lambda xs: sum(xs) / len(xs) if xs else float("nan")
rd = lambda p: [json.loads(l) for l in open(p) if l.strip()]

def load_set(data, fam, seed):
    q = {r["id"]: r for r in rd(f"{data}/questions.jsonl")}
    traces = {t["itemId"]: t for t in rd(f"{data}/dev-s{seed}.traces.jsonl")}
    per = collections.defaultdict(dict)
    for r in rd(f"{data}/dev-s{seed}.{fam}.judgments.jsonl"):
        if r.get("ok"):
            per[r["queryId"]][r["order"]] = r["mapped"]
    out = {}
    for i, qq in q.items():
        if len(per.get(i, {})) < 2:
            continue
        ms = list(per[i].values())
        out[i] = {
            "app": {k: MEAN([m["boar"][k] for m in ms]) for k in DIM},
            "ref": {k: MEAN([m["ref"][k] for m in ms]) for k in DIM},
            "z": bool(traces[i]["ruler"].get("refusedZ")),
            "weight": qq["weight"],
            "anchor": bool(qq["anchor"]),
        }
    return out

def u_of(row, override=None):
    r = MEAN([row["ref"][k] for k in DIM]) - 1.0
    if row["z"]:
        return 0.0, r
    app = dict(row["app"])
    if override:
        app.update(override)
    u = MEAN([app[k] for k in DIM]) - 1.0
    return u, r

def U(rows, ids, override=None):
    num = den = 0.0
    for i in ids:
        u, r = u_of(rows[i], override)
        num += rows[i]["weight"] * u
        den += rows[i]["weight"] * r
    return num / den if den else None

def stats(rows, ids):
    n = len(ids)
    app = {k: [rows[i]["app"][k] for i in ids] for k in DIM}
    ref = {k: [rows[i]["ref"][k] for i in ids] for k in DIM}
    out = {"n": n, "weight": sum(rows[i]["weight"] for i in ids)}
    for k in DIM:
        out[k] = {
            "app_mean": MEAN(app[k]), "app_sd": stt.pstdev(app[k]),
            "app_floor": sum(1 for v in app[k] if v == 1.0),
            "app_floor_share": sum(1 for v in app[k] if v == 1.0) / n,
            "app_ceil": sum(1 for v in app[k] if v == 5.0),
            "app_min": min(app[k]), "app_max": max(app[k]),
            "ref_mean": MEAN(ref[k]), "ref_sd": stt.pstdev(ref[k]),
            "ref_floor": sum(1 for v in ref[k] if v == 1.0),
            "ref_ceil": sum(1 for v in ref[k] if v == 5.0),
            "ref_ceil_share": sum(1 for v in ref[k] if v == 5.0) / n,
            "ref_min": min(ref[k]), "ref_max": max(ref[k]),
            "overlap_items": sum(1 for i in ids if rows[i]["app"][k] >= rows[i]["ref"][k]),
            "ratio": (MEAN(app[k]) - 1) / (MEAN(ref[k]) - 1),
        }
    # row-level histograms (both orders)
    out["row_hist"] = {}
    return out

def r2(xs, ys):
    mx, my = MEAN(xs), MEAN(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    return (sxy * sxy) / (sxx * syy) if sxx and syy else float("nan")

def boot(rows, ids, fn, B=2000, seed=11):
    rnd = random.Random(seed)
    vals = []
    for _ in range(B):
        sample = [rnd.choice(ids) for _ in ids]
        v = fn(sample)
        if v is not None:
            vals.append(v)
    vals.sort()
    return [round(vals[int(0.025 * len(vals))], 4), round(vals[int(0.975 * len(vals)) - 1], 4)]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data")
    ap.add_argument("--json")
    ap.add_argument("--md")
    a = ap.parse_args()
    q = {r["id"]: r for r in rd(f"{a.data}/questions.jsonl")}
    H = [i for i in q if not q[i]["anchor"]]
    res = {"sets": {}, "notes": {}}
    md = ["| set | n | app completeness mean (floor share) | ref completeness mean (ceiling share) | app usefulness mean (floor share) | ref usefulness mean (ceiling share) | comp ratio | use ratio | U |",
          "|---|---|---|---|---|---|---|---|---|"]
    for fam in ["opus", "codex"]:
        for seed in ["42", "43"]:
            rows = load_set(a.data, fam, seed)
            ids = [i for i in H if i in rows]
            s = stats(rows, ids)
            # row-level histograms from the raw judgment files (both orders)
            hist = {k: {"app": collections.Counter(), "ref": collections.Counter()} for k in DIM}
            for r in rd(f"{a.data}/dev-s{seed}.{fam}.judgments.jsonl"):
                if not r.get("ok") or r["queryId"] not in ids:
                    continue
                for k in DIM:
                    hist[k]["app"][r["mapped"]["boar"][k]] += 1
                    hist[k]["ref"][r["mapped"]["ref"][k]] += 1
            s["row_hist"] = {k: {side: dict(sorted(h.items())) for side, h in v.items()} for k, v in hist.items()}
            # U and counterfactuals
            s["U_actual"] = U(rows, ids)
            s["U_actual_ci"] = boot(rows, ids, lambda smp: U(rows, smp))
            s["U_correctness5"] = U(rows, ids, {"correctness": 5.0})
            s["U_correctness5_ci"] = boot(rows, ids, lambda smp: U(rows, smp, {"correctness": 5.0}))
            s["U_completeness_ref"] = U(rows, ids, {"completeness": MEAN([rows[i]["ref"]["completeness"] for i in ids])})
            s["U_usefulness_ref"] = U(rows, ids, {"usefulness": MEAN([rows[i]["ref"]["usefulness"] for i in ids])})
            s["U_comp_use_ref"] = U(rows, ids, {"completeness": MEAN([rows[i]["ref"]["completeness"] for i in ids]),
                                                 "usefulness": MEAN([rows[i]["ref"]["usefulness"] for i in ids])})
            s["U_comp_use_ref_ci"] = boot(rows, ids, lambda smp: U(rows, smp, {
                "completeness": MEAN([rows[i]["ref"]["completeness"] for i in ids]),
                "usefulness": MEAN([rows[i]["ref"]["usefulness"] for i in ids])}))
            # variance decomposition of per-item u
            us = [(rows[i]["app"]["correctness"] + rows[i]["app"]["completeness"] + rows[i]["app"]["usefulness"]) / 3 - 1 for i in ids]
            s["R2_u_on"] = {k: r2([rows[i]["app"][k] for i in ids], us) for k in DIM}
            s["corr"] = {f"{x}_{y}": stt.correlation([rows[i]["app"][x] for i in ids], [rows[i]["app"][y] for i in ids])
                         for x, y in [("correctness", "completeness"), ("correctness", "usefulness"), ("completeness", "usefulness")]}
            res["sets"][f"{fam}_s{seed}"] = s
            md.append("| {fam} s{seed} | {n} | {ac:.2f} ({af:.0%}) | {rc:.2f} ({rf:.0%}) | {au:.2f} ({auf:.0%}) | {ru:.2f} ({ruf:.0%}) | {cr:.3f} | {ur:.3f} | {U:.3f} |".format(
                fam=fam, seed=seed, n=s["n"], ac=s["completeness"]["app_mean"], af=s["completeness"]["app_floor_share"],
                rc=s["completeness"]["ref_mean"], rf=s["completeness"]["ref_ceil_share"],
                au=s["usefulness"]["app_mean"], auf=s["usefulness"]["app_floor_share"],
                ru=s["usefulness"]["ref_mean"], ruf=s["usefulness"]["ref_ceil_share"],
                cr=s["completeness"]["ratio"], ur=s["usefulness"]["ratio"], U=s["U_actual"]))
    res["notes"] = {
        "metric": "ruler v0.4 U-total: u=0 if trace refused else mean(3 dims)-1; r=mean(ref 3 dims)-1; U=sum(w*u)/sum(w*r); health weight 0.5",
        "counterfactual_correctness5": "replace the app's correctness with 5.0 on every item, keep completeness/usefulness as judged",
        "counterfactual_comp_use_ref": "replace the app's completeness and usefulness with the reference's item mean on every item, keep correctness as judged",
        "R2": "R^2 of the per-item u on one dimension, over the 71 headline items",
        "overlap": "items where the app's item-mean score >= the reference's item-mean score on that dimension",
    }
    if a.json:
        open(a.json, "w").write(json.dumps(res, indent=1, default=str) + "\n")
    if a.md:
        open(a.md, "w").write("\n".join(md) + "\n")
    # console summary
    for k, s in res["sets"].items():
        print(f"== {k}: n {s['n']} U {s['U_actual']:.3f} {s['U_actual_ci']}")
        for d in DIM:
            x = s[d]
            print(f"   {d:14s} app {x['app_mean']:.2f} [{x['app_min']:.1f},{x['app_max']:.1f}] floor {x['app_floor']}/{s['n']} ({x['app_floor_share']:.0%}) | "
                  f"ref {x['ref_mean']:.2f} [{x['ref_min']:.1f},{x['ref_max']:.1f}] ceil {x['ref_ceil']}/{s['n']} | overlap {x['overlap_items']} | ratio {x['ratio']:.3f}")
        print(f"   R2 u~ {s['R2_u_on']}")
        print(f"   U(correctness=5) {s['U_correctness5']:.3f} {s['U_correctness5_ci']} | U(comp+use=ref) {s['U_comp_use_ref']:.3f} {s['U_comp_use_ref_ci']}")
    print("\n" + "\n".join(md))

if __name__ == "__main__":
    main()
