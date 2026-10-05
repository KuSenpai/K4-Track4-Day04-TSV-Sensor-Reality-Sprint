# Báo cáo thành viên 1 – vai trò: đọc nguồn

Họ tên: Lâm Quang Anh Quân · MSSV: 2A202602467 · Nhóm: TSV
Chủ đề T4 · xe ADAS · camera + LiDAR · dữ liệu **tổng hợp**. Bằng chứng chung của nhóm: [results/results.csv](../results/results.csv), [results/summary_tables.md](../results/summary_tables.md), [SOURCES.md](../SOURCES.md). Lệnh chạy chung: `python src/run_benchmark.py && python scripts/check_submission.py`.

## Problem

Camera và LiDAR chạy theo đồng hồ riêng. Nếu mẫu LiDAR bị gắn nhãn giờ trễ hơn lúc đo thật một khoảng Δt, thì khi ghép với ảnh camera, vật đang chạy tốc độ v sẽ bị đặt sai chỗ khoảng v×Δt. Nhóm muốn biết với Δt từ 50 đến 200 ms thì sai bao nhiêu trên xe ADAS, và khi nào giả định "tốc độ gần như không đổi" không còn đúng.

Phần mình lo là đọc nguồn. Mức đọc được ghi rõ trong SOURCES.md:
- **Paper cho biết** (Nowicki, arXiv:2006.16081v2, mình đọc bản HTML qua công cụ trích xuất): offset thời gian camera–LiDAR được ước lượng cùng lúc với phép biến đổi 6-DOF; paper giả định offset nhỏ và gần như không đổi, và cần camera global-shutter.
- **Paper cho biết** (Wang và cộng sự, arXiv:2207.10454): mình mới đọc abstract, chưa đọc được phần thân (file PDF không mở ra được), nên limitation của bài này là "chưa xác minh".
- Các nguồn gợi ý S5, S7, S9 của đề: chưa đọc, nên nhóm không dùng.

## Method

Nhóm không làm lại thuật toán của paper nào. Nhóm tự viết một mô phỏng nhỏ:
- Mẫu LiDAR mang nhãn giờ `t_k` nhưng thực ra đo vật tại `t_k − Δt`; camera được coi là mốc thời gian chuẩn.
- Sai số không bù là khoảng cách giữa vị trí LiDAR và vị trí thật tại `t_k`; dọc theo hướng chạy nó kỳ vọng bằng v×Δt.
- Bù chuyển động: ước lượng vận tốc từ N = 5 mẫu gần nhất rồi cộng thêm v̂×Δt. Mô phỏng cho biết trước Δt, giống tình huống đã hiệu chuẩn.
- Số của nhóm và số của paper là hai thứ khác nhau (khác dữ liệu, khác metric), nên báo cáo không đặt chúng cạnh nhau để so.

## Benchmark

Nhóm đo được (dữ liệu tổng hợp, v = 20 m/s, tốc độ không đổi, nhiễu 0.10 m, 200 lượt, seed 42):

| v (m/s) | offset (ms) | v*dt (m) | \|bias\| (m) | \|bias\|/(v*dt) | RMSE khong bu (m) | RMSE bu (m) | giam RMSE (%) |
|---|---|---|---|---|---|---|---|
| 20 | 50 | 1.00 | 1.00 | 1.000 | 1.01 | 0.13 | 87.2 |
| 20 | 100 | 2.00 | 2.00 | 1.000 | 2.00 | 0.15 | 92.6 |
| 20 | 150 | 3.00 | 3.00 | 1.000 | 3.00 | 0.17 | 94.4 |
| 20 | 200 | 4.00 | 4.00 | 1.000 | 4.00 | 0.19 | 95.2 |

Hình: [results/error_vs_offset.png](../results/error_vs_offset.png). Sai số đo được trùng với v×Δt (tỉ số 1.000), khớp với giả định offset không đổi mà paper của Nowicki nêu.

## Failure case

Paper của Nowicki giả định offset gần như không đổi. Từ đó nhóm đoán (**giả thuyết**) rằng khi vật gia tốc thì chỗ hỏng không phải là offset mà là bộ bù vận tốc. Trong mô phỏng, khi vật phanh 8 m/s² với offset 200 ms, sai số sau bù là 0.55 m, còn khi tốc độ không đổi là 0.19 m (xem [failure_case.md](../failure_case.md)). Kết quả này là của nhóm tự mô phỏng, không có nguồn nào xác nhận.

## Engineering decision

Vì chưa đọc được toàn văn các paper và không có dữ liệu thật, nhóm chọn: dùng mô phỏng với tham số ghi rõ, ghi "chưa xác minh" cho những gì chưa đọc, và không đưa số của paper vào bảng kết quả. Việc nên làm tiếp: đọc toàn văn arXiv:2207.10454 và một bài về rolling shutter (S9) trước khi thử phần mở rộng.
