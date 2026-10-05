# Giải thích cho cả nhóm (đọc trước khi pitch / bị hỏi)

Mục tiêu: ai trong nhóm cũng tự trả lời được. Mọi số lấy từ [results/summary_tables.md](../results/summary_tables.md) (sinh từ [results/results.csv](../results/results.csv)). Dữ liệu là **tổng hợp** – do code của nhóm sinh ra, không phải dữ liệu xe thật.

## 1. Bức tranh lớn

Camera và LiDAR đo cùng một chiếc xe, nhưng mẫu LiDAR của chúng ta bị "dán nhãn giờ" trễ Δt so với lúc nó đo thật. Khi ghép với ảnh camera cùng nhãn giờ, ta dùng vị trí cũ của xe. Xe càng nhanh, vị trí cũ càng xa vị trí hiện tại. Đó là toàn bộ vấn đề của T4.

## 2. Công thức

- **Sai số ≈ v × Δt.** Ví dụ v = 20 m/s, Δt = 0.1 s → 2.00 m. Đúng khi v gần không đổi vì quãng đường đi được trong Δt chính là v × Δt.
- **Bù chuyển động:** ước lượng vận tốc v̂ từ vài mẫu gần nhất rồi dịch vị trí đo thêm v̂ × Δt (code gọi là `comp_cv`).
- **Khi phanh:** vận tốc đang giảm mà v̂ lấy từ cửa sổ quá khứ, nên v̂ bị "cũ" và lớn hơn thật → bù quá tay. Bias ổn định ≈ ½·a·[(Δt + (N−1)h/2)² − h²(N²−1)/12], với a là gia tốc, N số khung trong cửa sổ, h = 0.1 s. Công thức này là suy luận của nhóm và khớp số đo trong mô phỏng (Bảng D), không phải kết quả của paper nào.

## 3. Code làm gì ([src/run_benchmark.py](../src/run_benchmark.py))

1. `arc_and_speed` / `position`: quỹ đạo thật (thẳng, 15°; tốc độ không đổi hoặc phanh đều từ 5 s).
2. `run_condition`: tạo mẫu LiDAR = vị trí thật tại `t − Δt` + nhiễu 0.10 m; áp `uncomp`, `comp_cv`, `comp_ca`; tính metric chỉ trên các khung đánh giá.
3. `fit_weights` / `estimate`: khớp bình phương tối thiểu trên N khung (bậc 1 hoặc 2) rồi ngoại suy thêm Δt.
4. `make_plots`, `write_tables`: sinh 4 PNG và bảng markdown từ CSV.
5. Một mảng nhiễu duy nhất, seed 42, dùng cho mọi điều kiện → khác biệt giữa điều kiện là do điều kiện.

## 4. Kết quả cần nhớ

| Điều | Số |
|---|---|
| Sàn nhiễu (offset 0 ms) | 0.14 m không bù, 0.11 m sau bù |
| 20 m/s, 100 ms, không bù | 2.00 m (= v×Δt, tỉ số 1.000) |
| 20 m/s, 200 ms: không bù → bù | 4.00 m → 0.19 m (giảm 95.2%) |
| Giảm RMSE tối thiểu khi v×Δt ≥ 1 m | 81.1% |
| Ca yếu nhất (5 m/s, 50 ms) | chỉ giảm 55.1% |
| Tốc độ vượt ngưỡng 0.5 m | 10.0 m/s (50 ms), 5.0 m/s (100 ms), 3.3 m/s (150 ms), 2.5 m/s (200 ms) |
| Failure: phanh 8 m/s², 200 ms, comp_cv N=5 | 0.55 m (so với 0.19 m khi không phanh); 59.1% khung > 0.5 m |
| Công thức v×Δt khi phanh | theo v₀: tỉ số 0.558; theo v(t): 1.073 |

Claim ban đầu **sai**: comp_ca N=5 tốt hơn comp_cv N=5 (thực tế tệ hơn, 0.58 m so với 0.55 m ở a = 8, offset 200 ms).

## 5. Câu hỏi giảng viên có thể hỏi

**1. Vì sao sai số ≈ v × Δt?**
Vì LiDAR đo vật tại thời điểm sớm hơn Δt; trong khoảng đó vật đi thêm v × Δt nếu v không đổi. Nhóm kiểm lại: tỉ số |bias|/(v×Δt) từ 0.999 đến 1.000 ở 16 cấu hình.

**2. Dữ liệu tổng hợp thì kết luận được gì? Sao không dùng dữ liệu thật?**
Chỉ kết luận trong phạm vi mô phỏng và tham số đã ghi (nhiễu 0.10 m, 10 Hz, quỹ đạo thẳng, Δt biết chính xác). Mô phỏng cho ta ground truth tuyệt đối và cô lập được riêng hiệu ứng lệch thời gian. Sai số do lệch thời gian chỉ phụ thuộc hình học chuyển động và Δt nên mô phỏng tái tạo đúng cơ chế; xem mục "Vì sao benchmark mô phỏng là proxy hợp lý" trong [design/benchmark_design.md](../design/benchmark_design.md). Nhóm không có dữ liệu thật trong 120 phút; đây là hạn chế đã nêu. Về nguồn: Nowicki (arXiv:2006.16081) ước lượng Δt chung với biến đổi 6-DOF và giả định offset nhỏ, xấp xỉ không đổi, camera global-shutter; Wang et al. (arXiv:2207.10454) nhóm chỉ đọc abstract. Nhóm không tái hiện thuật toán của họ và không so số của mình với số của họ (xem [SOURCES.md](../SOURCES.md)).

**3. Vì sao bias khớp v×Δt chính xác mà RMSE thì lớn hơn một chút?**
RMSE gồm cả nhiễu đo (sàn 0.14 m), còn bias là trung bình có dấu nên nhiễu triệt tiêu. Ví dụ 5 m/s, 50 ms: |bias| 0.25 m nhưng RMSE 0.29 m.

**4. Bù chuyển động hoạt động thế nào và hiệu quả đến đâu?**
Ước lượng v̂ từ 5 khung (0.4 s) rồi cộng v̂×Δt. Khi tốc độ không đổi, RMSE sau bù còn 0.13–0.19 m ở offset 50–200 ms; giảm 81.1% hoặc hơn khi v×Δt ≥ 1 m. Ca yếu nhất giảm 55.1% vì sai số gốc đã gần sàn nhiễu. Điều kiện: biết đúng Δt.

**5. Vì sao phanh gấp làm bộ bù hỏng, trong khi công thức v×Δt vẫn đúng?**
Công thức đúng nếu dùng tốc độ tức thời (tỉ số 1.073). Bộ bù thì ước lượng vận tốc từ cửa sổ quá khứ nên chậm pha, ước lượng cao hơn thật khi đang giảm tốc → bù thừa 0.49 m (bias), sai số dư 0.55 m. Công thức giải tích khớp bias đo được (0.56 m ổn định, a = 8, 200 ms, N=5).

**6. Vì sao claim "comp_ca tốt hơn" sai?**
Hồi quy bậc hai trên 5 mẫu khuếch đại nhiễu: ở a = 0 nó cho 0.57 m so với 0.19 m của comp_cv. Chỉ khi cửa sổ dài (N=9) và phanh mạnh nó thắng (0.31 m so với 0.55 m ở a = 8, 200 ms), nhưng vẫn thua ở phanh nhẹ (a = 2: 0.27 m so với 0.23 m). Nhóm ghi nhận claim sai thay vì sửa metric.

**7. Ngưỡng 0.5 m lấy từ đâu?**
Là giả định của nhóm (cỡ cổng gán đối tượng), không lấy từ nguồn nào. Đổi ngưỡng thì tốc độ nguy hiểm v* = ngưỡng/Δt đổi tương ứng (Bảng E).

**8. Nếu Δt ước lượng sai thì sao?**
Nhóm **chưa mô phỏng**. Giả thuyết: sai số dư tăng thêm khoảng v × (sai số ước lượng Δt). Đây là suy luận, cần kiểm ở vòng sau.

**9. Rolling shutter khác gì? Nhóm có làm không?**
Chưa làm (phần mở rộng, chỉ làm sau khi xong phần tối thiểu). Ý tưởng: mỗi hàng ảnh được chụp ở thời điểm khác nhau nên "Δt" thay đổi theo hàng. Nhóm chưa đo gì về điều này và chưa đọc nguồn S9.

**10. Làm sao biết kết quả không do may mắn của một seed?**
Hạn chế: chỉ 1 seed (42) × 200 lượt. Các kết luận chính (bias ≈ v×Δt, xu hướng tăng theo gia tốc) là xu hướng có cấu trúc, không phụ thuộc vào nhiễu, nhưng biến thiên giữa các seed chưa đo.

## 6. Việc cần làm trước khi pitch

- Điền tên/MSSV vào [TEAMMATES.md](../TEAMMATES.md) và đầu mỗi báo cáo trong [reports/](../reports/).
- Chạy lệnh trong [README.md](../README.md) trên máy mình.
- Diễn tập [pitch/pitch_script.md](../pitch/pitch_script.md) để bấm giờ thật.
