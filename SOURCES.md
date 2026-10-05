# SOURCES – nguồn thực sự đã đọc

Ngày truy cập tất cả nguồn: **2026-10-05**. Công cụ đọc: WebFetch (trả về bản tóm tắt/trích xuất tự động của trang, không phải toàn văn người đọc). Vì vậy mọi mục dưới đây chỉ ghi những gì công cụ trả về; chưa ai trong nhóm đối chiếu toàn văn PDF.

## Nguồn 1 – Nowicki, *Spatiotemporal Calibration of Camera and 3D Laser Scanner*

| Mục | Nội dung |
|---|---|
| Link | https://arxiv.org/html/2006.16081 (abs: https://arxiv.org/abs/2006.16081) |
| Version | arXiv:2006.16081v2 [cs.RO], 29/08/2020 |
| Commit repo | **Chưa xác minh** (bản tóm tắt nói framework "open-source" nhưng nhóm chưa mở repo, không có commit) |
| Mức đọc | Trang HTML arXiv qua WebFetch (bản trích xuất). Chưa đọc toàn văn kiểm chứng từng công thức. |
| Input → Output | Ảnh camera có phát hiện bàn cờ + point cloud LiDAR có timestamp từng điểm + ước lượng thô ban đầu của phép biến đổi → biến đổi cứng 6-DOF camera–LiDAR và độ lệch thời gian Δt (ms). |
| Mô hình lệch thời gian | Δt được tối ưu đồng thời với biến đổi 6-DOF: `T*, Δt* = argmin Σ π(tᵢ+Δt)ᵀ T pᵢ` (π = mặt phẳng bàn cờ tại thời điểm đã dịch, nội suy B-spline). |
| Metric / dataset | Thực nghiệm: Velodyne VLP-16 + stereo camera (sai số tịnh tiến 0.74 cm, quay 0.97°); SICK MRS6124 + stereo camera (0.8 cm, 3.52°). Mô phỏng: 1900 thí nghiệm ngẫu nhiên. Metric: sai số tịnh tiến (cm), quay (độ), sai số time offset (ms). |
| Yêu cầu chạy | Camera global-shutter đã hiệu chuẩn nội tham số; LiDAR 3D; gắn cứng; bàn cờ; ~1 phút hiệu chuẩn. |
| Limitation do nguồn nêu | Giả định time offset "nhỏ và xấp xỉ không đổi"; kết quả MRS6124 có sai số quay lớn hơn do cảm biến kém chính xác hơn; hiệu năng phụ thuộc độ chính xác cảm biến và lượng dữ liệu. Yêu cầu camera global-shutter (không áp dụng cho rolling-shutter). |
| Phần nhóm tái hiện | **Không tái hiện** thuật toán của paper. Nhóm chỉ dùng paper làm bối cảnh: lệch thời gian camera–LiDAR là vấn đề thực và thường được ước lượng như một hằng số Δt. Nhóm làm **benchmark mô phỏng riêng** (dữ liệu tổng hợp) về hệ quả của Δt lên sai số vị trí. Metric của nhóm là metric thật trên dữ liệu tổng hợp (mét), không phải metric của paper; không so sánh số của nhóm với số của paper. |

## Nguồn 2 – Wang et al., *Temporal and Spatial Online Integrated Calibration for Camera and LiDAR*

| Mục | Nội dung |
|---|---|
| Link | https://arxiv.org/abs/2207.10454 |
| Version | arXiv:2207.10454 v1, nộp 21/07/2022 |
| Commit repo | **Chưa xác minh** |
| Mức đọc | **Chỉ trang abstract** qua WebFetch. Thử lấy PDF (https://arxiv.org/pdf/2207.10454) nhưng công cụ trả về dữ liệu nhị phân không giải mã được → **chưa đọc phần method/limitation**. |
| Input → Output | Không nêu chính thức trong abstract (**chưa xác minh**). |
| Metric / dataset | Theo abstract: đánh giá trên KITTI; hiệu chuẩn thời gian cải thiện độ chính xác 38.5% so với phương pháp "soft synchronization"; hiệu chuẩn không gian sửa sai số trong 0.4 s, độ chính xác 0.3°. |
| Yêu cầu chạy | Chưa xác minh. |
| Limitation do nguồn nêu | Abstract không nêu limitation cụ thể (**chưa xác minh** phần thân bài). |
| Phần nhóm tái hiện | Không tái hiện. Chỉ dùng để xác nhận rằng đồng bộ thời gian camera–LiDAR là bài toán được nghiên cứu cho lái xe tự động. Nhóm không dùng con số 38.5% để so sánh với số của nhóm (khác dữ liệu, khác metric). |

## Nguồn gợi ý của đề – CHƯA ĐỌC

Huai et al. 2021 (S9, rolling-shutter camera-IMU), Dong et al. CVPR 2023 (S5), Galibr 2024 / CalibRefine 2025 / DF-Calib 2025 (S7): **chưa xác minh**, nhóm chưa tìm và chưa đọc. Không dùng bất kỳ nội dung nào từ các nguồn này trong báo cáo.

## Ghi chú

- Kết quả tìm kiếm (WebSearch) chỉ dùng để tìm nguồn; ba bài khác xuất hiện trong kết quả (2207.03704, 2508.12564, 2607.15889) nhóm **không đọc** nên không trích dẫn.
