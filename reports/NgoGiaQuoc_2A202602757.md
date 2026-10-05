# Báo cáo thành viên 2 – vai trò: chạy code

Họ tên: Ngô Gia Quốc · MSSV: 2A202602757 · Nhóm: TSV
Chủ đề T4 · xe ADAS · camera + LiDAR · dữ liệu **tổng hợp**. Bằng chứng chung của nhóm: [results/results.csv](../results/results.csv), [results/run_log.txt](../results/run_log.txt), [src/run_benchmark.py](../src/run_benchmark.py). Lệnh chạy chung: `python src/run_benchmark.py && python scripts/check_submission.py`.

## Problem

Nhóm cần một benchmark chạy lại được chỉ bằng một dòng lệnh. Benchmark đo sai số vị trí (m) khi LiDAR lệch 0/50/100/150/200 ms so với camera, có bù và không bù chuyển động, cộng thêm một kịch bản làm hỏng giả định tốc độ không đổi. Phần mình lo là code: chạy đúng, cùng seed, và mọi điều kiện dùng chung một cách tính metric.

## Method

Code nằm trong `src/run_benchmark.py` (một file chạy duy nhất, Python 3.11.7, numpy 2.4.6, pandas 3.0.5, matplotlib 3.11.2). Các bước:
1. Sinh **một** mảng nhiễu Gauss (200 lượt × 100 khung × 2 trục, nhiễu 0.10 m, seed 42) rồi dùng lại cho mọi điều kiện. Nhờ vậy chênh lệch giữa các điều kiện chỉ do điều kiện, không phải do nhiễu may rủi.
2. Hàm `position(t)` cho quỹ đạo thật: đường thẳng 15°, tốc độ không đổi hoặc phanh đều từ giây thứ 5.
3. Mẫu LiDAR là vị trí thật tại `t_k − Δt` cộng nhiễu. Có ba cách xử lý: `uncomp` (dùng thẳng), `comp_cv` (khớp đường thẳng bằng bình phương tối thiểu trên N khung rồi ngoại suy thêm Δt), `comp_ca` (khớp bậc hai).
4. Metric tính bằng cùng một hàm cho mọi điều kiện: RMSE, mean, p95, tỉ lệ khung vượt 0.5 m, bias có dấu dọc quỹ đạo, tỉ số |bias|/(v×Δt), % giảm RMSE. Chỉ tính các khung từ giây thứ 1 trở đi (tốc độ không đổi) hoặc trong 5–8 s (phanh), và khi vật còn chạy.
5. Ghi CSV, bảng markdown, 4 ảnh PNG và log.

## Benchmark

Lệnh đã chạy: `python src/run_benchmark.py`, exit code 0, ra 190 dòng trong [results/results.csv](../results/results.csv). Log ở [results/run_log.txt](../results/run_log.txt). Chạy tiếp `python scripts/check_submission.py` để kiểm tra tự động.

Nhóm đo được: baseline đồng bộ 0 ms có RMSE không bù 0.14 m (mọi tốc độ), sau bù N=5 là 0.11 m. Đây là mức nhiễu nền của mô phỏng. Một dòng kết quả làm ví dụ:

| v (m/s) | offset (ms) | v*dt (m) | \|bias\| (m) | \|bias\|/(v*dt) | RMSE khong bu (m) | RMSE bu (m) | giam RMSE (%) |
|---|---|---|---|---|---|---|---|
| 10 | 100 | 1.00 | 1.00 | 1.000 | 1.01 | 0.15 | 85.2 |

Hình: [results/comp_vs_uncomp.png](../results/comp_vs_uncomp.png).

## Failure case

Trong code, kịch bản failure là `position()` với `a > 0`: vật chạy 20 m/s rồi phanh đều từ giây thứ 5. Với offset 200 ms và comp_cv N=5, sai số sau bù tăng 0.19 → 0.23 → 0.32 → 0.44 → 0.55 m khi a = 0 → 2 → 4 → 6 → 8 m/s².

Mình còn đối chiếu thêm với một công thức giải tích: ½·a·[(Δt + (N−1)h/2)² − h²(N²−1)/12]. Bias ổn định đo được khớp công thức này (a = 8, offset 200 ms, N=5: đo 0.56 m, công thức 0.56 m), xem Bảng D trong [results/summary_tables.md](../results/summary_tables.md). Việc này chỉ cho thấy code mô phỏng khớp với suy luận, không chứng minh gì về dữ liệu thật.

## Engineering decision

- Một file chạy, một seed, một mảng nhiễu dùng chung, để so sánh công bằng.
- Chỉ dùng numpy, pandas, matplotlib, không thêm thư viện nào khác.
- Bảng markdown do chính file chạy sinh ra từ CSV, và `scripts/check_submission.py` so số trong báo cáo với các bảng đó, nên số trong báo cáo không lệch khỏi lần chạy thật.
- Đánh đổi: mới chạy 1 seed × 200 lượt (mất vài giây) chứ chưa chạy nhiều seed, nên chưa biết kết quả dao động bao nhiêu giữa các seed.
