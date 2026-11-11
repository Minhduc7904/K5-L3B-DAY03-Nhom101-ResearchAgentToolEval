# Báo cáo cá nhân — NguyenMinhDuc-2A202603751

## 1. Thông tin thành viên

- Họ tên: Nguyễn Minh Đức
- MSSV: 2A202603751
- GitHub: [Minhduc7904](https://github.com/Minhduc7904)
- Nhóm: nhóm 101 — Lớp L3B

## 2. Phần việc phụ trách

- **CP1:** chạy baseline `v0` hợp lệ trên OpenAI gpt-4o-mini và phân tích lỗi (bảng B2).
- **CP2:** vòng `v1` (sửa `system_prompt.md`); sau đó chạy lại `v2` và viết lại `v3` trên cùng model OpenAI để cả chuỗi `v0 → v3` so sánh được với nhau.
- **CP4:** viết 10 case eval của nhóm (`data/eval_group.json`) và điền bảng B3.
- **CP5:** mở link dùng thử qua Cloudflare Tunnel, chat thử ba phiên với prompt v3, điền các mục còn lại của `group_report.md`.

## 3. Đóng góp cụ thể

### CP1 — Baseline v0
- Dùng chung `.venv` ở thư mục gốc cho cả khóa, cài thư viện của lab vào đó; chạy preflight (`--provider openai`) và `pytest` (contract và example xanh, test TODO còn skipped).
- Chạy base eval `v0` (20 case): `case_accuracy` 0.65, `provider_error_cases = 0`, `measured_cases = 20`. Phân loại 7 case FAIL (R03, R08, R10, R11, R12, R13, R14) theo loại lỗi và nguyên nhân (bảng B2). Kết luận: cả 7 lỗi khớp với ba chỉ dẫn xấu cố ý của prompt starter (đoán thay vì hỏi, gửi ngay, ép một bước).
- Ghi dòng `v0` vào `version_log.csv` và B1, B2.

### CP2 — v1, v2, v3 trên cùng một model
- **v1** (chỉ sửa `system_prompt.md`): bỏ ba chỉ dẫn xấu, thêm rule `clarify` khi thiếu thông tin và xin xác nhận trước `send`. Kết quả 0.65 → 0.75. Đo được: R10, R11, R12 đã gọi đúng `clarify` nhưng vẫn FAIL vì model bỏ trống `response_type` (lỗi quy ước tham số, thuộc `tools.yaml`); và hai case multi-turn M02, M06 hồi quy.
- Khi nhận `tools.yaml` v2 và prompt v3 của Nam (chạy trên Gemini), tôi thấy chuỗi bị lẫn hai model (v0 và v1 trên OpenAI, v2 và v3 trên Gemini) nên mức tăng không so sánh được. Tôi **chạy lại v2 trên OpenAI** (0.75 → 0.95) và giữ các run Gemini làm tham khảo (`v0-gemini`, `v2-gemini`, `v3-gemini` trong `version_log.csv`).
- Chạy lại prompt v3 gốc của Nam trên OpenAI: base 20/20 nhưng bộ group chỉ 8/10 (G06, G09), và prompt chép nguyên văn câu của case R12 cùng ví dụ "AI", "tuần này" — dấu hiệu tune theo bộ base. Tôi **viết lại v3** bỏ phần chép từ eval, thêm luật "đã xác nhận rõ thì gửi `confirmed=true`, không hỏi lại". Kết quả v3: base 0.95, group 0.90; chạy thêm run đối chứng `v2-artifact` (group 10/10) nên biết G09 là hồi quy do prompt v3. Ghi rõ trong báo cáo là v3 không tăng điểm base và gộp 4 thay đổi.
- Sau khi nhờ một agent chấm độc lập (86/100, không tính bonus), tôi thử sửa hai điểm yếu còn lại là R10 và G09 bằng **hai version, mỗi version đúng một rule**:
  - **v4** (rule "chỉ xử lý yêu cầu ở lượt cuối"): bị bác bỏ. Base 0.95 / 1.00 / 0.95, R10 vẫn FAIL 2/3 lần; group 0.90 / 0.90, G09 FAIL cả 2 lần. Harness đã dặn model dùng lượt trước làm ngữ cảnh nên rule bị trùng.
  - **v5** (rule "mỗi nhu cầu chỉ gọi một tool tìm kiếm, trừ khi user nói rõ muốn nhiều nguồn"): base 1.00 / 1.00, R10 PASS 2/2 (R13 vẫn PASS), nhưng group vẫn 0.90 / 0.90 vì G09 vẫn FAIL (gọi thêm `social_search` sau `lookup`). R10 có khả năng đã sửa nhưng chưa đủ lần chạy để chắc chắn; G09 chưa sửa. Giả thuyết cho vòng sau: bỏ chữ `social_search` khỏi câu rule `query` của prompt v3 (prompt v2 không có câu đó và PASS G09).
- Cập nhật `version_log.csv` (các dòng `v1`, `v2`, `v3`, `v3-nam`, `v2-artifact`, `v4`, `v5` và các dòng Gemini tham khảo) và B1, B2 trong `group_report.md`.

### CP4 — Eval nhóm
- Viết `data/eval_group.json`: 10 case (5 single turn, 5 multi turn), mỗi case có `failure_type`, `expect`, `metadata.what_it_tests`. Phủ các điểm bộ base chưa có: xác nhận gửi, hủy gửi, bỏ `@` ở handle, `timeframe=month`, chuyển tool giữa chừng, và 4 case cho tool `artifact` của Quang (2 nên gọi, 2 không nên gọi). Test `tests/test_tool_contract.py` xanh sau khi thêm.
- Chạy `--suite group` và điền bảng B3 (v3: 9/10, v3 gốc của Nam: 8/10, đối chứng v2-artifact: 10/10).

### CP5 — Demo và báo cáo
- Build giao diện web của Quang, cài `cloudflared`, chạy `server.py --provider openai --version v3` và mở link `trycloudflare.com` cho nhóm khác dùng thử (đã kiểm tra link trả HTTP 200).
- Chat thử ba phiên với v3 (yêu cầu thường; thiếu URL rồi bổ sung; yêu cầu gửi → xin xác nhận → `send`), quét khóa API trong transcript rồi commit.
- Sau đó cấu hình Telegram trên máy tôi và chat lại một phiên trên OpenAI (prompt v5): "gửi qua tele cho tôi" → `clarify(yes_no)` → "ok" → `send(confirmed=true)` → `status: sent`. Transcript này ban đầu có tên `v3` do tôi bật máy chủ với `--version v3`, nhưng hash là của prompt v5 nên tôi đổi tên và nhãn thành `v5`. Tôi cũng sửa nhãn hai transcript `v0_openai_web_*` bị gắn nhầm thành `v3` vì hash trong file là của v3 (một transcript v0 thật được giữ nguyên); việc sửa nhãn đã ghi ở B4.
- Điền các mục còn lại của `group_report.md`: A1 (link, lệnh chạy), mục 3, B4 (ba phiên OpenAI), B5 (ghi rõ các bonus không đạt), mục 5, B6, mục 8.

## 4. Bằng chứng

- File/commit/PR (repo `Minhduc7904/K5-L3B-DAY03-Nhom101-ResearchAgentToolEval`, nhánh `main`):
  - `7917383` CP1: baseline v0 (gpt-4o-mini) và failure analysis
  - `5e17791` CP2: v1 — viết lại system prompt
  - `f658144` CP2/CP4: chạy lại v2 trên OpenAI, thêm 10 case group, sửa báo cáo
  - `72a563b` CP2: v3 trên OpenAI, viết lại case group, sửa báo cáo và log
  - `fc7de23` CP4: điền bảng B3
  - `c049372` CP5: điền các mục báo cáo nhóm và thêm transcript v3
  - `a06a325` thêm vòng v4/v5 (R10, G09), sửa nhãn transcript, cập nhật báo cáo nhóm và `TEAM.md`
  - `37d6338` thêm transcript gửi Telegram thành công trên OpenAI (v5) và cập nhật B4, B5
- Run (đều `provider_error_cases = 0`, `measured_cases = total_cases`, trong `starter_v0/runs/`):
  - `v0_B_base_openai_20261110T172311282476.json` (0.65)
  - `v1_B_base_openai_20261110T175547880942.json` (0.75)
  - `v2_B_base_openai_20261110T183148819703.json` (0.95)
  - `v3_B_base_openai_20261110T184941408701.json` (0.95), `v3_B_group_openai_20261110T185010179172.json` (0.90)
  - Đối chiếu: `v3-nam_B_*_openai_*.json`, `v2-artifact_B_group_openai_20261110T184249362732.json`
  - Vòng sau: `v4_B_base_openai_*.json` (3 run), `v4_B_group_openai_*.json` (2 run), `v5_B_base_openai_*.json` (2 run), `v5_B_group_openai_*.json` (2 run); danh sách đầy đủ trong `starter_v0/artifacts/version_log.csv`.
- Transcript: `starter_v0/transcripts/v3_openai_web_20261110T191013015667`, `…191400882629`, `…191448500175` (`.transcript.json`); `v5_openai_web_20261111T093140281155` (gửi Telegram thành công); `v3_openai_web_20261110T194302105068` và `…194701705690` (phiên thử, đã sửa nhãn từ v0).
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:
  - Dùng **Claude Code** để hỗ trợ đọc đề, viết lại prompt, viết case eval, chạy lệnh và soạn báo cáo. Tôi không tin kết quả của AI mà kiểm tra bằng:
  - **Đọc số liệu từ run JSON** (`summary`, `provider_error_cases`, `measured_cases`, `prompt_hash`, `tools_hash`, `actual_tool_calls`), không dựa vào phần AI tóm tắt.
  - **Hai lần cho một agent khác review độc lập** (chỉ đọc file, không sửa): lần 1 phát hiện giả thuyết v1 "sẽ sửa R10–R12" đã bị run bác bỏ và R03 nên là `wrong_arg_value`; lần 2 phát hiện v2 so sánh khác model và `tools.yaml` có chép ví dụ từ eval; lần 3 phát hiện báo cáo v3 bỏ sót run đối chứng `v2-artifact`. Tôi sửa báo cáo theo từng lần. Lần chấm độc lập cuối (86/100, không tính bonus) chỉ ra các điểm yếu còn lại: mỗi version gộp nhiều thay đổi, R10 và G09 chưa xử lý, nhãn transcript sai, `TEAM.md` thiếu thông tin; tôi xử lý được phần lớn ở vòng v4/v5 và phần ghi chú.
  - **Chạy `pytest`** (78 passed, 14 skipped, 0 failed) và **quét khóa API** trong run, transcript trước khi commit; kiểm tra link dùng thử từ bên ngoài.

## 5. Tự đánh giá

- **Làm tốt:** giữ cả chuỗi `v0 → v3` trên một model nên so sánh được; ghi trung thực những chỗ không chắc (v3 không tăng điểm base, thay đổi gộp nhiều phần, một run mỗi cấu hình); phát hiện bản v3 gốc tune theo bộ base nhờ bộ group; mọi con số trong báo cáo trỏ được tới file run.
- **Chưa tốt / bài học:**
  - v1 và v3 gộp nhiều thay đổi nên không tách được đóng góp từng rule; lẽ ra nên chia thành các version nhỏ hơn.
  - Phát hiện lệch model và overfit muộn, khi các thành viên đã chạy xong v2, v3 trên Gemini; nên thống nhất provider/model ngay từ CP1.
  - Chưa làm bonus nào (Small Local Model, ≥ 4 tool, test challenge). G09 vẫn FAIL sau hai version (v4, v5); R10 có khả năng đã sửa ở v5 nhưng mới có 2 lần chạy. Nhóm chưa thêm rule routing vào `system_prompt.md` và chưa thêm "KHÔNG DÙNG KHI" cho `format`, `papers`, `paper_text`.
  - Ban đầu máy tôi chưa cấu hình Telegram nên lượt `send` trong phiên A bị lỗi; sau đó tôi cấu hình và chạy lại, có transcript `status: sent` trên OpenAI.
- **Nếu làm lại:** chốt provider/model và `.gitattributes` (để `prompt_hash`/`tools_hash` không đổi giữa các máy) trước khi chạy v0; chạy mỗi cấu hình nhiều lần để ước lượng nhiễu; viết bộ eval nhóm trước khi sửa prompt để tránh tune theo bộ base.
