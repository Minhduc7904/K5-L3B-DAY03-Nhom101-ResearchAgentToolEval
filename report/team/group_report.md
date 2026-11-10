# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm: nhóm 101
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3: OpenAI / gpt-4o-mini

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì (cho team khác hiểu nhanh).

Ví dụ: "Research agent: tìm tin theo từ khóa / theo tài khoản, đọc URL, tổng hợp thành digest, và gửi lên Telegram khi được xác nhận."

**Cách chạy UI:**

> Lệnh chạy UI (ví dụ `streamlit run app.py`) và dependency đã thêm vào `starter_v0/requirements.txt`.

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL:

### A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
|  |  |  |
|  |  |  |

### A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1.
2.
3.

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

-

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đo hành vi chưa tối ưu trước khi sửa | n/a | 0.65 (13/20) | `runs/v0_B_base_openai_20261110T172311282476.json` |
| v1 | system_prompt.md | Bỏ chỉ dẫn xấu (đoán / gửi ngay / một bước), thêm rule `clarify` khi thiếu thông tin và xác nhận trước `send`; không đụng `tools.yaml` | 0.65 | 0.75 (15/20) | `runs/v1_B_base_openai_20261110T175547880942.json` |
| v2 | tools.yaml | Viết rõ khi nào dùng/không dùng cho từng tool; chuẩn hóa convention args (response_type='text'/'yes_no', handle không '@', topic, timeframe) | 0.75 | 0.90 (18/20) | `runs/v2_B_base_gemini_20261110T182232420866.json` |
| v3 |  |  |  |  |  |

Các chỉ số chi tiết (từ `summary` trong run JSON):

| Version | case_accuracy | tool_routing | argument | multiturn | Case FAIL |
|---|---:|---:|---:|---:|---|
| v0 | 0.65 | 0.70 | 0.65 | 1.000 | R03, R08, R10, R11, R12, R13, R14 |
| v1 | 0.75 | 0.90 | 0.75 | 0.667 | R10, R11, R12, M02, M06 |
| v2 | 0.90 | 1.00 | 0.90 | 1.000 | R03, R12 |

Nhận xét v2 (dựa trên run JSON):

- **Độ chính xác tăng vượt bậc từ 75% lên 90% (18/20 case PASS)**.
- **Tool routing đạt 100% (20/20 case)**: Agent không còn bất kỳ lỗi chọn sai tool nào.
- **Multiturn accuracy đạt 100%**: Sửa hoàn toàn lỗi hồi quy ở M02 và M06 nhờ phân định rạch ròi phạm vi giữa `lookup` (tìm web) và `social_search` (tìm mạng xã hội).
- **Sửa thành công R10 và R11**: Model đã điền chính xác `response_type="text"` khi gọi `clarify` nhờ mô tả chi tiết quy ước trong `tools.yaml`.
- Chỉ còn 2 case chưa hoàn hảo: `R03` (query dư chữ) và `R12` (boundary xác nhận của `send`).

Nhận xét v1 (dựa trên run JSON):

- Sửa được R03, R08, R13, R14. R08 và R14 chỉ "PASS" vì không còn gọi tool; agent vẫn trả lời thẳng bài toán/code thay vì từ chối, harness không phân biệt được nên cần review thủ công.
- Giả thuyết ban đầu "sẽ sửa R10, R11, R12" **không đúng**: ba case này đã gọi đúng `clarify` (không còn đoán hay gửi ngay) nhưng vẫn FAIL vì model bỏ trống `response_type` (case mong `text` / `yes_no`). Đây là lỗi quy ước tham số thuộc `tools.yaml`, sẽ xử lý ở v2.
- Prompt v1 gộp nhiều thay đổi (đổi persona, bỏ đoán, thêm rule `clarify`, bỏ "gửi ngay / một bước"); R03 và R13 được sửa dù prompt không nói về `topic` / `query`, nên chưa thể kết luận do giả thuyết hay do nhiễu.
- Hai case multi-turn M02 và M06 hồi quy (từ PASS sang FAIL): model gọi `social_search` thay vì `lookup`. **Chưa kiểm chứng nguyên nhân**; giả thuyết là mô tả `lookup` / `social_search` mơ hồ, có thể bị đẩy thêm bởi rule "never assume". Mẫu nhỏ (1 run, 6 case multi-turn).

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

Run v0: `starter_v0/runs/v0_B_base_openai_20261110T172311282476.json` (gpt-4o-mini, 20 case, `provider_error_cases=0`, `measured_cases=20`). Fix là kế hoạch cho v1–v3, chưa kiểm chứng.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03_web_news_routing | wrong_arg_value (harness gán `wrong_tool`; tool đúng, chỉ `query` sai) | `lookup(query="AI news", topic="news", timeframe="day")` | `query` thừa chữ "news" (expected `AI`) | `tools.yaml`: tin tức đi vào `topic=news`, không đưa "news" vào `query` |
| R13_parallel_web_and_tweets | wrong_tool | `lookup(query="AI news")` + `timeline(sama)` | Thiếu `topic=news`, query thừa "news", gọi `timeline` thay vì `social_search`, thiếu `social_search` | `tools.yaml`: phân biệt `timeline` (theo tài khoản) và `social_search` (theo từ khóa); thêm rule routing trong prompt |
| R08_out_of_scope | out_of_scope | `send(text="Nguyên hàm của x^2 ...")` | Câu hỏi toán ngoài phạm vi mà agent vẫn gọi `send` | `system_prompt.md`: từ chối/trả lời ngoài phạm vi, không gọi tool |
| R14_out_of_scope_coding | out_of_scope | `send(text="Dưới đây là hàm Fibonacci ...")` | Yêu cầu viết code ngoài phạm vi mà agent vẫn gọi `send` | Giống R08 |
| R10_missing_handle | missing_info | `timeline(screenname="sama")` | Không có handle trong request nhưng agent tự đoán `sama` thay vì `clarify` | `system_prompt.md`: thiếu tham số bắt buộc thì gọi `clarify`, không đoán |
| R11_missing_url | missing_info | `fetch(url="https://example.com/article")` | Không có URL nhưng agent bịa URL thay vì `clarify` | Giống R10 |
| R12_confirm_before_send | wrong_boundary | `send(text="Bản tin mới nhất đã được cập nhật!")` | Gửi ngay mà chưa xin xác nhận | `system_prompt.md` + mô tả `send` trong `tools.yaml`: chỉ gửi khi user đã xác nhận (`confirmed=true`), nếu chưa thì `clarify` |

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/<tên>/`) |  |  |  |
| Unit test tool mới (≥ 3 test/tool) | `pytest` output (0 failed) |  |  |
| UI (lệnh chạy + link dùng thử) |  |  |  |

Tool unit tests: số test đã viết, và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 |  |  |
| Hơn 3 tool mới (≥ 4) |  |  |  |
| `send` gửi thật lên Telegram sau xác nhận | transcript |  |  |
| Test challenge (0 skipped / regression test) | `pytest` output |  |  |

Test challenge: số bug tìm được trong tool có sẵn (nếu có), cách sửa, và test regression tương ứng.

### B7. Small Local Model Challenge (bonus)

Chỉ điền nếu nhóm làm bonus này.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?

## 5. Khó khăn và cách xử lý

> Khó khăn chính và cách nhóm xử lý. Nếu gặp lỗi kỹ thuật (provider lỗi, hết quota API, tool không chạy), mô tả lỗi và dẫn bằng chứng: run JSON, log, ảnh chụp.

-

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào cần review thủ công thay vì chấm tự động?
- Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?

## 8. Tài liệu tham khảo

-
