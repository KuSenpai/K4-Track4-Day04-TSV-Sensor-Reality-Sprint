# Báo cáo thành viên 4 – vai trò: phân tích failure

Họ tên: [CHƯA ĐIỀN: Họ tên TV4] · MSSV: [CHƯA ĐIỀN: MSSV TV4] · Nhóm: TSV
Chủ đề T4 · xe ADAS · camera + LiDAR · dữ liệu **tổng hợp**. Bằng chứng chung: [failure_case.md](../failure_case.md), [results/results.csv](../results/results.csv), [results/failure_braking.png](../results/failure_braking.png). Lệnh chạy chung: `python src/run_benchmark.py && python scripts/check_submission.py`.

## Problem

Công thức sai số ≈ v×Δt chỉ đúng khi tốc độ gần không đổi. Tôi phân tích điều gì hỏng khi vật phanh gấp: công thức, hay bộ bù chuyển động dựa trên nó.

## Method

Kịch bản: v₀ = 20 m/s, phanh đều từ t = 5 s với a = 2/4/6/8 m/s² (cùng a = 0 làm đối chứng), offset 50–200 ms, cửa sổ đánh giá 5–8 s. So bốn bộ bù: comp_cv N = 3/5/9 (hồi quy tuyến tính) và comp_ca N = 5/9 (hồi quy bậc hai). Suy luận giải tích: hồi quy tuyến tính trên N mẫu đúng cho vận tốc giữa cửa sổ nên chậm (N−1)h/2; bias ổn định = ½·a·[(Δt + (N−1)h/2)² − h²(N²−1)/12].

## Benchmark

Nhóm quan sát được, RMSE (m) sau bù ở a = 8 m/s² (Bảng C):

| a (m/s^2) | offset (ms) | khong bu | cv N=3 | cv N=5 | cv N=9 | ca N=5 | ca N=9 |
|---|---|---|---|---|---|---|---|
| 8 | 0 | 0.14 | 0.13 | 0.13 | 0.35 | 0.14 | 0.12 |
| 8 | 50 | 0.62 | 0.18 | 0.21 | 0.49 | 0.21 | 0.15 |
| 8 | 100 | 1.23 | 0.25 | 0.30 | 0.66 | 0.31 | 0.20 |
| 8 | 150 | 1.86 | 0.34 | 0.42 | 0.84 | 0.43 | 0.25 |
| 8 | 200 | 2.51 | 0.44 | 0.55 | 1.03 | 0.58 | 0.31 |

Đối chiếu với tốc độ không đổi, offset 200 ms: cv N=3 0.32 m, cv N=5 0.19 m, cv N=9 0.12 m, ca N=5 0.57 m, ca N=9 0.27 m.

## Failure case

Nhóm quan sát được (offset 200 ms, a = 8): comp_cv N=5 còn sai 0.55 m; bias dọc quỹ đạo +0.49 m (ước lượng nằm trước vị trí thật). Bias ổn định khớp công thức giải tích (Bảng D, a = 8):

| a (m/s^2) | offset (ms) | cv N=5 đo (ổn định) | cv N=5 công thức | cv N=9 đo | cv N=9 công thức |
|---|---|---|---|---|---|
| 8 | 100 | 0.28 | 0.28 | 0.73 | 0.73 |
| 8 | 200 | 0.56 | 0.56 | 1.17 | 1.17 |

- Nhóm quan sát được: cửa sổ dài hơn tốt khi tốc độ không đổi (0.12 m) nhưng tệ hơn khi phanh (1.03 m so với 0.55 m của N=5) – đúng hướng công thức.
- **Giả thuyết** (chưa kiểm chứng ngoài mô phỏng): tracker thật có bộ lọc làm mượt cũng chịu hiện tượng ước lượng vận tốc chậm pha.
- Tỉ lệ khung vượt 0.5 m sau bù (Bảng F, offset 200 ms): 0.1% khi a = 0 và 59.1% khi a = 8.
- Cải tiến thử: N=3 giảm sai số xuống 0.44 m; comp_ca N=9 xuống 0.31 m nhưng kém hơn khi tốc độ không đổi (0.27 m so với 0.12 m của comp_cv N=9). Fallback đề xuất: phát hiện gia tốc rồi chuyển bộ bù/nới cổng; ngưỡng chuyển **chưa xác định**.

## Engineering decision

- Chọn failure case "phanh gấp + bộ bù vận tốc không đổi" vì (a) nằm đúng giả định đề nêu, (b) cho phép kiểm bằng công thức giải tích, (c) cho kết quả không hiển nhiên (công thức đúng với v(t), bộ bù mới hỏng).
- Không chọn comp_ca làm giải pháp mặc định: C5 sai ở N=5 do khuếch đại nhiễu; chỉ nên bật khi phát hiện gia tốc.
- Limitation phải nói khi pitch: dữ liệu tổng hợp, Δt biết chính xác, khung sau khi vật dừng bị loại.
