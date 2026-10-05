# Kịch bản pitch – T4: LiDAR trễ bao nhiêu thì xe "nhìn nhầm chỗ"?

Tổng thời lượng: **4 phút 30 giây** (trong khoảng 3–5 phút của đề; **chưa diễn tập bấm giờ thật** – cả nhóm nên đọc thử một lần). Người trình bày: Trần Long Khánh cùng cả nhóm TSV. Mọi số lấy từ [results/summary_tables.md](../results/summary_tables.md); dữ liệu là **tổng hợp** (mô phỏng của nhóm).

| Phần | Thời lượng | Hình/Bảng đi kèm |
|---|---|---|
| 1. Problem | 0:45 | [results/timeline_offset200ms.png](../results/timeline_offset200ms.png) |
| 2. Method | 1:00 | công thức trên slide |
| 3. Benchmark | 1:00 | [results/error_vs_offset.png](../results/error_vs_offset.png), [results/comp_vs_uncomp.png](../results/comp_vs_uncomp.png) |
| 4. Failure | 1:00 | [results/failure_braking.png](../results/failure_braking.png) |
| 5. Decision | 0:45 | bảng khuyến nghị |

## 1. Problem (0:45)

"Xe ADAS ghép camera và LiDAR. Nếu mẫu LiDAR mang dấu thời gian trễ hơn lúc đo thật 100 ms, và xe phía trước chạy 20 m/s, thì khi ghép vị trí bị lệch 2.00 m. Ngưỡng nhóm em đặt là 0.5 m – tức đã vượt xa. Câu hỏi của nhóm: lệch 50 đến 200 ms thì sai bao nhiêu, bù được bao nhiêu, và khi nào cách bù hỏng?" Chỉ vào timeline: mẫu LiDAR đo sớm 200 ms nhưng mang dấu thời gian muộn.

## 2. Method (1:00)

"Đây là dữ liệu tổng hợp do nhóm mô phỏng: vật chạy thẳng, 10 Hz, nhiễu đo 0.10 m, 200 lượt, seed 42. Baseline là offset 0 ms; điều kiện lỗi là 50, 100, 150, 200 ms. Ba cách xử lý: không bù; bù tuyến tính – ước lượng vận tốc từ 5 khung gần nhất rồi cộng vận tốc nhân Δt; bù bậc hai – thêm gia tốc. Công thức cần kiểm: sai số ≈ v nhân Δt. Nhóm không tái hiện thuật toán của paper nào; paper của Nowicki chỉ cho bối cảnh rằng offset thường được coi là nhỏ và gần không đổi."

## 3. Benchmark (1:00)

"Nhóm quan sát được: sai số dọc quỹ đạo không bù khớp v nhân Δt, tỉ số từ 0.999 đến 1.000 ở 16 cấu hình. Ví dụ 20 m/s, 200 ms: 4.00 m. Sau khi bù, RMSE chỉ còn 0.19 m, giảm 95.2%. Với cấu hình có v nhân Δt từ 1 m trở lên, bù giảm ít nhất 81.1%. Ở xe chậm 5 m/s và 50 ms, chỉ giảm 55.1% vì sai số nhỏ gần sàn nhiễu 0.14 m. Với ngưỡng 0.5 m, tốc độ nguy hiểm là 10.0 m/s ở 50 ms, 5.0 m/s ở 100 ms, và 2.5 m/s ở 200 ms."

## 4. Failure (1:00)

"Failure case: xe phía trước phanh gấp 8 m/s², offset 200 ms. Công thức v nhân Δt với tốc độ ban đầu cho 4.00 m nhưng sai số không bù đo được 2.23 m. Điều bất ngờ: dùng tốc độ tức thời thì công thức vẫn đúng, tỉ số 1.073. Cái hỏng là bộ bù: nó ước lượng vận tốc chậm pha, nên đẩy vị trí quá xa. Sai số dư lên 0.55 m so với 0.19 m khi tốc độ không đổi, và 59.1% khung vượt 0.5 m. Công thức giải tích của nhóm giải thích đúng độ lệch này trong mô phỏng. Giả thuyết là tracker thật cũng gặp tương tự – nhóm chưa kiểm chứng. Một kỳ vọng của nhóm đã sai: mô hình gia tốc N=5 không tốt hơn mô hình tuyến tính vì khuếch đại nhiễu."

## 5. Decision (0:45)

"Quyết định: một, giảm Δt tại gốc vì sai số tỉ lệ với Δt; hai, giữ bù chuyển động như lớp thứ hai; ba, khi phát hiện gia tốc thì chuyển sang bộ bù bậc hai với cửa sổ dài – 0.31 m ở cấu hình tệ nhất – hoặc nới cổng gán; ngưỡng chuyển nhóm chưa xác định. Giới hạn: dữ liệu tổng hợp, Δt biết chính xác, chưa có rolling-shutter hay dữ liệu thật. Vòng sau: lỗi ước lượng Δt, nhiều seed, dữ liệu thật."
