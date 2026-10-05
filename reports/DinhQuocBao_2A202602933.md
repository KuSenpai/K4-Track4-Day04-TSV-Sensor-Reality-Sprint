# Báo cáo thành viên 3 – vai trò: ghi benchmark

Họ tên: Đinh Quốc Bảo · MSSV: 2A202602933 · Nhóm: TSV
Chủ đề T4 · xe ADAS · camera + LiDAR · dữ liệu **tổng hợp**. Bằng chứng chung của nhóm: [results/results.csv](../results/results.csv), [results/summary_tables.md](../results/summary_tables.md), [design/benchmark_design.md](../design/benchmark_design.md). Lệnh chạy chung: `python src/run_benchmark.py && python scripts/check_submission.py`.

## Problem

Ghi lại benchmark cho trung thực: claim viết **trước** khi chạy, số điền vào **sau** khi chạy, và claim nào sai thì ghi là sai.  Giữ bảng Bước 1 và Bước 3 trong file thiết kế và đối chiếu số trong đó với file CSV.

## Method

Các điều kiện đã đo:

- Offset LiDAR: 0/50/100/150/200 ms.
- Tốc độ không đổi: 5/10/20/30 m/s.
- Kịch bản phanh: v₀ = 20 m/s, a = 0/2/4/6/8 m/s².

Metric: RMSE (m), bias dọc quỹ đạo (m), tỉ số |bias|/(v×Δt), % giảm RMSE sau bù, và tốc độ nguy hiểm v* = ngưỡng/Δt với ngưỡng 0.5 m (ngưỡng này do nhóm tự đặt). Mọi số lấy từ lần chạy seed 42.

## Benchmark

Nhóm đo được, tốc độ không đổi (trích Bảng A):

| v (m/s) | offset (ms) | v*dt (m) | \|bias\| (m) | \|bias\|/(v*dt) | RMSE khong bu (m) | RMSE bu (m) | giam RMSE (%) |
| ------- | ----------- | -------- | ------------ | --------------- | ----------------- | ----------- | ------------- |
| 5       | 50          | 0.25     | 0.25         | 0.999           | 0.29              | 0.13        | 55.1          |
| 5       | 200         | 1.00     | 1.00         | 1.000           | 1.01              | 0.19        | 81.1          |
| 10      | 100         | 1.00     | 1.00         | 1.000           | 1.01              | 0.15        | 85.2          |
| 30      | 200         | 6.00     | 6.00         | 1.000           | 6.00              | 0.19        | 96.8          |

Tốc độ nguy hiểm (Bảng E, suy từ công thức v×Δt đã kiểm): ngưỡng 0.5 m bị vượt từ 10.0 m/s ở 50 ms, 5.0 m/s ở 100 ms, 3.3 m/s ở 150 ms và 2.5 m/s ở 200 ms. Hình: [results/error_vs_offset.png](../results/error_vs_offset.png), [results/comp_vs_uncomp.png](../results/comp_vs_uncomp.png), timeline: [results/timeline_offset200ms.png](../results/timeline_offset200ms.png).

Kết quả kiểm từng claim (chi tiết trong file thiết kế):

- C1 đúng: tỉ số 0.999–1.000.
- C2 đúng trong phạm vi claim (v·Δt ≥ 1 m thì giảm ít nhất 81.1%). Ngoài phạm vi, ca 5 m/s, 50 ms chỉ giảm 55.1%.
- C3 đúng một phần: tính theo v₀ danh định thì tỉ số còn 0.853–0.529, nhưng tính theo v(t) vẫn là 1.003–1.073.
- C4 đúng: RMSE sau bù tăng đều theo |a|.
- **C5 sai với N=5**: comp_ca N=5 tệ hơn comp_cv N=5.

## Failure case

Nhóm đo được khi phanh a = 8 m/s² (Bảng B, không bù):

| a (m/s^2) | offset (ms) | v0*dt (m) | v(t)*dt TB (m) | \|bias\| (m) | ty so theo v0 | ty so theo v(t) | RMSE khong bu (m) |
| --------- | ----------- | --------- | -------------- | ------------ | ------------- | --------------- | ----------------- |
| 8         | 100         | 2.00      | 1.04           | 1.08         | 0.539         | 1.037           | 1.23              |
| 8         | 200         | 4.00      | 2.08           | 2.23         | 0.558         | 1.073           | 2.51              |

Công thức v×Δt dùng v₀ danh định thì lệch rõ, nhưng dùng tốc độ tức thời thì vẫn gần đúng (tỉ số 1.073). Nghĩa là claim C3 ban đầu của nhóm hơi đơn giản; mình ghi phát hiện này vào file thiết kế chứ không sửa lại claim. Chi tiết failure xem [failure_case.md](../failure_case.md).

## Engineering decision

- Báo cáo cả RMSE (có nhiễu) lẫn bias có dấu (nhiễu triệt tiêu), vì với v·Δt nhỏ thì RMSE bị mức nhiễu nền 0.14 m chi phối, còn bias vẫn khớp v×Δt rất sát.
- Ngưỡng 0.5 m là giả định của nhóm, nên ghi rõ như vậy và không viện dẫn nguồn nào.
- Khi thấy C5 sai, nhóm không đổi tham số hay metric cho đẹp mà chỉ ghi nhận.
