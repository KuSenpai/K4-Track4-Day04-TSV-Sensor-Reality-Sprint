# Báo cáo thành viên 5 – vai trò: trình bày

Họ tên: Trần Long Khánh · MSSV: 2A202602538 · Nhóm: TSV
Chủ đề T4 · xe ADAS · camera + LiDAR · dữ liệu **tổng hợp**. Bằng chứng chung của nhóm: [pitch/pitch_script.md](../pitch/pitch_script.md), [results/summary_tables.md](../results/summary_tables.md), [results/timeline_offset200ms.png](../results/timeline_offset200ms.png). Lệnh chạy chung: `python src/run_benchmark.py && python scripts/check_submission.py`.

## Problem

Trên xe ADAS, nếu LiDAR bị trễ so với camera thì vật chạy nhanh sẽ bị đặt sai chỗ khi ghép dữ liệu. Câu mở đầu của bài pitch: "LiDAR trễ 100 ms, xe phía trước chạy 20 m/s thì vị trí lệch 2.00 m, lớn hơn nhiều so với ngưỡng 0.5 m nhóm đặt ra."

## Method

Tóm tắt khi nói: nhóm mô phỏng một vật chuyển động, cho LiDAR lệch 50/100/150/200 ms, đo sai số trước và sau khi bù bằng vận tốc ước lượng, rồi so với v×Δt. Sau đó thêm kịch bản phanh gấp để làm hỏng giả định tốc độ không đổi. Hình minh họa là [results/timeline_offset200ms.png](../results/timeline_offset200ms.png): mẫu LiDAR được đo sớm 200 ms nhưng mang nhãn giờ muộn, nên đường chấm đỏ nằm sau đường vị trí thật.

## Benchmark

Nhóm đo được (dữ liệu tổng hợp), trích Bảng A:

| v (m/s) | offset (ms) | v*dt (m) | \|bias\| (m) | \|bias\|/(v*dt) | RMSE khong bu (m) | RMSE bu (m) | giam RMSE (%) |
|---|---|---|---|---|---|---|---|
| 10 | 100 | 1.00 | 1.00 | 1.000 | 1.01 | 0.15 | 85.2 |
| 20 | 100 | 2.00 | 2.00 | 1.000 | 2.00 | 0.15 | 92.6 |
| 30 | 100 | 3.00 | 3.00 | 1.000 | 3.00 | 0.15 | 95.0 |

Với ngưỡng 0.5 m, tốc độ bắt đầu nguy hiểm là 10.0 m/s (36 km/h) ở offset 50 ms, 5.0 m/s (18 km/h) ở 100 ms, 3.3 m/s (12 km/h) ở 150 ms và 2.5 m/s (9 km/h) ở 200 ms. Tức là offset đủ lớn thì xe chạy chậm cũng vượt ngưỡng. Hình: [results/error_vs_offset.png](../results/error_vs_offset.png).

## Failure case

Ý chính để kể: bù chuyển động giúp được nhiều, nhưng khi xe phía trước phanh gấp (a = 8 m/s², offset 200 ms) thì sai số còn lại là 0.55 m và 59.1% khung vượt ngưỡng 0.5 m, trong khi lúc tốc độ không đổi chỉ là 0.19 m và 0.1%. Hình: [results/failure_braking.png](../results/failure_braking.png).

Điểm hơi bất ngờ: công thức v×Δt vẫn đúng nếu dùng tốc độ tức thời (tỉ số 1.073). Cái hỏng là bộ bù, vì nó ước lượng vận tốc chậm pha. Cần nói rõ đây là kết quả mô phỏng; việc tracker thật cũng bị như vậy chỉ là **giả thuyết**, nhóm chưa kiểm.

## Engineering decision

Khuyến nghị, chỉ trong phạm vi đã đo:
1. Giảm Δt ngay từ gốc (đồng bộ phần cứng hoặc ước lượng Δt), vì sai số tỉ lệ thuận với v×Δt.
2. Dùng bù chuyển động như lớp thứ hai: giảm RMSE ít nhất 81.1% khi v×Δt ≥ 1 m.
3. Khi phát hiện gia tốc lớn thì đổi bộ bù hoặc nới cổng gán thay vì tin vị trí đã bù (comp_ca N=9 cho 0.31 m ở a = 8, offset 200 ms, nhưng kém hơn khi tốc độ không đổi).

Đánh đổi: cửa sổ dài giảm nhiễu nhưng ước lượng chậm hơn; mô hình bậc hai bắt được gia tốc nhưng khuếch đại nhiễu. Nhóm chưa làm rolling shutter, dữ liệu thật và lỗi ước lượng Δt.
