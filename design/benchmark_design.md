# Benchmark design – T4: lệch thời gian đa sensor tạo sai số vị trí bao nhiêu?

File này được viết **trước khi chạy code** (ngày 2026-10-05). Các ô "Bằng chứng" của Bước 3 được điền sau mỗi lần chạy; các claim ở Bước 1 giữ nguyên để so sánh với kết quả.

## Bước 1 – Thiết kế

| Hạng mục | Nội dung |
|---|---|
| Nền tảng | Xe ADAS (ego-vehicle) |
| Tính năng | Fusion camera + LiDAR để theo dõi vị trí xe phía trước (cảnh báo va chạm / giữ khoảng cách / gán đối tượng giữa hai sensor) |
| Sensor | Camera (làm mốc thời gian chuẩn) + LiDAR (bị lệch timestamp). Radar: không dùng. |
| Dữ liệu | **Tổng hợp** (mô phỏng 2D, không có dữ liệu thật). Không phải dữ liệu KITTI/nuScenes. |
| Failure case dự kiến | Xe mục tiêu phanh gấp (giảm tốc a) trong khi bộ bù dùng mô hình vận tốc không đổi → vi phạm giả định "tốc độ gần không đổi" |
| Metric + đơn vị | (1) Sai số vị trí Euclid: RMSE, mean, p95 [m]. (2) Sai số dọc quỹ đạo có dấu (along-track bias) [m]. (3) Tỉ lệ \|bias\| / (v·Δt) [không đơn vị]. (4) Phần trăm giảm sai số sau bù [%]. (5) Tốc độ nguy hiểm v* = ngưỡng / Δt [m/s]. |
| Baseline | Offset 0 ms (hai sensor đồng bộ) – cho sàn nhiễu đo. |
| Điều kiện lỗi | Offset LiDAR 50 / 100 / 150 / 200 ms (LiDAR đóng dấu thời gian trễ so với thời điểm chụp thật). |
| Đối chứng bù | `uncomp` (dùng thẳng phép đo lệch) vs `comp_cv` (bù bằng vận tốc ước lượng từ N mẫu) vs `comp_ca` (bù bằng mô hình gia tốc không đổi). |

### Mô hình mô phỏng (tham số cố định)

- Vật thể chuyển động trong mặt phẳng 2D, hướng 15° so với trục x, bắt đầu tại gốc.
- LiDAR và camera cùng tần số 10 Hz, 100 khung/lượt, 200 lượt (trial)/cấu hình, seed 42, **cùng một mảng nhiễu cho mọi điều kiện** (common random numbers).
- Mẫu LiDAR tại timestamp `t_k` thực ra đo vị trí tại `t_k − Δt` + nhiễu Gauss σ = 0.10 m mỗi trục (**giả định của nhóm**, không lấy từ nguồn). Camera được coi là mốc thời gian chuẩn; đối chiếu với vị trí thật `p(t_k)`.
- Bộ bù biết trước Δt (đã hiệu chuẩn) – mô phỏng trường hợp tốt nhất; **không** mô phỏng lỗi ước lượng Δt.
- Bộ bù: khớp bình phương tối thiểu trên N khung gần nhất (mặc định N = 5, tức 0.4 s), ngoại suy thêm Δt.
- Bỏ 1 s đầu (khởi động cửa sổ). Chỉ tính các khung có tốc độ thật > 0.1 m/s.
- Tốc độ không đổi: v ∈ {5, 10, 20, 30} m/s. Failure: v₀ = 20 m/s, bắt đầu phanh tại t = 5 s với a ∈ {0, 2, 4, 6, 8} m/s²; đánh giá trong cửa sổ t ∈ [5, 8] s.
- Ngưỡng "đáng lo": **0.5 m** sai số vị trí – là **giả định của nhóm** (cỡ cổng gán đối tượng / một phần nhỏ bề rộng làn), không lấy từ nguồn nào.

### Claim → metric dự kiến (viết trước khi chạy)

| # | Claim ban đầu | Metric kiểm | Tiêu chí |
|---|---|---|---|
| C1 | Khi tốc độ không đổi, sai số dọc quỹ đạo không bù ≈ v·Δt | \|bias\|/(v·Δt) | trong khoảng 0.95–1.05 |
| C2 | Bù chuyển động giảm RMSE ≥ 70% ở mọi cấu hình có v·Δt ≥ 1 m | % giảm RMSE | ≥ 70% |
| C3 | Khi phanh gấp, v₀·Δt (tốc độ danh định) không còn mô tả được sai số | \|bias\|/(v₀·Δt) | lệch > 10% so với 1 |
| C4 | Khi phanh gấp, sai số dư sau bù (comp_cv) tăng đơn điệu theo \|a\| | RMSE comp_cv theo a | tăng đơn điệu |
| C5 | Mô hình gia tốc (comp_ca) giảm sai số dư so với comp_cv khi phanh | RMSE comp_ca vs comp_cv | comp_ca thấp hơn |

### Phân công 5 người

| Thành viên | Vai trò chính | Việc cụ thể |
|---|---|---|
| TV1 | Đọc nguồn | SOURCES.md, giữ ranh giới "paper cho biết" vs "nhóm đo" |
| TV2 | Chạy code | `src/run_benchmark.py`, seed, chạy lại bản sạch |
| TV3 | Ghi benchmark | results.csv, bảng Bước 3, kiểm tra số khớp CSV |
| TV4 | Phân tích failure | failure_case.md, giả thuyết, cải tiến/fallback |
| TV5 | Trình bày | pitch, team_explainer, CHECKLIST |

## Bước 3 – Điều kiện, tham số, metric, bằng chứng

Ô "Bằng chứng" được điền sau lần chạy ngày 2026-10-05 (seed 42). Mọi số lấy từ [results/summary_tables.md](../results/summary_tables.md) (sinh từ [results/results.csv](../results/results.csv)).

| Điều kiện | Tham số | Metric | Bằng chứng (số đo thật) | Điều cho phép kết luận |
|---|---|---|---|---|
| Baseline offset 0 ms | v ∈ {5,10,20,30} m/s, σ = 0.10 m | RMSE, bias | RMSE không bù 0.14 m (mọi tốc độ); sau bù N=5 là 0.11 m | Sàn nhiễu đo của mô phỏng ≈ 0.14 m |
| Offset 50 ms | như trên | RMSE, bias, ratio | RMSE không bù: 0.29 / 0.52 / 1.01 / 1.51 m cho v = 5 / 10 / 20 / 30 m/s; ratio 0.999–1.000 | Sai số theo v·Δt trong phạm vi 4 tốc độ, dữ liệu tổng hợp |
| Offset 100 ms | như trên | như trên | RMSE: 0.52 / 1.01 / 2.00 / 3.00 m | như trên |
| Offset 150 ms | như trên | như trên | RMSE: 0.76 / 1.51 / 3.00 / 4.50 m | như trên |
| Offset 200 ms | như trên | như trên | RMSE: 1.01 / 2.00 / 4.00 / 6.00 m | như trên |
| Bù comp_cv, N=5 | mọi offset, mọi tốc độ | % giảm RMSE | 55.1% (5 m/s, 50 ms) đến 96.8% (30 m/s, 200 ms); RMSE sau bù 0.13–0.19 m với offset 50–200 ms | Bù hiệu quả khi Δt đã biết chính xác và tốc độ gần không đổi |
| Phanh a = 2/4/6/8 m/s², v₀ = 20 m/s | offset 50–200 ms, N ∈ {3,5,9} | RMSE dư, ratio | Offset 200 ms, comp_cv N=5: RMSE 0.23 / 0.32 / 0.44 / 0.55 m cho a = 2 / 4 / 6 / 8; ratio theo v₀: 0.860 → 0.558, theo v(t): 1.011 → 1.073 | Giả định tốc độ không đổi vi phạm ra sao trong phạm vi đã đo (xem failure_case.md) |

### Kết quả kiểm từng claim (ghi trung thực)

| # | Kết quả | Chi tiết |
|---|---|---|
| C1 | **ĐÚNG** | ratio \|bias\|/(v·Δt) từ 0.999 đến 1.000 ở 16 cấu hình tốc độ không đổi có Δt > 0 |
| C2 | **ĐÚNG trong phạm vi claim** | Cấu hình có v·Δt ≥ 1 m: giảm RMSE thấp nhất 81.1%. Ngoài phạm vi claim (v·Δt < 1 m): có cấu hình chỉ giảm 55.1% (5 m/s, 50 ms) vì sàn nhiễu chiếm phần lớn |
| C3 | **ĐÚNG một phần – phát hiện đáng chú ý** | Với v₀ danh định, ratio còn 0.853–0.529 (lệch > 10%). Nhưng với tốc độ tức thời v(t) trung bình, ratio vẫn 1.003–1.073: công thức v·Δt **vẫn dùng được nếu dùng đúng tốc độ tại thời điểm đó**; chỗ vi phạm thật nằm ở bộ bù (C4) |
| C4 | **ĐÚNG** | RMSE comp_cv tăng đơn điệu theo \|a\| ở cả 12 tổ hợp (offset 50–200 ms × N = 3/5/9) |
| C5 | **SAI với N=5** | comp_ca N=5 **tệ hơn** comp_cv N=5 ở mọi a (vd a = 8, offset 200 ms: 0.58 m vs 0.55 m; a = 0: 0.57 m vs 0.19 m) vì khuếch đại nhiễu. Với N=9, comp_ca (0.31 m) tốt hơn comp_cv N=9 (1.03 m) và comp_cv N=5 (0.55 m) tại a = 8, offset 200 ms, nhưng vẫn kém comp_cv N=5 ở a = 2 (0.27 m vs 0.23 m) |
