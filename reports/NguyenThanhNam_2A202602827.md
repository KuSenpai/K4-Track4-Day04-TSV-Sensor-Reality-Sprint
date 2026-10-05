# Báo cáo thành viên 4 – vai trò: phân tích failure

Họ tên: Nguyễn Thành Nam · MSSV: 2A202602827 · Nhóm: TSV
Chủ đề T4 · xe ADAS · camera + LiDAR · dữ liệu **tổng hợp**. Bằng chứng chung của nhóm: [failure_case.md](../failure_case.md), [results/results.csv](../results/results.csv), [results/failure_braking.png](../results/failure_braking.png). Lệnh chạy chung: `python src/run_benchmark.py && python scripts/check_submission.py`.

## Problem

Công thức sai số ≈ v×Δt chỉ đúng khi tốc độ gần như không đổi. Phần mình lo là xem khi vật phanh gấp thì cái gì hỏng: bản thân công thức, hay bộ bù chuyển động dựa trên nó.

## Method

Kịch bản: v₀ = 20 m/s, phanh đều từ giây thứ 5 với a = 2/4/6/8 m/s² (thêm a = 0 để so), offset 50–200 ms, đánh giá trong khoảng 5–8 s. Nhóm so bốn bộ bù: comp_cv với N = 3/5/9 (khớp đường thẳng) và comp_ca với N = 5/9 (khớp bậc hai).

Lý do đoán bộ bù bị lệch: khớp đường thẳng trên N mẫu cho ra đúng vận tốc ở *giữa cửa sổ*, tức là chậm hơn hiện tại (N−1)h/2. Khi vật đang giảm tốc, vận tốc ước lượng bị cao hơn thật. Tính ra bias ổn định là ½·a·[(Δt + (N−1)h/2)² − h²(N²−1)/12].

## Benchmark

Nhóm đo được RMSE (m) sau bù ở a = 8 m/s² (Bảng C):

| a (m/s^2) | offset (ms) | khong bu | cv N=3 | cv N=5 | cv N=9 | ca N=5 | ca N=9 |
|---|---|---|---|---|---|---|---|
| 8 | 0 | 0.14 | 0.13 | 0.13 | 0.35 | 0.14 | 0.12 |
| 8 | 50 | 0.62 | 0.18 | 0.21 | 0.49 | 0.21 | 0.15 |
| 8 | 100 | 1.23 | 0.25 | 0.30 | 0.66 | 0.31 | 0.20 |
| 8 | 150 | 1.86 | 0.34 | 0.42 | 0.84 | 0.43 | 0.25 |
| 8 | 200 | 2.51 | 0.44 | 0.55 | 1.03 | 0.58 | 0.31 |

Để so sánh, khi tốc độ không đổi và offset 200 ms thì cv N=3 là 0.32 m, cv N=5 là 0.19 m, cv N=9 là 0.12 m, ca N=5 là 0.57 m, ca N=9 là 0.27 m.

## Failure case

Nhóm đo được (offset 200 ms, a = 8): comp_cv N=5 còn sai 0.55 m, bias dọc quỹ đạo +0.49 m (ước lượng nằm *trước* vị trí thật). Bias ổn định khớp công thức ở trên (Bảng D, a = 8):

| a (m/s^2) | offset (ms) | cv N=5 đo (ổn định) | cv N=5 công thức | cv N=9 đo | cv N=9 công thức |
|---|---|---|---|---|---|
| 8 | 100 | 0.28 | 0.28 | 0.73 | 0.73 |
| 8 | 200 | 0.56 | 0.56 | 1.17 | 1.17 |

- Cửa sổ dài hơn thì tốt khi tốc độ không đổi (0.12 m) nhưng tệ hơn khi phanh (1.03 m so với 0.55 m của N=5), đúng hướng mà công thức dự đoán.
- **Giả thuyết** (mới chỉ kiểm trong mô phỏng): tracker thật có bộ lọc làm mượt cũng sẽ bị ước lượng vận tốc chậm pha như vậy.
- Tỉ lệ khung sai số vượt 0.5 m sau bù (Bảng F, offset 200 ms): 0.1% khi a = 0, và 59.1% khi a = 8.
- Cách cải thiện đã thử: N=3 xuống còn 0.44 m; comp_ca N=9 xuống 0.31 m nhưng kém hơn khi tốc độ không đổi (0.27 m so với 0.12 m của comp_cv N=9). Hướng fallback: phát hiện gia tốc rồi đổi bộ bù hoặc nới cổng gán. Ngưỡng để đổi thì **chưa xác định**.

## Engineering decision

- Nhóm chọn failure "phanh gấp + bộ bù vận tốc không đổi" vì nó đúng giả định đề nêu, kiểm được bằng công thức giải tích, và kết quả không hiển nhiên: công thức vẫn đúng với v(t), chính bộ bù mới hỏng.
- Không dùng comp_ca làm mặc định, vì C5 sai ở N=5 (khớp bậc hai làm nhiễu to lên). Chỉ nên bật khi phát hiện có gia tốc.
- Khi pitch phải nói rõ hạn chế: dữ liệu tổng hợp, Δt biết chính xác, và các khung sau khi vật dừng bị loại.
