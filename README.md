# K4-Track4-Day04 – Sensor Reality Sprint (T4: lệch thời gian đa sensor)

Nhóm: TSV – thành viên xem [TEAMMATES.md](TEAMMATES.md).
Chủ đề T4 · xe ADAS · camera + LiDAR · **dữ liệu tổng hợp** (mô phỏng 2D, không phải dữ liệu thật).

Câu hỏi của nhóm: LiDAR lệch 50–200 ms so với camera thì sai vị trí bao nhiêu, bù chuyển động giảm được bao nhiêu, và khi nào giả định "tốc độ không đổi" không còn đúng?

## Cài đặt

Python 3.11 (nhóm chạy với 3.11.7), cần numpy, pandas, matplotlib.

```bash
pip install -r requirements.txt
```

## Chạy lại toàn bộ kết quả (một dòng)

```bash
python src/run_benchmark.py && python scripts/check_submission.py
```

(Windows PowerShell 5.1 không có `&&`, dùng `python src/run_benchmark.py; python scripts/check_submission.py`.)

- `src/run_benchmark.py` là file chạy duy nhất (seed 42). Nó ghi vào `results/`: `results.csv`, `summary_tables.md`, `thresholds.csv`, `params.json`, `run_log.txt` và 4 ảnh PNG (`error_vs_offset.png`, `comp_vs_uncomp.png`, `failure_braking.png`, `timeline_offset200ms.png`). Chạy mất vài giây.
- `scripts/check_submission.py` kiểm tra tự động: đủ 5 thành viên, đủ 5 báo cáo và 5 mục mỗi báo cáo, các file được dẫn đều tồn tại, số trong báo cáo khớp với bảng sinh từ `results.csv`, và các claim C1–C5 (công thức v×Δt đúng hay sai ở đâu).

## Cấu trúc thư mục

| Đường dẫn                                           | Nội dung                                                                                                  |
| ------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| [design/benchmark_design.md](design/benchmark_design.md) | Thiết kế Bước 1 và bảng Bước 3 (viết trước khi chạy, điền kết quả sau)                     |
| [SOURCES.md](SOURCES.md)                                 | Các nguồn nhóm thật sự đã đọc và mức đọc                                                      |
| [src/run_benchmark.py](src/run_benchmark.py)             | Code benchmark                                                                                             |
| [results/](results/)                                     | CSV, bảng, log, hình, timeline                                                                           |
| [failure_case.md](failure_case.md)                       | Failure case: phanh gấp làm bộ bù vận tốc không đổi bù sai                                       |
| [reports/](reports/)                                     | 5 báo cáo cá nhân                                                                                      |
| [pitch/pitch_script.md](pitch/pitch_script.md)           | Kịch bản pitch 3–5 phút                                                                                |
| [pitch/TSV_T4_slide.pdf](pitch/TSV_T4_slide.pdf)         | Slide: trang 1 là bản 1 trang, trang 2–4 là hình (nguồn:[TSV_T4_slide.html](pitch/TSV_T4_slide.html)) |
| [docs/team_explainer.md](docs/team_explainer.md)         | Giải thích cho cả nhóm kèm câu hỏi giảng viên có thể hỏi                                       |
| [CHECKLIST.md](CHECKLIST.md)                             | Đối chiếu tự kiểm và rubric                                                                          |

## Lưu ý về phạm vi

Kết luận chỉ đúng với dữ liệu tổng hợp và các tham số trong [results/params.json](results/params.json) (nhiễu 0.10 m, 10 Hz, biết chính xác Δt, quỹ đạo thẳng). Nhóm chưa chạy trên dữ liệu thật và chưa làm phần mở rộng rolling-shutter.
