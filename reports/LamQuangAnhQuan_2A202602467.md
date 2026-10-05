# Báo cáo thành viên 1 – vai trò: đọc nguồn

Họ tên: Lâm Quang Anh Quân · MSSV: 2A202602467 · Nhóm: TSV
Chủ đề T4 · xe ADAS · camera + LiDAR · dữ liệu **tổng hợp**. Bằng chứng chung: [results/results.csv](../results/results.csv), [results/summary_tables.md](../results/summary_tables.md), [SOURCES.md](../SOURCES.md). Lệnh chạy chung: `python src/run_benchmark.py && python scripts/check_submission.py`.

## Problem

Camera và LiDAR chạy theo đồng hồ riêng. Nếu mẫu LiDAR mang dấu thời gian muộn hơn lúc đo thật một khoảng Δt, vật chuyển động với tốc độ v sẽ bị đặt sai chỗ khoảng v×Δt khi ghép với khung camera. Câu hỏi của nhóm: Δt = 50–200 ms gây sai số vị trí bao nhiêu trong tình huống xe ADAS, và giả định "tốc độ gần không đổi" hỏng khi nào?

Phần đọc nguồn của tôi (mức đọc ghi đầy đủ trong SOURCES.md):
- **Paper/repo cho biết** (Nowicki, arXiv:2006.16081v2, đọc qua WebFetch bản HTML): lệch thời gian camera–LiDAR được ước lượng chung với phép biến đổi 6-DOF; giả định offset "nhỏ và xấp xỉ không đổi"; yêu cầu camera global-shutter.
- **Paper/repo cho biết** (Wang et al., arXiv:2207.10454, **chỉ đọc abstract**): bài toán hiệu chuẩn thời gian + không gian online cho camera–LiDAR, đánh giá trên KITTI. Phần thân bài chưa đọc (PDF không giải mã được), nên limitation của bài này là "chưa xác minh".
- Các nguồn gợi ý của đề (S5, S7, S9) **chưa đọc**, không dùng.

## Method

Nhóm không tái hiện thuật toán của paper nào. Nhóm làm benchmark mô phỏng riêng:
- Mẫu LiDAR mang dấu thời gian `t_k` nhưng đo vật tại `t_k − Δt`; camera là mốc chuẩn.
- Sai số không bù = khoảng cách giữa vị trí LiDAR và vị trí thật tại `t_k`; kỳ vọng dọc quỹ đạo ≈ −v×Δt.
- Bù chuyển động: khớp vận tốc từ N = 5 mẫu gần nhất rồi ngoại suy thêm Δt (giả định Δt đã biết – gần với kịch bản mà paper của Nowicki ước lượng Δt như một hằng số, nhưng nhóm không dùng thuật toán đó).
- Lưu ý ranh giới: nhóm **không** so số của mình với số của paper (khác dữ liệu, khác metric).

## Benchmark

Nhóm quan sát được (dữ liệu tổng hợp, v = 20 m/s, tốc độ không đổi, σ = 0.10 m, 200 lượt, seed 42):

| v (m/s) | offset (ms) | v*dt (m) | \|bias\| (m) | \|bias\|/(v*dt) | RMSE khong bu (m) | RMSE bu (m) | giam RMSE (%) |
|---|---|---|---|---|---|---|---|
| 20 | 50 | 1.00 | 1.00 | 1.000 | 1.01 | 0.13 | 87.2 |
| 20 | 100 | 2.00 | 2.00 | 1.000 | 2.00 | 0.15 | 92.6 |
| 20 | 150 | 3.00 | 3.00 | 1.000 | 3.00 | 0.17 | 94.4 |
| 20 | 200 | 4.00 | 4.00 | 1.000 | 4.00 | 0.19 | 95.2 |

Plot: [results/error_vs_offset.png](../results/error_vs_offset.png). Nhóm quan sát được rằng sai số đo khớp v×Δt (tỉ số 1.000), phù hợp với giả định offset hằng số mà nguồn 1 nêu.

## Failure case

Nguồn 1 nêu giả định offset "xấp xỉ không đổi" và camera global-shutter; nhóm suy ra (**giả thuyết**) rằng khi vật gia tốc thì vấn đề không nằm ở offset mà ở bộ bù vận tốc. Nhóm quan sát được: khi vật phanh a = 8 m/s² ở offset 200 ms, RMSE sau bù là 0.55 m so với 0.19 m khi tốc độ không đổi (Bảng C, [failure_case.md](../failure_case.md)). Điều này **không** được nguồn nào xác nhận; đó là kết quả mô phỏng của nhóm.

## Engineering decision

Vì chưa có truy cập toàn văn các paper và không có dữ liệu thật, tôi đề xuất (và nhóm đồng ý): dùng benchmark mô phỏng có tham số công khai, ghi "chưa xác minh" cho mọi nội dung chưa đọc, và không trích số của paper vào bảng kết quả. Việc cần làm vòng sau: đọc toàn văn arXiv:2207.10454 và ít nhất một nguồn về rolling shutter (S9) trước khi làm phần mở rộng.
