# Kịch bản pitch – T4: LiDAR trễ bao nhiêu thì xe "nhìn nhầm chỗ"?

Tổng thời lượng dự kiến: **4 phút 30 giây** (đề cho 3–5 phút). **Chưa bấm giờ thật**, cả nhóm nên đọc thử một lượt. Người trình bày: Trần Long Khánh, cả nhóm TSV hỗ trợ trả lời. Mọi số lấy từ [results/summary_tables.md](../results/summary_tables.md); dữ liệu là **tổng hợp** do nhóm tự mô phỏng. Slide: [TSV_T4_slide.pdf](TSV_T4_slide.pdf).

| Phần | Thời lượng | Hình/Bảng đi kèm |
|---|---|---|
| 1. Problem | 0:45 | [results/timeline_offset200ms.png](../results/timeline_offset200ms.png) |
| 2. Method | 1:00 | công thức trên slide |
| 3. Benchmark | 1:00 | [results/error_vs_offset.png](../results/error_vs_offset.png), [results/comp_vs_uncomp.png](../results/comp_vs_uncomp.png) |
| 4. Failure | 1:00 | [results/failure_braking.png](../results/failure_braking.png) |
| 5. Decision | 0:45 | bảng khuyến nghị |

## 1. Problem (0:45)

"Xe ADAS ghép dữ liệu camera với LiDAR. Giả sử mẫu LiDAR bị gắn nhãn giờ trễ 100 ms, mà xe phía trước đang chạy 20 m/s, thì khi ghép vị trí sẽ lệch 2.00 m. Nhóm em tự đặt ngưỡng chấp nhận là 0.5 m, nên mức này vượt khá xa. Câu hỏi của tụi em là: lệch từ 50 đến 200 ms thì sai bao nhiêu, bù được bao nhiêu, và khi nào cách bù không còn đúng?" Chỉ vào timeline: mẫu LiDAR được đo sớm 200 ms nhưng mang nhãn giờ muộn.

## 2. Method (1:00)

"Dữ liệu là do nhóm tự mô phỏng: một vật chạy thẳng, lấy mẫu 10 Hz, nhiễu đo 0.10 m, 200 lượt, seed 42. Baseline là offset 0 ms, còn điều kiện lỗi là 50, 100, 150 và 200 ms. Tụi em thử ba cách: không bù; bù tuyến tính, tức là ước lượng vận tốc từ 5 khung gần nhất rồi cộng vận tốc nhân Δt; và bù bậc hai có thêm gia tốc. Công thức cần kiểm là sai số xấp xỉ v nhân Δt. Nhóm không làm lại thuật toán của paper nào, bài của Nowicki chỉ cho tụi em biết người ta thường coi offset là nhỏ và gần như không đổi."

## 3. Benchmark (1:00)

"Kết quả đo được: sai số dọc quỹ đạo khi không bù khớp với v nhân Δt, tỉ số từ 0.999 đến 1.000 ở cả 16 cấu hình. Ví dụ 20 m/s, 200 ms thì lệch 4.00 m. Sau khi bù chỉ còn 0.19 m, giảm 95.2%. Với các cấu hình có v nhân Δt từ 1 m trở lên, bù giảm ít nhất 81.1%. Riêng xe chậm 5 m/s ở 50 ms thì chỉ giảm 55.1%, vì sai số ban đầu đã gần mức nhiễu nền 0.14 m. Với ngưỡng 0.5 m, tốc độ bắt đầu nguy hiểm là 10.0 m/s ở 50 ms, 5.0 m/s ở 100 ms và 2.5 m/s ở 200 ms."

## 4. Failure (1:00)

"Failure case của nhóm là xe phía trước phanh gấp 8 m/s² với offset 200 ms. Nếu lấy tốc độ ban đầu nhân Δt thì ra 4.00 m, nhưng sai số không bù đo được chỉ 2.23 m. Điều tụi em thấy bất ngờ là nếu dùng tốc độ tức thời thì công thức vẫn đúng, tỉ số 1.073. Cái bị hỏng là bộ bù: nó ước lượng vận tốc chậm hơn thực tế nên đẩy vị trí đi quá xa. Sai số còn lại lên 0.55 m, so với 0.19 m khi tốc độ không đổi, và có 59.1% khung vượt 0.5 m. Công thức giải tích của nhóm giải thích đúng độ lệch này trong mô phỏng. Còn việc tracker thật có bị như vậy không thì đây mới là giả thuyết, tụi em chưa kiểm. Thêm một điều nhóm đã đoán sai: bù bậc hai với 5 khung không tốt hơn bù tuyến tính, vì nó làm nhiễu to lên."

## 5. Decision (0:45)

"Từ đó nhóm đề xuất ba việc. Một, giảm Δt ngay từ gốc vì sai số tỉ lệ với Δt. Hai, giữ bù chuyển động như lớp bảo vệ thứ hai. Ba, khi phát hiện xe đang gia tốc thì chuyển sang bù bậc hai với cửa sổ dài, ra 0.31 m ở trường hợp xấu nhất, hoặc nới cổng gán; ngưỡng để chuyển thì tụi em chưa xác định. Hạn chế của nhóm: dữ liệu là mô phỏng, Δt được biết chính xác, chưa có rolling shutter và chưa có dữ liệu thật. Lần sau nhóm muốn thử thêm lỗi ước lượng Δt, nhiều seed hơn và dữ liệu thật."
