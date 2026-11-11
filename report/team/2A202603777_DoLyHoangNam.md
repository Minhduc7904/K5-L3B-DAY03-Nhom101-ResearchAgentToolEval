# Báo cáo cá nhân — Đỗ Lý Hoàng Nam - 2A202603777

## 1. Thông tin thành viên

- Họ tên: Đỗ Lý Hoàng Nam
- MSSV: 2A202603777
- Email: dolyhoangnam13072005@gmail.com
- GitHub: [DoLyHoangNam](https://github.com/DoLyHoangNam)
- Nhóm: Nhóm 101 — Lớp L3B

## 2. Phần việc phụ trách

- **Checkpoint 1 (CP1):** Cấu hình môi trường thực thi, thiết lập API keys, chạy kiểm thử provider/contract test, thực hiện chạy đánh giá Baseline `v0` hợp lệ (20/20 cases) và phân tích các trường hợp lỗi (Failure Analysis).
- **Checkpoint 2 (CP2 - Version 2 & Version 3):** Trực tiếp thực hiện 2 vòng lặp tối ưu quan trọng:
  - **Version 2 (`v2`):** Tối ưu hóa file khai báo công cụ [`starter_v0/artifacts/tools.yaml`](file:///c:/Users/admin/LabTeam/TH%20day%2003/K5-L3-DAY03-ResearchAgentToolEval/starter_v0/artifacts/tools.yaml), phân định ranh giới sử dụng và chuẩn hóa tham số, nâng accuracy lên 90%.
  - **Version 3 (`v3`):** Tinh chỉnh [`starter_v0/artifacts/system_prompt.md`](file:///c:/Users/admin/LabTeam/TH%20day%2003/K5-L3-DAY03-ResearchAgentToolEval/starter_v0/artifacts/system_prompt.md) để giải quyết triệt để 2 lỗi biên cuối cùng, đưa toàn bộ hệ thống đạt điểm tuyệt đối **100% (20/20 cases PASS)**.

## 3. Đóng góp cụ thể

### 1. Checkpoint 1 — Thiết lập & Chạy Baseline `v0`
- Thiết lập môi trường ảo Python `.venv`, xử lý cài đặt đầy đủ các thư viện (`google-genai`, `requests`, `PyYAML`, `pypdf`, `pytest`).
- Cấu hình file `starter_v0/.env` với các API keys cho provider và các công cụ nghiên cứu (Gemini, Tavily, Firecrawl, RapidAPI Twitter API45).
- Chạy kiểm tra preflight và đảm bảo 55/55 contract tests trong `tests/test_tool_contract.py` pass 100%.
- Chạy bộ đánh giá baseline `v0` (20 cases) đạt chuẩn hợp lệ (`measured_cases = 20`, `provider_error_cases = 0`, case accuracy: 65%).
- Phân tích chi tiết 7 failure cases ban đầu do prompt starter xúi giục đoán mò và gửi tin không an toàn; điền dòng `v0` vào `artifacts/version_log.csv` và bảng B1, B2 trong `report/team/group_report.md`.
- Commit và push minh chứng CP1 lên Git: commit `af28f33` (`checkpoint 1`).

### 2. Checkpoint 2 — Tối ưu hóa Version 2 (`v2`)
- **Phân tích vấn đề từ `v1`:** Nhận diện 5 case thất bại ở `v1` (R10, R11, R12, M02, M06) chủ yếu do khai báo tool trong `tools.yaml` còn mơ hồ, thiếu quy ước tham số `response_type` dẫn đến model bỏ trống, và ranh giới giữa `lookup` (web search) với `social_search` (mạng xã hội) chưa rõ ràng.
- **Giả thuyết `v2`:** Viết lại toàn bộ mô tả của từng tool trong `tools.yaml`, quy định rõ ràng *khi nào dùng / khi nào KHÔNG dùng*, chuẩn hóa các tham số:
  - Bắt buộc `response_type='yes_no'` khi xin xác nhận, `response_type='text'` khi hỏi thông tin còn thiếu trong `clarify`.
  - Quy ước `screenname` trong `timeline` không chứa ký tự `@`.
  - Phân định rõ `lookup` dành cho tin tức thời sự trên web (`topic='news'`, `timeframe`) và `social_search` dành cho thảo luận cộng đồng trên Twitter/X.
  - Thiết lập ranh giới xác nhận an toàn `confirmed=true` cho `send`.
- **Thực thi và Đo lường:**
  - Cập nhật `starter_v0/artifacts/tools.yaml` và bảo toàn 55/55 test contract `pytest` đều pass.
  - Chạy eval `v2` với 20 cases, đạt kết quả xuất sắc:
    + **Case Accuracy:** Tăng vọt từ **75% lên 90%** (18/20 cases pass).
    + **Tool Routing Accuracy:** Đạt tuyệt đối **100%** (20/20 cases).
    + **Multiturn Accuracy:** Đạt tuyệt đối **100%** (6/6 cases, sửa hoàn toàn lỗi hồi quy M02, M06).
- Ghi nhận dòng `v2` vào `artifacts/version_log.csv` và cập nhật bằng chứng vào bảng B1 của `report/team/group_report.md`.
- Commit và push lên GitHub: commit `c558dc3` (`CP2: v2 - 90% accuracy`).

### 3. Checkpoint 2 — Hoàn thiện đỉnh cao Version 3 (`v3`)
- **Phân tích 2 lỗi cuối ở `v2`:** Case `R03` thất bại do model tự động mở rộng từ khóa 'AI' thành 'Artificial Intelligence news' thay vì giữ từ gốc; Case `R12` thất bại do model tưởng thiếu nội dung nên hỏi `clarify` dạng `text` thay vì xin xác nhận an toàn `yes_no`.
- **Giả thuyết `v3`:** Tinh chỉnh `starter_v0/artifacts/system_prompt.md` với 2 quy tắc sắc bén:
  - Giữ nguyên thực thể/từ khóa gốc khi trích xuất `query` cho công cụ tìm kiếm, không tự dịch hay nối thêm các từ chỉ thời gian/loại tin.
  - Khi người dùng yêu cầu đăng/gửi tin (`send`), coi như nội dung đã có sẵn và BẮT BUỘC gọi `clarify(response_type='yes_no')` để xin xác nhận người dùng.
- **Kết quả đo lường `v3`:** Đạt điểm tuyệt đối **100% (20/20 cases PASS)**. Toàn bộ 4 chỉ số đều đạt 1.0 (Case Accuracy: 100%, Tool Routing: 100%, Argument Accuracy: 100%, Multiturn Accuracy: 100%).
- Cập nhật dòng `v3` vào `artifacts/version_log.csv` và hoàn thiện bảng B1 trong `report/team/group_report.md`.

## 4. Bằng chứng

- **Commits trên GitHub:**
  - `af28f33`: `checkpoint 1` — Cung cấp file run baseline v0 hợp lệ.
  - `c558dc3`: `CP2: v2 - 90% accuracy` — Tối ưu hóa `tools.yaml`, nâng accuracy lên 90%.
  - `cb90f10`: `CP2: v3 - 100% accuracy (20/20 passed)` — Tinh chỉnh `system_prompt.md`, đạt điểm tuyệt đối 100% (20/20 cases).
- **Run Files:**
  - `starter_v0/runs/v0_B_base_gemini_20261110T175736805773.json` (Accuracy: 65%, 20/20 measured).
  - `starter_v0/runs/v2_B_base_gemini_20261110T182232420866.json` (Accuracy: 90%, Routing: 100%, Multiturn: 100%).
  - `starter_v0/runs/v3_B_base_gemini_20261110T183600784007.json` (Accuracy: 100%, Routing: 100%, Multiturn: 100%).
- **Artifacts đã tối ưu:**
  - [`starter_v0/artifacts/tools.yaml`](file:///c:/Users/admin/LabTeam/TH%20day%2003/K5-L3-DAY03-ResearchAgentToolEval/starter_v0/artifacts/tools.yaml)
  - [`starter_v0/artifacts/system_prompt.md`](file:///c:/Users/admin/LabTeam/TH%20day%2003/K5-L3-DAY03-ResearchAgentToolEval/starter_v0/artifacts/system_prompt.md)
  - [`starter_v0/artifacts/version_log.csv`](file:///c:/Users/admin/LabTeam/TH%20day%2003/K5-L3-DAY03-ResearchAgentToolEval/starter_v0/artifacts/version_log.csv)
  - [`report/team/group_report.md`](file:///c:/Users/admin/LabTeam/TH%20day%2003/K5-L3-DAY03-ResearchAgentToolEval/report/team/group_report.md)

## 5. Tự đánh giá

- **Làm tốt:**
  - Hoàn thành thiết lập ban đầu (CP1), giải quyết vấn đề cài đặt dependencies, chạy và xác thực run baseline `v0` hợp lệ 20/20 cases (`provider_error_cases = 0`).
  - Đặt giả thuyết chính xác cho Version 2 (`v2`): viết lại toàn bộ `tools.yaml` với ranh giới sử dụng và quy ước tham số rõ ràng, nâng vọt độ chính xác từ 75% lên 90% trên Gemini (và 95% khi nhóm trưởng chạy lại trên OpenAI), đưa Tool Routing và Multiturn đạt tuyệt đối 100%.
  - Tinh chỉnh `system_prompt.md` ở Version 3 (`v3`) giải quyết triệt để 2 lỗi biên cuối cùng (R03 và R12), giúp agent đạt điểm tuyệt đối 20/20 cases PASS (100% accuracy) trên bộ eval base.
  - Tuân thủ nghiêm ngặt phương pháp evidence-driven: mọi kết luận đều đối chiếu từ run log JSON thật, kiểm tra bộ contract test `pytest` (60 passed) trước mỗi lần commit.

- **Chưa tốt / bài học:**
  - **Lệch model giữa các thành viên:** Tôi chạy chuỗi `v0 → v2 → v3` trên Gemini (`gemini-3.5-flash-lite`), trong khi nhóm trưởng chạy trên OpenAI (`gpt-4o-mini`). Dù kết quả trên cả 2 model đều cải thiện rất mạnh, việc khác provider khiến hai chuỗi số liệu không thể gộp chung thành một đường baseline duy nhất mà phải chạy đối chứng chéo. Bài học: nhóm cần chốt một provider/model cố định ngay từ bước CP1.
  - **Gộp nhiều thay đổi trong một version:** Ở `v2`, việc sửa đồng loạt nhiều tool trong `tools.yaml` (gộp cả quy ước `response_type`, `topic/timeframe` và ranh giới `lookup` vs `social_search`) làm tăng điểm rất nhanh nhưng lại khó bóc tách định lượng xem từng thay đổi đơn lẻ đóng góp bao nhiêu phần trăm.
  - **Hiện tượng Overfitting (tune theo bộ base):** Bản prompt `v3` tinh chỉnh để đạt 20/20 trên `eval_base.json` nhưng khi nhóm chạy thử nghiệm trên bộ `eval_group.json` (10 case mới) thì chỉ đạt 8/10, cho thấy quy tắc prompt bị phụ thuộc một phần vào các trường hợp cụ thể của bộ base mà chưa đạt tính khái quát hóa tối đa.
  - Khác biệt định dạng kết thúc dòng (CRLF trên Windows vs LF trên Linux/macOS) giữa các máy làm hash của prompt/tools bị lệch dù nội dung văn bản giống nhau.

- **Nếu làm lại:**
  - Thống nhất duy nhất một provider/model và cấu hình file `.gitattributes` ngay từ đầu để đồng bộ hash giữa các máy trong nhóm.
  - Tách nhỏ các giả thuyết thành từng bước vi mô (micro-iterations) để đo lường chính xác tác động của từng quy tắc.
  - Luôn kiểm thử chéo đồng thời trên cả bộ eval base lẫn bộ eval mở rộng (hold-out set) sau mỗi lần sửa để tránh thiên lệch (overfitting).
