# K4-Track4-Day04 – Sensor Reality Sprint (T4: lệch thời gian đa sensor)

Nhóm: TSV – thành viên: xem [TEAMMATES.md](TEAMMATES.md).
Chủ đề T4 · nền tảng xe ADAS · sensor camera + LiDAR · **dữ liệu tổng hợp** (mô phỏng 2D, không phải dữ liệu thật).

Câu hỏi: LiDAR lệch 50–200 ms so với camera tạo sai số vị trí bao nhiêu, bù chuyển động giảm được bao nhiêu, và khi nào giả định "tốc độ không đổi" hỏng?

## Cài đặt

Python 3.11 (đã thử với 3.11.7), thư viện: numpy, pandas, matplotlib.

```bash
pip install -r requirements.txt
```

## Tái hiện toàn bộ kết quả (một dòng)

```bash
python src/run_benchmark.py && python scripts/check_submission.py
```

(Windows PowerShell 5.1 không có `&&`: dùng `python src/run_benchmark.py; python scripts/check_submission.py`.)

- `src/run_benchmark.py` (entrypoint duy nhất, seed 42) ghi vào `results/`: `results.csv`, `summary_tables.md`, `thresholds.csv`, `params.json`, `run_log.txt`, và 4 ảnh PNG (`error_vs_offset.png`, `comp_vs_uncomp.png`, `failure_braking.png`, `timeline_offset200ms.png`). Chạy vài giây.
- `scripts/check_submission.py` kiểm tra tự động: đủ 5 thành viên, đủ 5 báo cáo và 5 mục mỗi báo cáo, file được dẫn có tồn tại, số trong báo cáo khớp bảng sinh từ `results.csv`, và các claim C1–C5 (công thức v×Δt đúng/sai).

## Cấu trúc

| Đường dẫn | Nội dung |
|---|---|
| [design/benchmark_design.md](design/benchmark_design.md) | Thiết kế Bước 1 + bảng Bước 3 (viết trước khi chạy, điền bằng chứng sau) |
| [SOURCES.md](SOURCES.md) | Nguồn thực sự đã đọc và mức đọc |
| [src/run_benchmark.py](src/run_benchmark.py) | Benchmark |
| [results/](results/) | CSV, bảng, log, plot, timeline |
| [failure_case.md](failure_case.md) | Failure case: phanh gấp làm bộ bù vận tốc không đổi sai |
| [reports/](reports/) | 5 báo cáo cá nhân member_1..5 |
| [pitch/pitch_script.md](pitch/pitch_script.md) | Kịch bản pitch 3–5 phút |
| [pitch/TSV_T4_slide.pdf](pitch/TSV_T4_slide.pdf) | Slide: trang 1 là bản 1 trang, trang 2–4 là hình (nguồn: [TSV_T4_slide.html](pitch/TSV_T4_slide.html)) |
| [docs/team_explainer.md](docs/team_explainer.md) | Giải thích cho cả nhóm + câu hỏi giảng viên |
| [CHECKLIST.md](CHECKLIST.md) | Đối chiếu tự kiểm Bước 6 và rubric |

## Giới hạn quan trọng

Kết luận chỉ đúng trong phạm vi dữ liệu tổng hợp và các tham số trong [results/params.json](results/params.json) (nhiễu 0.10 m, 10 Hz, Δt biết chính xác, quỹ đạo thẳng). Chưa chạy trên dữ liệu thật; chưa làm phần mở rộng rolling-shutter.
