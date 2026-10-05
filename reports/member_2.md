# Báo cáo thành viên 2 – vai trò: chạy code

Họ tên: [CHƯA ĐIỀN: Họ tên TV2] · MSSV: [CHƯA ĐIỀN: MSSV TV2] · Nhóm: TSV
Chủ đề T4 · xe ADAS · camera + LiDAR · dữ liệu **tổng hợp**. Bằng chứng chung: [results/results.csv](../results/results.csv), [results/run_log.txt](../results/run_log.txt), [src/run_benchmark.py](../src/run_benchmark.py). Lệnh chạy chung: `python src/run_benchmark.py && python scripts/check_submission.py`.

## Problem

Cần một benchmark có đối chứng, tái hiện được từ một dòng lệnh, đo sai số vị trí (m) khi LiDAR lệch 0/50/100/150/200 ms so với camera, có và không bù chuyển động, kèm một kịch bản vi phạm giả định tốc độ không đổi. Vai trò của tôi: bảo đảm code chạy đúng, cùng seed, cùng cách tính metric cho mọi điều kiện.

## Method

Luồng trong `src/run_benchmark.py` (entrypoint duy nhất, Python 3.11.7, numpy 2.4.6, pandas 3.0.5, matplotlib 3.11.2):
1. Sinh **một** mảng nhiễu Gauss (200 lượt × 100 khung × 2 trục, σ = 0.10 m, seed 42) và dùng lại cho mọi điều kiện (common random numbers) để chênh lệch giữa điều kiện chỉ do điều kiện, không do nhiễu.
2. `position(t)` cho quỹ đạo thật (thẳng, 15°; tốc độ không đổi hoặc phanh đều từ t = 5 s).
3. Mẫu LiDAR `z_k = p(t_k − Δt) + nhiễu`. Ba bộ ước lượng: `uncomp` (dùng thẳng), `comp_cv` (khớp tuyến tính LSQ trên N khung, ngoại suy thêm Δt), `comp_ca` (khớp bậc hai).
4. Metric cùng một hàm cho mọi điều kiện: RMSE, mean, p95, tỉ lệ khung > 0.5 m, bias dọc quỹ đạo có dấu, tỉ số |bias|/(v×Δt), % giảm RMSE. Chỉ tính khung t ≥ 1 s (tốc độ không đổi) hoặc t ∈ [5, 8] s (phanh) và vật còn chạy.
5. Ghi CSV, bảng markdown, 4 PNG, log.

## Benchmark

Lệnh đã chạy: `python src/run_benchmark.py` → exit code 0, 190 dòng trong [results/results.csv](../results/results.csv); log ở [results/run_log.txt](../results/run_log.txt). Kiểm tra tự động bằng `python scripts/check_submission.py`.

Nhóm quan sát được (baseline đồng bộ 0 ms, mọi tốc độ): RMSE không bù 0.14 m, sau bù N=5 là 0.11 m – đây là sàn nhiễu của mô phỏng. Một dòng kết quả mẫu:

| v (m/s) | offset (ms) | v*dt (m) | \|bias\| (m) | \|bias\|/(v*dt) | RMSE khong bu (m) | RMSE bu (m) | giam RMSE (%) |
|---|---|---|---|---|---|---|---|
| 10 | 100 | 1.00 | 1.00 | 1.000 | 1.01 | 0.15 | 85.2 |

Plot: [results/comp_vs_uncomp.png](../results/comp_vs_uncomp.png).

## Failure case

Kịch bản trong code: `position()` với `a > 0` – vật chạy 20 m/s, phanh đều từ t = 5 s. Nhóm quan sát được ở offset 200 ms, comp_cv N=5: RMSE tăng 0.19 → 0.23 → 0.32 → 0.44 → 0.55 m khi a = 0 → 2 → 4 → 6 → 8 m/s². Tôi đã kiểm tra thêm một đối chiếu giải tích: bias ổn định đo được khớp công thức ½·a·[(Δt + (N−1)h/2)² − h²(N²−1)/12] (a = 8, offset 200 ms, N=5: đo 0.56 m, công thức 0.56 m) – xem [results/summary_tables.md](../results/summary_tables.md) Bảng D. Đây là kiểm tra mã mô phỏng khớp với suy luận, không phải bằng chứng về dữ liệu thật.

## Engineering decision

- Một entrypoint, một seed, mảng nhiễu dùng chung → so sánh công bằng giữa điều kiện.
- Chỉ dùng numpy/pandas/matplotlib (không thêm dependency).
- Bảng markdown được sinh từ CSV bởi chính entrypoint và `scripts/check_submission.py` kiểm số trong báo cáo so với bảng đó, để số trong báo cáo không thể lệch khỏi lần chạy thật.
- Đánh đổi chấp nhận: 1 seed × 200 lượt (chạy vài giây) thay vì nhiều seed; biến thiên giữa seed chưa đo.
