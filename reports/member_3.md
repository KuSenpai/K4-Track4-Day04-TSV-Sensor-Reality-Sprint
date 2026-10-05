# Báo cáo thành viên 3 – vai trò: ghi benchmark

Họ tên: [CHƯA ĐIỀN: Họ tên TV3] · MSSV: [CHƯA ĐIỀN: MSSV TV3] · Nhóm: TSV
Chủ đề T4 · xe ADAS · camera + LiDAR · dữ liệu **tổng hợp**. Bằng chứng chung: [results/results.csv](../results/results.csv), [results/summary_tables.md](../results/summary_tables.md), [design/benchmark_design.md](../design/benchmark_design.md). Lệnh chạy chung: `python src/run_benchmark.py && python scripts/check_submission.py`.

## Problem

Ghi lại benchmark một cách trung thực: claim viết **trước** khi chạy, số điền **sau** khi chạy, và nêu rõ claim nào sai. Vai trò của tôi là giữ bảng Bước 1/Bước 3 và đối chiếu số với CSV.

## Method

Điều kiện: offset LiDAR 0/50/100/150/200 ms; tốc độ không đổi 5/10/20/30 m/s; kịch bản phanh v₀ = 20 m/s với a = 0/2/4/6/8 m/s². Metric: RMSE (m), bias dọc quỹ đạo (m), tỉ số |bias|/(v×Δt), % giảm RMSE sau bù, tốc độ nguy hiểm v* = ngưỡng/Δt với ngưỡng 0.5 m (giả định của nhóm). Mọi số lấy từ lần chạy seed 42.

## Benchmark

Nhóm quan sát được, tốc độ không đổi (trích Bảng A):

| v (m/s) | offset (ms) | v*dt (m) | \|bias\| (m) | \|bias\|/(v*dt) | RMSE khong bu (m) | RMSE bu (m) | giam RMSE (%) |
|---|---|---|---|---|---|---|---|
| 5 | 50 | 0.25 | 0.25 | 0.999 | 0.29 | 0.13 | 55.1 |
| 5 | 200 | 1.00 | 1.00 | 1.000 | 1.01 | 0.19 | 81.1 |
| 10 | 100 | 1.00 | 1.00 | 1.000 | 1.01 | 0.15 | 85.2 |
| 30 | 200 | 6.00 | 6.00 | 1.000 | 6.00 | 0.19 | 96.8 |

Tốc độ nguy hiểm (Bảng E, suy từ công thức v×Δt đã kiểm): ngưỡng 0.5 m bị vượt từ 10.0 m/s ở 50 ms, 5.0 m/s ở 100 ms, 3.3 m/s ở 150 ms, 2.5 m/s ở 200 ms. Plot: [results/error_vs_offset.png](../results/error_vs_offset.png), [results/comp_vs_uncomp.png](../results/comp_vs_uncomp.png), timeline: [results/timeline_offset200ms.png](../results/timeline_offset200ms.png).

Kết quả kiểm claim (chi tiết trong design/benchmark_design.md):
- C1 đúng: tỉ số 0.999–1.000.
- C2 đúng trong phạm vi claim (v·Δt ≥ 1 m: giảm tối thiểu 81.1%); ngoài phạm vi (5 m/s, 50 ms) chỉ giảm 55.1%.
- C3 đúng một phần: theo v₀ danh định tỉ số còn 0.853–0.529, nhưng theo v(t) vẫn 1.003–1.073.
- C4 đúng: RMSE sau bù tăng đơn điệu theo |a|.
- **C5 sai với N=5**: comp_ca N=5 tệ hơn comp_cv N=5.

## Failure case

Nhóm quan sát được ở phanh a = 8 m/s² (Bảng B, không bù):

| a (m/s^2) | offset (ms) | v0*dt (m) | v(t)*dt TB (m) | \|bias\| (m) | ty so theo v0 | ty so theo v(t) | RMSE khong bu (m) |
|---|---|---|---|---|---|---|---|
| 8 | 100 | 2.00 | 1.04 | 1.08 | 0.539 | 1.037 | 1.23 |
| 8 | 200 | 4.00 | 2.08 | 2.23 | 0.558 | 1.073 | 2.51 |

Ghi nhận trung thực: công thức v×Δt với v₀ danh định lệch rõ, nhưng với tốc độ tức thời vẫn đúng gần như vậy (tỉ số 1.073). Claim C3 ban đầu của nhóm hơi ngây thơ; phát hiện này đã được ghi vào design thay vì sửa claim. Chi tiết failure: [failure_case.md](../failure_case.md).

## Engineering decision

- Chọn báo cáo cả RMSE (có nhiễu) lẫn bias có dấu (không nhiễu), vì RMSE ở v·Δt nhỏ bị sàn nhiễu 0.14 m chi phối còn bias thì khớp v×Δt chính xác.
- Chọn ngưỡng 0.5 m và gọi rõ là giả định; không viện dẫn nguồn.
- Không chỉnh tham số hay metric sau khi thấy C5 sai; chỉ ghi nhận.
