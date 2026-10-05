# CHECKLIST – tự kiểm và rubric

Lưu ý: nội dung gốc của "Bước 6" trong đề **không được cung cấp** cho nhóm khi làm repo này; các mục dưới đây được dựng lại từ phần tóm tắt đề (yêu cầu nộp bài, spec T4, ràng buộc). Nhóm nên đối chiếu với đề gốc trên VLearn.

## Tự kiểm

| # | Mục | Kết quả | Bằng chứng / lý do |
|---|---|---|---|
| 1 | Chọn đúng MỘT chủ đề (T4) | PASS | [design/benchmark_design.md](design/benchmark_design.md) |
| 2 | Nhóm đúng 5 thành viên, họ tên + MSSV | PASS | [TEAMMATES.md](TEAMMATES.md): đủ 5 người có tên + MSSV |
| 3 | Thiết kế (Bước 1 + Bước 3) viết trước khi chạy code | PASS | [design/benchmark_design.md](design/benchmark_design.md) (claim C1–C5 ghi trước; bằng chứng điền sau) |
| 4 | Benchmark có đối chứng: baseline + ≥ 3 mức lỗi, tên bằng tham số thật | PASS | baseline 0 ms, offset 50/100/150/200 ms: [results/results.csv](results/results.csv) |
| 5 | ≥ 1 metric định lượng có đơn vị | PASS | RMSE (m), bias (m), tỉ số, % giảm: [results/summary_tables.md](results/summary_tables.md) |
| 6 | Seed cố định, một entrypoint | PASS | [src/run_benchmark.py](src/run_benchmark.py) (seed 42), [results/params.json](results/params.json) |
| 7 | Sai số trước/sau bù chuyển động | PASS | Bảng A, [results/comp_vs_uncomp.png](results/comp_vs_uncomp.png) |
| 8 | Kiểm xấp xỉ v×Δt và ghi khi giả định sai | PASS | C1 tỉ số 0.999–1.000; C3 lệch khi phanh: [design/benchmark_design.md](design/benchmark_design.md), kiểm tự động bằng [scripts/check_submission.py](scripts/check_submission.py) |
| 9 | Timeline multi-sensor | PASS | [results/timeline_offset200ms.png](results/timeline_offset200ms.png) |
| 10 | Plot có nhãn trục + đơn vị | PASS | [results/error_vs_offset.png](results/error_vs_offset.png), [results/comp_vs_uncomp.png](results/comp_vs_uncomp.png), [results/failure_braking.png](results/failure_braking.png) (plot không dấu tiếng Việt) |
| 11 | Ngưỡng đáng lo trong tình huống nhóm đặt | PASS | Bảng E ([results/thresholds.csv](results/thresholds.csv)); ngưỡng 0.5 m là giả định nhóm |
| 12 | Một failure case đủ: cấu hình, số baseline, số lỗi, hệ quả, limitation, giả thuyết có nhãn, cải tiến/fallback, metric kiểm chứng | PASS | [failure_case.md](failure_case.md) (ngưỡng chuyển fallback "chưa xác định") |
| 13 | SOURCES.md chỉ ghi nguồn thực sự đọc, ghi mức đọc | PASS (có hạn chế) | [SOURCES.md](SOURCES.md): 1 nguồn đọc qua bản trích xuất HTML, 1 nguồn chỉ abstract; commit repo "chưa xác minh"; nguồn gợi ý S5/S7/S9 chưa đọc |
| 14 | Tách "Nhóm quan sát được / Paper cho biết / Giả thuyết"; không ghép số paper với số nhóm | PASS | [failure_case.md](failure_case.md), [reports/](reports/) |
| 15 | Dữ liệu tổng hợp được ghi rõ + tham số tạo dữ liệu + lý do proxy hợp lý | PASS | [results/params.json](results/params.json), [README.md](README.md), mục "Vì sao benchmark mô phỏng là proxy hợp lý" trong [design/benchmark_design.md](design/benchmark_design.md) |
| 16 | 5 báo cáo riêng, đủ 5 mục, nhấn vai trò khác nhau | PASS (nội dung) | [TV1](reports/LamQuangAnhQuan_2A202602467.md), [TV2](reports/NgoGiaQuoc_2A202602757.md), [TV3](reports/DinhQuocBao_2A202602933.md), [TV4](reports/NguyenThanhNam_2A202602827.md), [TV5](reports/TranLongKhanh_2A202602538.md). Lưu ý: tên file không thống nhất với `member_N.md` của đề (checker nhận theo tiêu đề); xác nhận cách đặt tên với giảng viên |
| 17 | Mọi file/plot được dẫn đều tồn tại; số báo cáo khớp CSV | PASS | `python scripts/check_submission.py` |
| 18 | Pitch 3–5 phút, thứ tự problem → method → benchmark → failure → decision, có thời lượng | PASS (kịch bản) | [pitch/pitch_script.md](pitch/pitch_script.md) – 4:30, **chưa diễn tập bấm giờ thật** |
| 19 | team_explainer có 8–10 câu hỏi giảng viên + gợi ý trả lời | PASS | [docs/team_explainer.md](docs/team_explainer.md) (10 câu) |
| 19b | 1 trang/slide ngắn theo mẫu (Problem/Method/Benchmark/Failure case/Engineering decision) | PASS (HTML + PDF, không phải .pptx) | [pitch/TSV_T4_slide.html](pitch/TSV_T4_slide.html), [pitch/TSV_T4_slide.pdf](pitch/TSV_T4_slide.pdf) – trang 1 là bản 1 trang, trang 2–4 là hình minh họa. Nhóm quyết định không cài công cụ tạo .pptx; nếu đề bắt buộc .pptx thì cần dựng thủ công hoặc cài python-pptx |
| 20 | README có lệnh một dòng tái hiện | PASS | [README.md](README.md) |
| 21 | Chạy lại từ đầu trên bản sạch, exit 0 | PASS (lần chạy 2026-10-05) | Xem mục "Kiểm tra bản sạch" bên dưới; checker hiện "TẤT CẢ PASS" |
| 22 | Ghost rate / trajectory residual (nếu có dữ liệu phù hợp) | N/A | Không có dữ liệu phù hợp; nhóm chỉ đo sai số dư sau bù (RMSE), không đo ghost rate |
| 23 | Mở rộng rolling-shutter line delay (chỉ sau khi xong phần tối thiểu) | N/A – chưa làm | Tùy chọn; ghi là việc vòng sau trong [failure_case.md](failure_case.md) |
| 24 | Nộp bài trên VLearn | **FAIL (nhóm tự làm)** | Trợ lý không được phép nộp/đăng nhập VLearn; hạn 06/10/2026 11:59 (giờ VN) |

## Rubric

| Tiêu chí | Trọng số | Tự đánh giá | Bằng chứng |
|---|---|---|---|
| Benchmark/demo chạy được | 40% | PASS | `python src/run_benchmark.py` → [results/](results/) |
| Hiểu failure thực tế | 25% | PASS (giới hạn: dữ liệu tổng hợp, chưa có dữ liệu thật) | [failure_case.md](failure_case.md) |
| Giải thích thuật toán | 20% | PASS | [docs/team_explainer.md](docs/team_explainer.md) |
| Trade-off | 15% | PASS | cửa sổ N ngắn/dài, comp_cv vs comp_ca: [failure_case.md](failure_case.md) mục 6, Bảng C |

## Kiểm tra bản sạch

Ngày 2026-10-05: sao chép repo (không có `results/`) sang thư mục tạm, chạy `python src/run_benchmark.py && python scripts/check_submission.py` → exit code 0, "TAT CA PASS"; `results.csv` và `summary_tables.md` giống hệt (hash SHA-256) bản chạy gốc. Hạn chế: dùng chung môi trường Python hiện có (Python 3.11.7, numpy 2.4.6, pandas 3.0.5, matplotlib 3.11.2), **chưa** thử trong virtualenv mới cài từ `requirements.txt`.
