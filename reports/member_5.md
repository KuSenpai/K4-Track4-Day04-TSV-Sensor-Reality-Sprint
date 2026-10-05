# Báo cáo thành viên 5 – vai trò: trình bày

Họ tên: [CHƯA ĐIỀN: Họ tên TV5] · MSSV: [CHƯA ĐIỀN: MSSV TV5] · Nhóm: TSV
Chủ đề T4 · xe ADAS · camera + LiDAR · dữ liệu **tổng hợp**. Bằng chứng chung: [pitch/pitch_script.md](../pitch/pitch_script.md), [results/summary_tables.md](../results/summary_tables.md), [results/timeline_offset200ms.png](../results/timeline_offset200ms.png). Lệnh chạy chung: `python src/run_benchmark.py && python scripts/check_submission.py`.

## Problem

Trên xe ADAS, nếu LiDAR trễ so với camera thì vật chạy nhanh bị đặt sai chỗ khi fusion. Thông điệp 20 giây đầu pitch: "LiDAR trễ 100 ms, xe mục tiêu 20 m/s ⇒ vị trí lệch 2.00 m – lớn hơn cả ngưỡng 0.5 m nhóm đặt ra."

## Method

Nói ngắn: mô phỏng vật chuyển động, cho LiDAR lệch 50/100/150/200 ms, đo sai số trước và sau khi bù bằng vận tốc ước lượng; đối chiếu với v×Δt; thêm kịch bản phanh gấp để phá giả định tốc độ không đổi. Dùng ảnh [results/timeline_offset200ms.png](../results/timeline_offset200ms.png) để minh họa: mẫu LiDAR được đo sớm 200 ms nhưng mang dấu thời gian muộn, nên đường chấm đỏ nằm sau đường vị trí thật.

## Benchmark

Nhóm quan sát được (dữ liệu tổng hợp), Bảng A trích:

| v (m/s) | offset (ms) | v*dt (m) | \|bias\| (m) | \|bias\|/(v*dt) | RMSE khong bu (m) | RMSE bu (m) | giam RMSE (%) |
|---|---|---|---|---|---|---|---|
| 10 | 100 | 1.00 | 1.00 | 1.000 | 1.01 | 0.15 | 85.2 |
| 20 | 100 | 2.00 | 2.00 | 1.000 | 2.00 | 0.15 | 92.6 |
| 30 | 100 | 3.00 | 3.00 | 1.000 | 3.00 | 0.15 | 95.0 |

Tốc độ nguy hiểm với ngưỡng 0.5 m: 10.0 m/s (36 km/h) ở 50 ms, 5.0 m/s (18 km/h) ở 100 ms, 3.3 m/s (12 km/h) ở 150 ms, 2.5 m/s (9 km/h) ở 200 ms. Nghĩa là ngay cả xe chạy chậm cũng vượt ngưỡng nếu offset đủ lớn. Plot: [results/error_vs_offset.png](../results/error_vs_offset.png).

## Failure case

Câu chuyện: bù chuyển động giúp nhiều, nhưng khi xe phía trước phanh gấp (a = 8 m/s², offset 200 ms) sai số dư là 0.55 m và 59.1% khung vượt ngưỡng 0.5 m, so với 0.19 m và 0.1% khi tốc độ không đổi. Ảnh: [results/failure_braking.png](../results/failure_braking.png). Điểm bất ngờ để nói: công thức v×Δt vẫn đúng nếu dùng tốc độ tức thời (tỉ số 1.073); thứ hỏng là bộ bù ước lượng vận tốc chậm pha. Phải nói rõ đây là kết quả mô phỏng; **giả thuyết** rằng tracker thật cũng vậy chưa được kiểm.

## Engineering decision

Khuyến nghị (trong phạm vi đã đo, không khái quát hóa):
1. Ưu tiên giảm Δt tại gốc (đồng bộ phần cứng/ước lượng Δt) vì sai số tỉ lệ thuận với v×Δt.
2. Dùng bù chuyển động như lớp thứ hai: giảm RMSE tối thiểu 81.1% khi v×Δt ≥ 1 m.
3. Khi phát hiện gia tốc lớn: chuyển bộ bù hoặc nới cổng gán thay vì tin vị trí đã bù (comp_ca N=9 cho 0.31 m ở a = 8, offset 200 ms, nhưng kém hơn ở tốc độ không đổi).
Trade-off: cửa sổ dài giảm nhiễu nhưng tăng độ trễ ước lượng; mô hình bậc hai bắt được gia tốc nhưng khuếch đại nhiễu. Chưa làm: rolling-shutter, dữ liệu thật, lỗi ước lượng Δt.
