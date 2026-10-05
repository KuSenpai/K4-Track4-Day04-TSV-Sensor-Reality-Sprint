"""T4 benchmark: sai so vi tri do lech thoi gian camera-LiDAR (du lieu tong hop).

Entrypoint duy nhat:  python src/run_benchmark.py
Ghi ra results/: results.csv, thresholds.csv, params.json, run_log.txt, *.png
"""
import json
import os
import sys

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------------------------------------------------------- tham so co dinh
SEED = 42
H = 0.1                      # chu ky lay mau 10 Hz (camera va LiDAR) [s]
N_FRAMES = 100               # 10 s
N_TRIALS = 200
SIGMA = 0.10                 # nhieu do LiDAR moi truc [m] (gia dinh cua nhom)
THETA = np.deg2rad(15.0)     # huong chuyen dong
OFFSETS_MS = [0, 50, 100, 150, 200]
SPEEDS = [5.0, 10.0, 20.0, 30.0]          # m/s, kich ban toc do khong doi
DECELS = [0.0, 2.0, 4.0, 6.0, 8.0]        # m/s^2, kich ban phanh
BRAKE_V0 = 20.0
BRAKE_ONSET = 5.0            # s
BRAKE_WINDOW = (5.0, 8.0)    # s
CONST_WINDOW = (1.0, 10.0)   # s, bo 1 s khoi dong
V_MIN = 0.1                  # chi tinh khung co toc do that > V_MIN
THRESHOLD_M = 0.5            # nguong "dang lo" (gia dinh cua nhom)
WINDOWS_CV = [3, 5, 9]
WINDOWS_CA = [5, 9]
DEFAULT_N = 5

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
U = np.array([np.cos(THETA), np.sin(THETA)])   # vector huong don vi

_log_lines = []


def log(msg=""):
    print(msg)
    _log_lines.append(msg)


# ---------------------------------------------------------------- chuyen dong that
def arc_and_speed(t, v0, a, t_on):
    """Quang duong s(t) va toc do v(t): toc do v0, phanh deu a sau t_on cho den khi dung."""
    t = np.asarray(t, dtype=float)
    if a <= 0:
        return v0 * t, np.full_like(t, v0)
    tau = np.clip(t - t_on, 0.0, v0 / a)
    s = v0 * t_on + v0 * tau - 0.5 * a * tau**2
    s = np.where(t <= t_on, v0 * t, s)
    v = np.where(t <= t_on, v0, np.maximum(v0 - a * tau, 0.0))
    return s, v


def position(t, v0, a, t_on):
    s, v = arc_and_speed(t, v0, a, t_on)
    return s[..., None] * U, v


# ---------------------------------------------------------------- bo bu
def fit_weights(n, degree, dt_s):
    """Trong so w (n,) sao cho w @ z = gia tri ngoai suy sau dt_s cua da thuc bac `degree`
    khop LSQ tren n mau gan nhat (muc thoi gian s = -(n-1)h ... 0, ngoai suy tai s = dt_s)."""
    s = (np.arange(n) - (n - 1)) * H
    A = np.vander(s, degree + 1, increasing=True)
    basis = np.array([dt_s**p for p in range(degree + 1)])
    return basis @ np.linalg.pinv(A)


def estimate(z, n, degree, dt_s):
    """z: (trials, frames, 2). Tra ve uoc luong (trials, frames-n+1, 2), tai khung k = idx + n - 1."""
    w = fit_weights(n, degree, dt_s)
    win = np.lib.stride_tricks.sliding_window_view(z, n, axis=1)   # (T, F-n+1, 2, n)
    return win @ w


# ---------------------------------------------------------------- chay mot kich ban
def run_condition(noise, scenario, v0, a, t_on, window, dt_ms):
    """Tra ve cac dong ket qua (uncomp + comp) cho mot kich ban/offset."""
    dt_s = dt_ms / 1000.0
    tk = np.arange(N_FRAMES) * H
    p_true, v_true = position(tk, v0, a, t_on)                    # (F,2), (F,)
    p_meas, _ = position(tk - dt_s, v0, a, t_on)                  # LiDAR do tai t_k - dt
    z = p_meas[None] + noise                                      # (T,F,2)

    in_win = (tk >= window[0]) & (tk <= window[1]) & (v_true > V_MIN)
    vdt_nom = v0 * dt_s
    vdt_inst = float(v_true[in_win].mean() * dt_s)

    methods = [("uncomp", None, None, z)]
    for n in WINDOWS_CV if scenario == "brake" else [DEFAULT_N]:
        est = np.full_like(z, np.nan)
        est[:, n - 1:] = estimate(z, n, 1, dt_s)
        methods.append(("comp_cv", n, 1, est))
    if scenario == "brake":
        for n in WINDOWS_CA:
            est = np.full_like(z, np.nan)
            est[:, n - 1:] = estimate(z, n, 2, dt_s)
            methods.append(("comp_ca", n, 2, est))

    rows, base_rmse = [], None
    for name, n, _, est in methods:
        e = (est - p_true[None])[:, in_win]                       # (T,Fe,2)
        if np.isnan(e).any():
            raise RuntimeError("khung danh gia chua du mau cho cua so N")
        norm = np.linalg.norm(e, axis=-1)
        along = e @ U
        rmse = float(np.sqrt((norm**2).mean()))
        if name == "uncomp":
            base_rmse = rmse
        bias = float(along.mean())
        # trang thai on dinh khi phanh: ca cua so N nam trong pha phanh va vat chua dung
        steady_bias = pred_steady = np.nan
        if name != "uncomp" and a > 0:
            steady = in_win & (tk - dt_s - (n - 1) * H >= t_on) & (tk <= t_on + v0 / a)
            if steady.any():
                steady_bias = float(((est - p_true[None])[:, steady] @ U).mean())
                # LSQ tuyen tinh tren da thuc bac 2 (gia toc a): sai so giai tich
                pred_steady = (0.5 * a * ((dt_s + (n - 1) * H / 2) ** 2 - H**2 * (n**2 - 1) / 12)
                               if name == "comp_cv" else 0.0)
        rows.append(dict(
            scenario=scenario, v0_mps=v0, decel_mps2=a, offset_ms=dt_ms,
            method=name, window_n=n if n else "",
            n_trials=N_TRIALS, n_frames_eval=int(in_win.sum()),
            rmse_m=rmse, mean_err_m=float(norm.mean()),
            p95_err_m=float(np.percentile(norm, 95)),
            frac_gt_thr=float((norm > THRESHOLD_M).mean()),
            along_bias_m=bias,
            along_bias_steady_m=steady_bias, pred_bias_steady_m=pred_steady,
            vdt_nominal_m=vdt_nom, vdt_inst_m=vdt_inst,
            ratio_nominal=abs(bias) / vdt_nom if dt_ms > 0 and name == "uncomp" else np.nan,
            ratio_inst=abs(bias) / vdt_inst if dt_ms > 0 and name == "uncomp" else np.nan,
            rmse_reduction_pct=(100.0 * (base_rmse - rmse) / base_rmse
                                if name != "uncomp" and dt_ms > 0 else np.nan),
        ))
    return rows


def main():
    os.makedirs(RES, exist_ok=True)
    rng = np.random.default_rng(SEED)
    noise = rng.normal(0.0, SIGMA, size=(N_TRIALS, N_FRAMES, 2))   # cung 1 mang nhieu cho moi dieu kien

    params = dict(seed=SEED, h_s=H, n_frames=N_FRAMES, n_trials=N_TRIALS, sigma_m=SIGMA,
                  theta_deg=15.0, offsets_ms=OFFSETS_MS, speeds_mps=SPEEDS, decels_mps2=DECELS,
                  brake_v0_mps=BRAKE_V0, brake_onset_s=BRAKE_ONSET, brake_window_s=BRAKE_WINDOW,
                  const_window_s=CONST_WINDOW, threshold_m=THRESHOLD_M, windows_cv=WINDOWS_CV,
                  windows_ca=WINDOWS_CA, default_n=DEFAULT_N, data="synthetic")
    with open(os.path.join(RES, "params.json"), "w", encoding="utf-8") as f:
        json.dump(params, f, indent=2)
    log(f"python {sys.version.split()[0]}  numpy {np.__version__}  pandas {pd.__version__}")
    log("params: " + json.dumps(params))

    rows = []
    for v in SPEEDS:
        for dt in OFFSETS_MS:
            rows += run_condition(noise, "const", v, 0.0, 0.0, CONST_WINDOW, dt)
    for a in DECELS:
        for dt in OFFSETS_MS:
            rows += run_condition(noise, "brake", BRAKE_V0, a, BRAKE_ONSET, BRAKE_WINDOW, dt)
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(RES, "results.csv"), index=False, float_format="%.4f")
    log(f"results.csv: {len(df)} dong")

    # ---- toc do nguy hiem v* = nguong / dt (suy tu cong thuc v*dt, da kiem trong C1)
    th = pd.DataFrame([dict(offset_ms=d, threshold_m=THRESHOLD_M, v_star_mps=THRESHOLD_M / (d / 1000.0),
                            v_star_kmh=3.6 * THRESHOLD_M / (d / 1000.0)) for d in OFFSETS_MS if d > 0])
    th.to_csv(os.path.join(RES, "thresholds.csv"), index=False, float_format="%.4f")

    # ---- in tom tat
    pd.set_option("display.width", 220, "display.max_columns", 30)
    c = df[(df.scenario == "const") & (df.method == "uncomp")]
    log("\n[C1] const-speed, uncomp: |along bias| vs v*dt")
    log(c[["v0_mps", "offset_ms", "rmse_m", "along_bias_m", "vdt_nominal_m", "ratio_nominal"]]
        .to_string(index=False, float_format=lambda x: f"{x:.4f}"))
    cc = df[(df.scenario == "const") & (df.method == "comp_cv")]
    log("\n[C2] const-speed, comp_cv N=5: rmse + % reduction")
    log(cc[["v0_mps", "offset_ms", "rmse_m", "rmse_reduction_pct"]]
        .to_string(index=False, float_format=lambda x: f"{x:.4f}"))
    b = df[df.scenario == "brake"]
    log("\n[C3] brake, uncomp: ratio vs nominal / instantaneous speed")
    log(b[b.method == "uncomp"][["decel_mps2", "offset_ms", "rmse_m", "along_bias_m", "vdt_nominal_m",
                                 "vdt_inst_m", "ratio_nominal", "ratio_inst"]]
        .to_string(index=False, float_format=lambda x: f"{x:.4f}"))
    log("\n[C4/C5] brake, compensated residual")
    log(b[b.method != "uncomp"][["decel_mps2", "offset_ms", "method", "window_n", "rmse_m", "along_bias_m",
                                 "along_bias_steady_m", "pred_bias_steady_m",
                                 "frac_gt_thr", "rmse_reduction_pct"]]
        .to_string(index=False, float_format=lambda x: f"{x:.4f}"))

    make_plots(df, noise)
    write_tables(df, th)
    with open(os.path.join(RES, "run_log.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(_log_lines) + "\n")
    print("DONE")


# ---------------------------------------------------------------- bang markdown tu CSV
def md(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(out)


def write_tables(df, th):
    """Sinh results/summary_tables.md: moi so trong bao cao phai lay tu cac bang nay."""
    f2 = lambda x: "0.00" if f"{x:.2f}" == "-0.00" else f"{x:.2f}"
    parts = ["# Bang tong hop (sinh tu results/results.csv boi src/run_benchmark.py)\n"]

    c = df[df.scenario == "const"]
    rows = []
    for v in SPEEDS:
        for dt in OFFSETS_MS:
            u = c[(c.v0_mps == v) & (c.offset_ms == dt) & (c.method == "uncomp")].iloc[0]
            k = c[(c.v0_mps == v) & (c.offset_ms == dt) & (c.method == "comp_cv")].iloc[0]
            rows.append([f"{v:g}", str(dt), f2(u.vdt_nominal_m), f2(abs(u.along_bias_m)),
                         "-" if dt == 0 else f"{u.ratio_nominal:.3f}", f2(u.rmse_m), f2(k.rmse_m),
                         "-" if dt == 0 else f"{k.rmse_reduction_pct:.1f}"])
    parts += ["## Bang A - toc do khong doi (uncomp vs comp_cv N=5)\n",
              md(["v (m/s)", "offset (ms)", "v*dt (m)", "|bias| (m)", "|bias|/(v*dt)",
                  "RMSE khong bu (m)", "RMSE bu (m)", "giam RMSE (%)"], rows), ""]

    b = df[df.scenario == "brake"]
    rows = []
    for a in DECELS:
        for dt in OFFSETS_MS[1:]:
            u = b[(b.decel_mps2 == a) & (b.offset_ms == dt) & (b.method == "uncomp")].iloc[0]
            rows.append([f"{a:g}", str(dt), f2(u.vdt_nominal_m), f2(u.vdt_inst_m), f2(abs(u.along_bias_m)),
                         f"{u.ratio_nominal:.3f}", f"{u.ratio_inst:.3f}", f2(u.rmse_m)])
    parts += ["## Bang B - phanh, khong bu (v0 = 20 m/s, cua so 5-8 s)\n",
              md(["a (m/s^2)", "offset (ms)", "v0*dt (m)", "v(t)*dt TB (m)", "|bias| (m)",
                  "ty so theo v0", "ty so theo v(t)", "RMSE khong bu (m)"], rows), ""]

    def pick(a, dt, m, n=None):
        s = b[(b.decel_mps2 == a) & (b.offset_ms == dt) & (b.method == m)]
        if n is not None:
            s = s[s.window_n == n]
        return s.iloc[0]

    rows = []
    for a in DECELS:
        for dt in OFFSETS_MS:
            rows.append([f"{a:g}", str(dt), f2(pick(a, dt, "uncomp").rmse_m),
                         f2(pick(a, dt, "comp_cv", 3).rmse_m), f2(pick(a, dt, "comp_cv", 5).rmse_m),
                         f2(pick(a, dt, "comp_cv", 9).rmse_m), f2(pick(a, dt, "comp_ca", 5).rmse_m),
                         f2(pick(a, dt, "comp_ca", 9).rmse_m)])
    parts += ["## Bang C - phanh, RMSE (m) sau bu theo bo bu\n",
              md(["a (m/s^2)", "offset (ms)", "khong bu", "cv N=3", "cv N=5", "cv N=9", "ca N=5", "ca N=9"],
                 rows), ""]

    rows = []
    for a in DECELS[1:]:
        for dt in OFFSETS_MS[1:]:
            r5, r9 = pick(a, dt, "comp_cv", 5), pick(a, dt, "comp_cv", 9)
            rows.append([f"{a:g}", str(dt), f2(r5.along_bias_m), f2(r5.along_bias_steady_m),
                         f2(r5.pred_bias_steady_m),
                         f2(r9.along_bias_steady_m), f2(r9.pred_bias_steady_m),
                         f2(pick(a, dt, "comp_ca", 5).along_bias_steady_m),
                         f2(pick(a, dt, "comp_ca", 9).along_bias_steady_m)])
    parts += ["## Bang D - phanh, bias on dinh (m) cua comp: do duoc vs cong thuc giai tich\n",
              md(["a (m/s^2)", "offset (ms)", "cv N=5 bias ca cua so", "cv N=5 do (on dinh)",
                  "cv N=5 cong thuc", "cv N=9 do",
                  "cv N=9 cong thuc", "ca N=5 do", "ca N=9 do"], rows), ""]

    rows = [[str(int(r.offset_ms)), f2(r.threshold_m), f"{r.v_star_mps:.1f}", f"{r.v_star_kmh:.0f}"]
            for r in th.itertuples()]
    parts += ["## Bang E - toc do nguy hiem v* = nguong / dt\n",
              md(["offset (ms)", "nguong (m)", "v* (m/s)", "v* (km/h)"], rows), ""]

    rows = []
    for dt in OFFSETS_MS[1:]:
        fr = [pick(a, dt, "comp_cv", 5).frac_gt_thr for a in DECELS]
        rows.append([str(dt)] + [f"{100 * x:.1f}" for x in fr])
    parts += ["## Bang F - phanh, ty le khung co sai so > 0.5 m sau bu comp_cv N=5 (%)\n",
              md(["offset (ms)"] + [f"a={a:g}" for a in DECELS], rows), ""]

    with open(os.path.join(RES, "summary_tables.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(parts) + "\n")


# ---------------------------------------------------------------- plot
COLORS = {5.0: "#1b9e77", 10.0: "#d95f02", 20.0: "#7570b3", 30.0: "#e7298a"}


def make_plots(df, noise):
    c = df[df.scenario == "const"]
    offs = np.array(OFFSETS_MS)

    # 1. sai so khong bu vs offset, doi chieu v*dt
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for v in SPEEDS:
        d = c[(c.v0_mps == v) & (c.method == "uncomp")]
        ax.plot(d.offset_ms, d.mean_err_m, "o-", color=COLORS[v], label=f"do duoc, v={v:g} m/s")
        ax.plot(offs, v * offs / 1000.0, "--", color=COLORS[v], alpha=0.6)
    ax.plot([], [], "k--", alpha=0.6, label="cong thuc v*dt")
    ax.axhline(THRESHOLD_M, color="red", lw=1, ls=":", label=f"nguong {THRESHOLD_M} m (gia dinh)")
    ax.set_xlabel("Do lech thoi gian LiDAR (ms)")
    ax.set_ylabel("Sai so vi tri trung binh, khong bu (m)")
    ax.set_title("Toc do khong doi: sai so do duoc vs v*dt (du lieu tong hop)")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(RES, "error_vs_offset.png"), dpi=140)
    plt.close(fig)

    # 2. RMSE khong bu vs co bu
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for v in SPEEDS:
        u = c[(c.v0_mps == v) & (c.method == "uncomp")]
        k = c[(c.v0_mps == v) & (c.method == "comp_cv")]
        ax.plot(u.offset_ms, u.rmse_m, "o-", color=COLORS[v], label=f"khong bu, v={v:g} m/s")
        ax.plot(k.offset_ms, k.rmse_m, "s--", color=COLORS[v], label=f"bu comp_cv, v={v:g} m/s")
    ax.set_yscale("log")
    ax.set_xlabel("Do lech thoi gian LiDAR (ms)")
    ax.set_ylabel("RMSE vi tri (m, thang log)")
    ax.set_title("Toc do khong doi: RMSE truoc/sau khi bu (N=5)")
    ax.legend(fontsize=7, ncol=2)
    ax.grid(alpha=0.3, which="both")
    fig.tight_layout()
    fig.savefig(os.path.join(RES, "comp_vs_uncomp.png"), dpi=140)
    plt.close(fig)

    # 3. failure: phanh
    b = df[df.scenario == "brake"]
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.5))
    for dt, col in [(100, "#1f78b4"), (200, "#e31a1c")]:
        for meth, n, mk in [("comp_cv", 5, "o-"), ("comp_ca", 5, "s--")]:
            d = b[(b.offset_ms == dt) & (b.method == meth) & (b.window_n == n)]
            axs[0].plot(d.decel_mps2, d.rmse_m, mk, color=col, label=f"{meth} N={n}, offset {dt} ms")
    axs[0].set_xlabel("Gia toc phanh cua vat the (m/s^2)")
    axs[0].set_ylabel("RMSE sau khi bu (m)")
    axs[0].set_title("Sai so du sau bu khi phanh (v0=20 m/s)")
    axs[0].legend(fontsize=7)
    axs[0].grid(alpha=0.3)
    for dt, col in [(100, "#1f78b4"), (200, "#e31a1c")]:
        d = b[(b.offset_ms == dt) & (b.method == "uncomp")]
        axs[1].plot(d.decel_mps2, d.ratio_nominal, "o-", color=col, label=f"|bias|/(v0*dt), offset {dt} ms")
        axs[1].plot(d.decel_mps2, d.ratio_inst, "s--", color=col, label=f"|bias|/(v(t)*dt), offset {dt} ms")
    axs[1].axhline(1.0, color="gray", lw=1)
    axs[1].set_xlabel("Gia toc phanh cua vat the (m/s^2)")
    axs[1].set_ylabel("Ti so |bias| / (toc do x dt) (khong don vi)")
    axs[1].set_title("Cong thuc v*dt: toc do danh dinh vs tuc thoi")
    axs[1].legend(fontsize=7)
    axs[1].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(RES, "failure_braking.png"), dpi=140)
    plt.close(fig)

    # 4. timeline offset 200 ms, phanh 6 m/s^2, 1 trial
    dt_ms, a = 200, 6.0
    dt_s = dt_ms / 1000.0
    tk = np.arange(N_FRAMES) * H
    s_true, _ = arc_and_speed(tk, BRAKE_V0, a, BRAKE_ONSET)
    s_meas, _ = arc_and_speed(tk - dt_s, BRAKE_V0, a, BRAKE_ONSET)
    z = (s_meas[:, None] * U[None] + noise[0])
    est_cv = np.full_like(z, np.nan)
    est_cv[4:] = estimate(z[None], 5, 1, dt_s)[0]
    est_ca = np.full_like(z, np.nan)
    est_ca[4:] = estimate(z[None], 5, 2, dt_s)[0]
    proj = lambda p: p @ U
    fig, axs = plt.subplots(2, 1, figsize=(9, 7), gridspec_kw={"height_ratios": [1, 2]})
    ax = axs[0]
    k0 = np.arange(40, 60)
    ax.eventplot([tk[k0]], lineoffsets=[2], linelengths=0.6, colors="#1f78b4")
    ax.eventplot([tk[k0]], lineoffsets=[1], linelengths=0.6, colors="#e31a1c")
    ax.eventplot([tk[k0] - dt_s], lineoffsets=[0], linelengths=0.6, colors="#555555")
    for t in tk[k0][:4]:
        ax.annotate("", xy=(t, 0.75), xytext=(t - dt_s, 0.25),
                    arrowprops=dict(arrowstyle="->", color="#999999", lw=0.8))
    ax.set_yticks([2, 1, 0])
    ax.set_yticklabels(["Camera: dau thoi gian", "LiDAR: dau thoi gian", "LiDAR: thoi diem do that"], fontsize=8)
    ax.set_xlim(3.9, 6.0)
    ax.set_xlabel("Thoi gian (s)")
    ax.set_title(f"Timeline: LiDAR lech {dt_ms} ms (mui ten: mau do som {dt_ms} ms nhung mang dau thoi gian muon)")
    ax = axs[1]
    ax.plot(tk, proj(np.c_[s_true * U[0], s_true * U[1]]), "k-", lw=2, label="Vi tri that")
    ax.plot(tk, proj(z), "o", ms=3, color="#e31a1c", label="LiDAR khong bu (tre 200 ms + nhieu)")
    ax.plot(tk, proj(est_cv), "s", ms=3, color="#1b9e77", label="bu comp_cv (N=5)")
    ax.plot(tk, proj(est_ca), "^", ms=3, color="#7570b3", label="bu comp_ca (N=5)")
    ax.axvline(BRAKE_ONSET, color="gray", ls=":", label="bat dau phanh (6 m/s^2)")
    ax.set_xlim(3.9, 8.0)
    ax.set_ylim(s_true[39] - 2, s_true[80] + 4)
    ax.set_xlabel("Thoi gian (s)")
    ax.set_ylabel("Vi tri doc quy dao (m)")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(RES, "timeline_offset200ms.png"), dpi=140)
    plt.close(fig)


if __name__ == "__main__":
    main()
