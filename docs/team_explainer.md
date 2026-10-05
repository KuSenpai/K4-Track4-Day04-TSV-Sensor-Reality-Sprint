# Giải thích cho cả nhóm (đọc trước khi pitch)

Mục đích: ai trong nhóm cũng tự trả lời được khi bị hỏi. Mọi số lấy từ [results/summary_tables.md](../results/summary_tables.md) (sinh từ [results/results.csv](../results/results.csv)). Dữ liệu là **tổng hợp**, do code của nhóm tạo ra, không phải dữ liệu xe thật.

## 1. Vấn đề trong một đoạn

Camera và LiDAR cùng đo một chiếc xe, nhưng mẫu LiDAR của mình bị gắn nhãn giờ trễ Δt so với lúc nó đo thật. Khi ghép với ảnh camera có cùng nhãn giờ, mình đang dùng vị trí cũ của xe. Xe càng nhanh thì vị trí cũ càng cách xa vị trí hiện tại. Đó là toàn bộ vấn đề của T4.

## 2. Công thức

- **Sai số ≈ v × Δt.** Ví dụ v = 20 m/s, Δt = 0.1 s thì sai 2.00 m. Công thức đúng khi v gần như không đổi, vì quãng đường xe đi trong Δt chính là v × Δt.
- **Bù chuyển động:** ước lượng vận tốc v̂ từ vài mẫu gần nhất, rồi dịch vị trí đo thêm v̂ × Δt (trong code gọi là `comp_cv`).
- **Khi xe phanh:** vận tốc đang giảm mà v̂ lấy từ các mẫu trước đó, nên v̂ bị "cũ", lớn hơn vận tốc thật và bù quá tay. Bias ổn định xấp xỉ ½·a·[(Δt + (N−1)h/2)² − h²(N²−1)/12], trong đó a là gia tốc, N là số khung trong cửa sổ, h = 0.1 s. Công thức này là suy luận của nhóm, khớp với số đo trong mô phỏng (Bảng D), không lấy từ paper nào.

## 3. Code làm gì ([src/run_benchmark.py](../src/run_benchmark.py))

1. `arc_and_speed` và `position`: tạo quỹ đạo thật (đường thẳng 15°, tốc độ không đổi hoặc phanh đều từ giây thứ 5).
2. `run_condition`: tạo mẫu LiDAR = vị trí thật tại `t − Δt` cộng nhiễu 0.10 m, áp ba cách xử lý `uncomp`, `comp_cv`, `comp_ca`, rồi tính metric trên các khung cần đánh giá.
3. `fit_weights` và `estimate`: khớp bình phương tối thiểu trên N khung (bậc 1 hoặc 2) rồi ngoại suy thêm Δt.
4. `make_plots` và `write_tables`: vẽ 4 ảnh PNG và sinh bảng markdown từ CSV.
5. Chỉ có một mảng nhiễu, seed 42, dùng chung cho mọi điều kiện, nên khác biệt giữa các điều kiện là do điều kiện chứ không phải do nhiễu.

## 4. Những số cần nhớ

| Điều cần nhớ | Số |
|---|---|
| Mức nhiễu nền (offset 0 ms) | 0.14 m không bù, 0.11 m sau bù |
| 20 m/s, 100 ms, không bù | 2.00 m (đúng bằng v×Δt, tỉ số 1.000) |
| 20 m/s, 200 ms: không bù → bù | 4.00 m → 0.19 m (giảm 95.2%) |
| Giảm RMSE thấp nhất khi v×Δt ≥ 1 m | 81.1% |
| Ca yếu nhất (5 m/s, 50 ms) | chỉ giảm 55.1% |
| Tốc độ vượt ngưỡng 0.5 m | 10.0 m/s (50 ms), 5.0 m/s (100 ms), 3.3 m/s (150 ms), 2.5 m/s (200 ms) |
| Failure: phanh 8 m/s², 200 ms, comp_cv N=5 | 0.55 m (so với 0.19 m khi không phanh); 59.1% khung vượt 0.5 m |
| Công thức v×Δt khi phanh | theo v₀: tỉ số 0.558; theo v(t): 1.073 |

Một claim ban đầu của nhóm **bị sai**: "comp_ca N=5 tốt hơn comp_cv N=5". Thực tế nó tệ hơn (0.58 m so với 0.55 m ở a = 8, offset 200 ms).

## 5. Câu hỏi giảng viên có thể hỏi

**1. Vì sao sai số ≈ v × Δt?**
LiDAR đo vật tại thời điểm sớm hơn nhãn giờ Δt. Trong khoảng Δt đó vật đi thêm v × Δt nếu v không đổi. Nhóm có kiểm lại: tỉ số |bias|/(v×Δt) từ 0.999 đến 1.000 ở 16 cấu hình.

**2. Dữ liệu tổng hợp thì kết luận được gì? Sao không dùng dữ liệu thật?**
Chỉ kết luận trong phạm vi mô phỏng và các tham số đã ghi (nhiễu 0.10 m, 10 Hz, quỹ đạo thẳng, biết chính xác Δt). Mô phỏng cho ground truth tuyệt đối và tách riêng được ảnh hưởng của lệch thời gian. Sai số do lệch thời gian chỉ phụ thuộc hình học chuyển động và Δt, nên mô phỏng tái tạo đúng cơ chế; chi tiết trong mục "Vì sao benchmark mô phỏng là proxy hợp lý" của [design/benchmark_design.md](../design/benchmark_design.md). Nhóm không có dữ liệu thật trong 120 phút, đó là hạn chế đã ghi. Về nguồn: Nowicki (arXiv:2006.16081) ước lượng Δt cùng với phép biến đổi 6-DOF và giả định offset nhỏ, gần như không đổi, camera global-shutter; với Wang và cộng sự (arXiv:2207.10454) nhóm chỉ đọc abstract. Nhóm không làm lại thuật toán của họ và không so số của mình với số của họ (xem [SOURCES.md](../SOURCES.md)).

**3. Sao bias khớp v×Δt chính xác mà RMSE thì lớn hơn một chút?**
RMSE tính cả nhiễu đo (mức nền 0.14 m), còn bias là trung bình có dấu nên nhiễu triệt tiêu. Ví dụ 5 m/s, 50 ms: |bias| là 0.25 m nhưng RMSE là 0.29 m.

**4. Bù chuyển động làm thế nào và hiệu quả đến đâu?**
Ước lượng v̂ từ 5 khung (0.4 s) rồi cộng v̂×Δt. Khi tốc độ không đổi, RMSE sau bù còn 0.13–0.19 m ở offset 50–200 ms; giảm ít nhất 81.1% khi v×Δt ≥ 1 m. Ca yếu nhất chỉ giảm 55.1% vì sai số gốc đã gần mức nhiễu nền. Điều kiện là phải biết đúng Δt.

**5. Sao phanh gấp làm bộ bù hỏng mà công thức v×Δt vẫn đúng?**
Công thức đúng nếu dùng tốc độ tức thời (tỉ số 1.073). Còn bộ bù ước lượng vận tốc từ cửa sổ các mẫu trước nên chậm pha, ước lượng cao hơn thật khi đang giảm tốc, nên bù thừa 0.49 m (bias) và sai số còn lại là 0.55 m. Công thức giải tích khớp bias đo được (0.56 m ở trạng thái ổn định, a = 8, 200 ms, N=5).

**6. Sao claim "comp_ca tốt hơn" lại sai?**
Khớp bậc hai trên 5 mẫu làm nhiễu to lên: ở a = 0 nó cho 0.57 m so với 0.19 m của comp_cv. Chỉ khi cửa sổ dài (N=9) và phanh mạnh thì nó thắng (0.31 m so với 0.55 m ở a = 8, 200 ms), còn phanh nhẹ vẫn thua (a = 2: 0.27 m so với 0.23 m). Nhóm ghi nhận claim sai chứ không sửa metric cho đẹp.

**7. Ngưỡng 0.5 m lấy ở đâu?**
Do nhóm tự đặt (cỡ cổng gán đối tượng), không lấy từ nguồn nào. Đổi ngưỡng thì tốc độ nguy hiểm v* = ngưỡng/Δt đổi theo (Bảng E).

**8. Nếu Δt ước lượng sai thì sao?**
Nhóm **chưa mô phỏng**. Giả thuyết: sai số còn lại sẽ tăng thêm cỡ v × (sai số ước lượng Δt). Đây mới là suy luận, cần kiểm ở vòng sau.

**9. Rolling shutter khác gì, nhóm có làm không?**
Chưa làm (phần mở rộng, chỉ làm sau khi xong phần tối thiểu). Ý tưởng: mỗi hàng ảnh được chụp ở thời điểm khác nhau, nên "Δt" thay đổi theo hàng. Nhóm chưa đo gì về việc này và chưa đọc nguồn S9.

**10. Sao biết kết quả không phải do may mắn của một seed?**
Đây là hạn chế: nhóm chỉ chạy 1 seed (42) × 200 lượt. Các kết luận chính (bias ≈ v×Δt, sai số tăng theo gia tốc) có cấu trúc rõ ràng, không phụ thuộc vào nhiễu, nhưng dao động giữa các seed thì chưa đo.

## 6. Việc cần làm trước khi pitch

- Chạy lệnh trong [README.md](../README.md) trên máy của mình.
- Đọc lại báo cáo của mình trong [reports/](../reports/) và sửa cho đúng phần mình làm.
- Diễn tập [pitch/pitch_script.md](../pitch/pitch_script.md) và bấm giờ thật.
