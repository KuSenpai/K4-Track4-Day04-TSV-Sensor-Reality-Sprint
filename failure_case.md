# Failure case – bộ bù chuyển động giả định vận tốc không đổi, khi vật thể phanh gấp

Dữ liệu: **tổng hợp** (mô phỏng 2D của nhóm, không phải dữ liệu thật). Mọi số lấy từ [results/summary_tables.md](results/summary_tables.md) / [results/results.csv](results/results.csv), lệnh tái hiện: `python src/run_benchmark.py`.

## 1. Cấu hình

- Vật thể chạy thẳng hướng 15°, v₀ = 20 m/s, **bắt đầu phanh tại t = 5 s** với giảm tốc a = 8 m/s² (dừng sau 2.5 s). Đánh giá trong cửa sổ t ∈ [5, 8] s, chỉ các khung vật còn chuyển động (v > 0.1 m/s).
- LiDAR bị lệch **offset 200 ms** (mẫu đóng dấu thời gian trễ 200 ms so với lúc đo). Camera là mốc chuẩn. Nhiễu LiDAR σ = 0.10 m mỗi trục, 10 Hz, 200 lượt, seed 42, cùng mảng nhiễu cho mọi điều kiện.
- Bộ bù `comp_cv`: khớp tuyến tính bình phương tối thiểu trên N = 5 khung gần nhất (0.4 s), ngoại suy thêm Δt. Δt được biết chính xác.
- Ảnh: [results/failure_braking.png](results/failure_braking.png), [results/timeline_offset200ms.png](results/timeline_offset200ms.png) (timeline minh họa a = 6 m/s², 1 lượt).

## 2. Số baseline và số khi lỗi (đo thật)

| Điều kiện | Offset | Gia tốc | RMSE (m) |
|---|---|---|---|
| Baseline đồng bộ, comp_cv N=5 | 0 ms | 8 m/s² | 0.13 |
| Không bù, offset 200 ms | 200 ms | 8 m/s² | 2.51 |
| comp_cv N=5, tốc độ không đổi (a = 0) | 200 ms | 0 | 0.19 |
| **comp_cv N=5, phanh gấp (failure)** | 200 ms | 8 m/s² | **0.55** |

- Nhóm quan sát được: bù chuyển động giảm RMSE từ 2.51 m xuống 0.55 m khi phanh gấp, nhưng sai số dư gần gấp ba so với trường hợp tốc độ không đổi cùng offset (0.55 m so với 0.19 m).
- Nhóm quan sát được: bias dọc quỹ đạo sau bù là +0.49 m (dương = ước lượng nằm **trước** vị trí thật theo hướng chuyển động), tỉ lệ khung có sai số > 0.5 m là 59.1% (khi tốc độ không đổi: 0.1%).
- Nhóm quan sát được: sai số dư tăng đơn điệu theo giảm tốc (offset 200 ms, N=5): 0.19 → 0.23 → 0.32 → 0.44 → 0.55 m cho a = 0 / 2 / 4 / 6 / 8 m/s².
- Nhóm quan sát được: công thức v·Δt với v₀ = 20 m/s cho 4.00 m, nhưng sai số không bù đo được chỉ 2.23 m (ratio 0.558). Với tốc độ tức thời trung bình, v(t)·Δt = 2.08 m và ratio 1.073 → công thức vẫn đúng nếu dùng đúng tốc độ tại thời điểm đó. Sự vi phạm giả định thể hiện chủ yếu ở bộ bù, không phải ở bản thân công thức.

## 3. Hệ quả cho tính năng (ADAS)

- Nhóm quan sát được: với ngưỡng 0.5 m (giả định của nhóm), bộ bù hoạt động tốt khi tốc độ không đổi nhưng vượt ngưỡng ở 59.1% khung khi phanh gấp ở offset 200 ms; ở offset 100 ms con số là 2.2% (a = 8) và ở 50 ms là 0.0%.
- Giả thuyết (chưa kiểm chứng, mô phỏng không có xe ego): lệch dương nghĩa là vật bị đặt xa hơn/trước vị trí thật trong lúc nó đang phanh – đúng lúc cần phản ứng nhanh nhất. Nếu fusion dùng vị trí đã bù để tính TTC hay khoảng cách, cảnh báo có thể muộn.

## 4. Limitation

- Dữ liệu tổng hợp, quỹ đạo thẳng, phanh đều, nhiễu Gauss trắng σ = 0.10 m (giả định), Δt được biết chính xác, không có xe ego, không có rolling shutter, không mô phỏng lỗi ước lượng Δt hay jitter.
- Chỉ tính các khung vật còn chuyển động; khung sau khi vật dừng bị loại, nên hiện tượng "bù vượt khi vật vừa dừng" không nằm trong số liệu.
- Một seed (42) × 200 lượt; chưa đo biến thiên giữa các seed.
- Ngưỡng 0.5 m là lựa chọn của nhóm, không từ nguồn nào. Nhóm không so sánh số của mình với số của paper nào.

## 5. Giả thuyết giải thích (gắn nhãn: GIẢ THUYẾT / suy luận giải tích)

- **Giả thuyết:** Hồi quy tuyến tính trên N mẫu chỉ ước lượng đúng vận tốc ở *giữa cửa sổ*, tức chậm (N−1)·h/2 so với thời điểm cần; khi vật giảm tốc, vận tốc ước lượng cao hơn thực tế và bộ bù đẩy vị trí quá xa. Suy luận giải tích (mô hình giảm tốc đều, cửa sổ nằm trọn trong pha phanh) cho bias ổn định = ½·a·[(Δt + (N−1)h/2)² − h²(N²−1)/12].
- Nhóm quan sát được (kiểm chứng giả thuyết trong *mô phỏng*): bias ổn định đo được khớp công thức này ở cả 16 tổ hợp a × offset cho N = 5 và N = 9 (vd a = 8, offset 200 ms, N = 5: đo 0.56 m, công thức 0.56 m; N = 9: đo 1.17 m, công thức 1.17 m – xem Bảng D). Công thức cho thấy cửa sổ dài hơn làm sai số lớn hơn khi phanh (N=9: RMSE 1.03 m so với N=5: 0.55 m ở a = 8, offset 200 ms) dù tốt hơn khi tốc độ không đổi (0.12 m so với 0.19 m).
- **Giả thuyết (chưa kiểm chứng):** trên dữ liệu thật, cùng cơ chế "ước lượng vận tốc chậm pha" sẽ xuất hiện với tracker dùng cửa sổ/bộ lọc làm mượt; độ lớn phụ thuộc cấu hình tracker thật.

## 6. Cải tiến / fallback đề xuất

1. **Giảm lag ước lượng:** dùng cửa sổ ngắn hơn khi phát hiện gia tốc. Bằng chứng đo: ở a = 8, offset 200 ms, N = 3 cho RMSE 0.44 m so với 0.55 m của N = 5 (đổi lại nhiễu cao hơn khi tốc độ không đổi: 0.32 m so với 0.19 m).
2. **Mô hình gia tốc không đổi (comp_ca) với cửa sổ dài:** bias ổn định ≈ 0.00 m ở mọi tổ hợp đo; ở a = 8, offset 200 ms, comp_ca N = 9 cho 0.31 m. Nhược điểm đo được: khi tốc độ không đổi, comp_ca N = 9 cho 0.27 m so với 0.12 m của comp_cv N = 9 (nhiễu khuếch đại), và comp_ca N = 5 kém hơn comp_cv N = 5 ở mọi mức phanh đã đo.
3. **Fallback:** khi hệ số bậc hai của khớp comp_ca (gia tốc ước lượng) vượt một ngưỡng, chuyển sang comp_ca N = 9 hoặc nới cổng gán/tăng hiệp phương sai thay vì tin vị trí đã bù. Ngưỡng cụ thể: **chưa xác định**, cần thử ở vòng sau.
4. **Gốc rễ:** giảm Δt bằng đồng bộ phần cứng/ước lượng Δt online, vì sai số dư ∝ Δt (xem bảng C: ở a = 8, RMSE tăng từ 0.21 m (50 ms) lên 0.55 m (200 ms) với comp_cv N = 5).

## 7. Metric / log để kiểm chứng ở vòng sau

- Metric: RMSE và p95 sai số sau bù, tỉ lệ khung sai số > 0.5 m, bias dọc quỹ đạo (có dấu), tách theo |a| ước lượng; so với công thức giải tích ở trên.
- Log cần có: timestamp thô của từng sensor, Δt ước lượng, vận tốc/gia tốc ước lượng từng khung, sai số dư sau gán đối tượng, và nhãn "đang phanh" từ ground truth.
- Thí nghiệm kế tiếp: (a) thêm lỗi ước lượng Δt và jitter, (b) dữ liệu thật có ground truth (nếu có), (c) nhiều seed, (d) rolling-shutter line delay như phần mở rộng.
