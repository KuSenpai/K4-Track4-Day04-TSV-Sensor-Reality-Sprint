# Failure case – xe phía trước phanh gấp, bộ bù vận tốc không đổi bù sai

Dữ liệu là **tổng hợp** (nhóm tự mô phỏng 2D, không phải dữ liệu thật). Mọi số lấy từ [results/summary_tables.md](results/summary_tables.md) và [results/results.csv](results/results.csv). Chạy lại bằng `python src/run_benchmark.py`.

## 1. Cấu hình

- Vật chạy thẳng theo hướng 15°, v₀ = 20 m/s, **bắt đầu phanh ở giây thứ 5** với a = 8 m/s² (dừng sau 2.5 s). Nhóm đánh giá trong khoảng 5–8 s và chỉ tính các khung vật còn chuyển động (v > 0.1 m/s).
- LiDAR lệch **200 ms** (mẫu bị gắn nhãn giờ trễ 200 ms so với lúc đo thật). Camera là mốc chuẩn. Nhiễu LiDAR 0.10 m mỗi trục, 10 Hz, 200 lượt, seed 42, mọi điều kiện dùng chung một mảng nhiễu.
- Bộ bù `comp_cv`: khớp đường thẳng (bình phương tối thiểu) trên 5 khung gần nhất (0.4 s) rồi ngoại suy thêm Δt. Δt được biết chính xác.
- Hình: [results/failure_braking.png](results/failure_braking.png), [results/timeline_offset200ms.png](results/timeline_offset200ms.png) (timeline minh họa với a = 6 m/s², một lượt).

## 2. Số baseline và số khi lỗi (đo thật)

| Điều kiện | Offset | Gia tốc | RMSE (m) |
|---|---|---|---|
| Baseline đồng bộ, comp_cv N=5 | 0 ms | 8 m/s² | 0.13 |
| Không bù, offset 200 ms | 200 ms | 8 m/s² | 2.51 |
| comp_cv N=5, tốc độ không đổi (a = 0) | 200 ms | 0 | 0.19 |
| **comp_cv N=5, phanh gấp (failure)** | 200 ms | 8 m/s² | **0.55** |

- Nhóm quan sát được: bù chuyển động kéo RMSE từ 2.51 m xuống 0.55 m khi phanh gấp, nhưng sai số còn lại gần gấp ba so với lúc tốc độ không đổi cùng offset (0.55 m so với 0.19 m).
- Nhóm quan sát được: sau khi bù, bias dọc quỹ đạo là +0.49 m (dương nghĩa là ước lượng nằm *trước* vị trí thật theo hướng chạy), và 59.1% số khung có sai số vượt 0.5 m (lúc tốc độ không đổi là 0.1%).
- Nhóm quan sát được: sai số còn lại tăng đều theo gia tốc phanh (offset 200 ms, N=5): 0.19 → 0.23 → 0.32 → 0.44 → 0.55 m ứng với a = 0 / 2 / 4 / 6 / 8 m/s².
- Nhóm quan sát được: công thức v·Δt với v₀ = 20 m/s cho 4.00 m, nhưng sai số không bù đo được chỉ 2.23 m (tỉ số 0.558). Nếu dùng tốc độ tức thời trung bình thì v(t)·Δt là 2.08 m và tỉ số 1.073, tức công thức vẫn đúng khi dùng đúng tốc độ tại thời điểm đó. Vậy giả định bị vi phạm chủ yếu ở bộ bù, không phải ở công thức.

## 3. Hệ quả cho tính năng ADAS

- Nhóm quan sát được: với ngưỡng 0.5 m (nhóm tự đặt), bộ bù chạy tốt khi tốc độ không đổi, nhưng khi phanh gấp ở offset 200 ms thì 59.1% khung vượt ngưỡng. Ở offset 100 ms con số này là 2.2% (a = 8), ở 50 ms là 0.0%.
- Giả thuyết (chưa kiểm vì mô phỏng không có xe ego): bias dương nghĩa là vật bị đặt xa hơn vị trí thật đúng lúc nó đang phanh, tức lúc cần phản ứng nhanh nhất. Nếu hệ thống dùng vị trí đã bù để tính khoảng cách hay thời gian va chạm thì cảnh báo có thể đến muộn.

## 4. Hạn chế

- Dữ liệu tổng hợp, quỹ đạo thẳng, phanh đều, nhiễu Gauss 0.10 m (giả định), Δt biết chính xác. Không có xe ego, không có rolling shutter, không mô phỏng lỗi ước lượng Δt hay jitter.
- Các khung sau khi vật đã dừng bị loại, nên hiện tượng bù vượt ngay lúc vật vừa dừng không nằm trong số liệu.
- Chỉ có một seed (42) × 200 lượt; chưa đo dao động giữa các seed.
- Ngưỡng 0.5 m do nhóm chọn, không lấy từ nguồn nào. Nhóm không đem số của mình so với số của paper nào.

## 5. Giả thuyết giải thích (có gắn nhãn)

- **Giả thuyết:** khớp đường thẳng trên N mẫu chỉ cho đúng vận tốc ở *giữa cửa sổ*, tức chậm (N−1)·h/2 so với hiện tại. Khi vật giảm tốc, vận tốc ước lượng cao hơn thật nên bộ bù đẩy vị trí đi quá xa. Tính giải tích với giảm tốc đều và cửa sổ nằm hẳn trong pha phanh cho bias ổn định = ½·a·[(Δt + (N−1)h/2)² − h²(N²−1)/12].
- Nhóm quan sát được (kiểm giả thuyết ngay trong mô phỏng): bias ổn định đo được khớp công thức ở cả 16 tổ hợp a × offset với N = 5 và N = 9 (ví dụ a = 8, offset 200 ms, N = 5: đo 0.56 m, công thức 0.56 m; N = 9: đo 1.17 m, công thức 1.17 m, xem Bảng D). Công thức cũng cho thấy cửa sổ dài hơn thì sai nhiều hơn khi phanh (N=9: RMSE 1.03 m, N=5: 0.55 m ở a = 8, offset 200 ms) dù tốt hơn khi tốc độ không đổi (0.12 m so với 0.19 m).
- **Giả thuyết (chưa kiểm):** trên dữ liệu thật, tracker có làm mượt vận tốc cũng sẽ bị chậm pha theo cách tương tự; mức độ phụ thuộc vào tracker cụ thể.

## 6. Cải tiến / fallback đề xuất

1. **Giảm độ trễ của ước lượng vận tốc:** dùng cửa sổ ngắn hơn khi thấy có gia tốc. Số đo: a = 8, offset 200 ms, N = 3 cho RMSE 0.44 m so với 0.55 m của N = 5 (đổi lại nhiễu cao hơn khi tốc độ không đổi: 0.32 m so với 0.19 m).
2. **Mô hình gia tốc không đổi (comp_ca) với cửa sổ dài:** bias ổn định xấp xỉ 0.00 m ở mọi tổ hợp đã đo; ở a = 8, offset 200 ms, comp_ca N = 9 cho 0.31 m. Nhược điểm đã đo: khi tốc độ không đổi, comp_ca N = 9 cho 0.27 m so với 0.12 m của comp_cv N = 9, và comp_ca N = 5 kém hơn comp_cv N = 5 ở mọi mức phanh.
3. **Fallback:** khi hệ số bậc hai của khớp comp_ca (gia tốc ước lượng) vượt một ngưỡng thì chuyển sang comp_ca N = 9, hoặc nới cổng gán và tăng độ bất định thay vì tin vị trí đã bù. Ngưỡng cụ thể **chưa xác định**, cần thử ở vòng sau.
4. **Xử lý từ gốc:** giảm Δt bằng đồng bộ phần cứng hoặc ước lượng Δt online, vì sai số còn lại tăng theo Δt (Bảng C: ở a = 8, RMSE tăng từ 0.21 m ở 50 ms lên 0.55 m ở 200 ms với comp_cv N = 5).

## 7. Metric và log để kiểm chứng ở vòng sau

- Metric: RMSE và p95 sau bù, tỉ lệ khung sai số vượt 0.5 m, bias dọc quỹ đạo có dấu, tách theo gia tốc ước lượng; so với công thức giải tích ở trên.
- Log cần có: nhãn giờ thô của từng sensor, Δt ước lượng, vận tốc và gia tốc ước lượng từng khung, sai số còn lại sau bước gán đối tượng, và nhãn "đang phanh" từ ground truth.
- Thí nghiệm tiếp theo: (a) thêm lỗi ước lượng Δt và jitter, (b) dữ liệu thật có ground truth nếu kiếm được, (c) chạy nhiều seed, (d) thử rolling-shutter line delay như phần mở rộng.
