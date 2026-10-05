"""Kiem tra tu dong san pham nop bai. Chay: python scripts/check_submission.py (exit 0 = tat ca dat)."""
import os
import re
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fails = []


def check(ok, msg):
    print(("PASS  " if ok else "FAIL  ") + msg)
    if not ok:
        fails.append(msg)


def read(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return f.read()


# 1. TEAMMATES: dung 5 dong thanh vien
tm = [l for l in read("TEAMMATES.md").splitlines() if re.match(r"^\d+\.\s", l)]
check(len(tm) == 5, f"TEAMMATES.md co dung 5 dong thanh vien (tim thay {len(tm)})")

# 2. bao cao thanh vien 1..5 (ten file tu do: nhan theo tieu de "Bao cao thanh vien N"), du 5 muc
REPORTS = {}
for fn in sorted(os.listdir(os.path.join(ROOT, "reports"))):
    if fn.endswith(".md"):
        m = re.match(r"#\s*Báo cáo thành viên (\d)", read(f"reports/{fn}"))
        if m:
            REPORTS.setdefault(int(m.group(1)), []).append(f"reports/{fn}")
dups = {i: v for i, v in REPORTS.items() if len(v) > 1}
check(not dups, "moi thanh vien co dung 1 file bao cao" + (f" (trung: {dups})" if dups else ""))
SECTIONS = ["Problem", "Method", "Benchmark", "Failure case", "Engineering decision"]
for i in range(1, 6):
    p = REPORTS.get(i, [f"reports/member_{i}.md"])[0]
    ex = i in REPORTS
    check(ex, f"bao cao thanh vien {i} ton tai ({p})")
    if ex:
        heads = re.findall(r"^##\s+(.+?)\s*$", read(p), flags=re.M)
        miss = [s for s in SECTIONS if not any(h.startswith(s) for h in heads)]
        check(not miss, f"{p} du 5 muc" + (f" (thieu {miss})" if miss else ""))

# 3. file/plot duoc dan phai ton tai
md_files = ["README.md", "SOURCES.md", "failure_case.md", "CHECKLIST.md", "design/benchmark_design.md",
            "pitch/pitch_script.md", "docs/team_explainer.md"] + [REPORTS.get(i, [f"reports/member_{i}.md"])[0] for i in range(1, 6)]
missing = set()
for p in md_files:
    if not os.path.exists(os.path.join(ROOT, p)):
        missing.add(f"{p} (chinh no)")
        continue
    txt = read(p)
    base = os.path.dirname(os.path.join(ROOT, p))
    for t in re.findall(r"\]\(([^)#\s]+)\)", txt):
        if not re.match(r"^(https?:|mailto:)", t) and not os.path.exists(os.path.normpath(os.path.join(base, t))):
            missing.add(f"{p} -> {t}")
    for t in re.findall(r"`((?:results|src|reports|pitch|docs|design|scripts)/[\w./-]+\.\w+)`", txt):
        if not os.path.exists(os.path.join(ROOT, t)):
            missing.add(f"{p} -> {t}")
check(not missing, "moi file/plot duoc dan deu ton tai" + (f" (thieu: {sorted(missing)})" if missing else ""))

# 4. so trong bao cao khop bang sinh tu results.csv
res = os.path.join(ROOT, "results")
need = ["results.csv", "summary_tables.md", "thresholds.csv", "params.json", "run_log.txt",
        "error_vs_offset.png", "comp_vs_uncomp.png", "failure_braking.png", "timeline_offset200ms.png"]
check(all(os.path.exists(os.path.join(res, f)) for f in need), "results/ du file ket qua")

NUM = re.compile(r"(?<![\w.])\d+\.\d+(?![\w.])")
table_nums = {round(float(x), 3) for x in NUM.findall(read("results/summary_tables.md"))}
# tham so thiet ke (khong phai ket qua do): sigma, chu ky, nguong, cua so, claim tolerance, tham so mo ta
DESIGN = {0.1, 0.5, 0.4, 0.95, 1.05, 0.7, 0.9, 0.8, 0.2, 0.01}
bad = []
for p in ["failure_case.md", "pitch/pitch_script.md", "docs/team_explainer.md"] + \
        [REPORTS.get(i, [f"reports/member_{i}.md"])[0] for i in range(1, 6)]:
    if not os.path.exists(os.path.join(ROOT, p)):
        continue
    for ln, line in enumerate(read(p).splitlines(), 1):
        if "[CHƯA" in line or "http" in line:
            continue
        line = re.sub(r"\d{4}\.\d{5}(v\d+)?", "", line)   # ma arXiv, khong phai so ket qua
        for tok in NUM.findall(line):
            if round(float(tok), 3) not in table_nums | DESIGN:
                bad.append(f"{p}:{ln}: {tok}")
check(not bad, "moi so thap phan trong bao cao/pitch/explainer co trong results/summary_tables.md hoac la tham so thiet ke"
      + (f" (khong khop: {bad[:15]})" if bad else ""))

# 5. claim T4 tren results.csv
if os.path.exists(os.path.join(res, "results.csv")):
    d = pd.read_csv(os.path.join(res, "results.csv"))
    u = d[(d.scenario == "const") & (d.method == "uncomp") & (d.offset_ms > 0)]
    check(u.ratio_nominal.between(0.95, 1.05).all(),
          f"C1: |bias|/(v*dt) tren toc do khong doi trong [0.95, 1.05] (min {u.ratio_nominal.min():.4f}, max {u.ratio_nominal.max():.4f})")
    bu = d[(d.scenario == "brake") & (d.method == "uncomp") & (d.decel_mps2 > 0) & (d.offset_ms > 0)]
    check((bu.ratio_nominal < 0.9).all(),
          f"C3: khi phanh, |bias|/(v0*dt) lech > 10% (max ratio {bu.ratio_nominal.max():.4f})")
    cv = d[(d.scenario == "brake") & (d.method == "comp_cv") & (d.offset_ms > 0)]
    mono = all((g.sort_values("decel_mps2").rmse_m.diff().dropna() > 0).all()
               for _, g in cv.groupby(["offset_ms", "window_n"]))
    check(mono, "C4: RMSE comp_cv tang don dieu theo |a| o moi (offset, N)")
    k = d[(d.scenario == "const") & (d.method == "comp_cv") & (d.offset_ms > 0)]
    k = k[k.v0_mps * k.offset_ms / 1000 >= 1]
    check((k.rmse_reduction_pct >= 70).all(), f"C2: giam RMSE >= 70% khi v*dt >= 1 m (min {k.rmse_reduction_pct.min():.1f}%)")
    ca = d[(d.scenario == "brake") & (d.method == "comp_ca") & (d.window_n == 5) & (d.offset_ms > 0)]
    c5 = d[(d.scenario == "brake") & (d.method == "comp_cv") & (d.window_n == 5) & (d.offset_ms > 0)]
    m = ca.merge(c5, on=["decel_mps2", "offset_ms"], suffixes=("_ca", "_cv"))
    print(f"INFO  C5 (claim comp_ca N=5 < comp_cv N=5): dung o {(m.rmse_m_ca < m.rmse_m_cv).sum()}/{len(m)} cau hinh -> claim SAI (da ghi trong design)")

# 6. placeholder con thieu
ph = set()
for p in md_files + ["TEAMMATES.md"]:
    if os.path.exists(os.path.join(ROOT, p)):
        ph.update(re.findall(r"\[CHƯA ĐIỀN: [^\]]+\]", read(p)))
print("\nPlaceholder con thieu:")
for x in sorted(ph):
    print("  " + x)

print("\nKET QUA:", "TAT CA PASS" if not fails else f"{len(fails)} FAIL")
sys.exit(1 if fails else 0)
