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
| v2 | tools.yaml (viết lại mô tả nhiều tool, xem ghi chú) | `tools.yaml` mơ hồ (không nói khi nào dùng/không dùng, thiếu quy ước `response_type`, `topic`, handle) là nguyên nhân lỗi còn lại của v1. **Lưu ý: thay đổi gộp nhiều tool, không phải một giả thuyết đơn lẻ** | 0.75 | 0.95 (19/20) | `runs/v2_B_base_openai_20261110T183148819703.json` |
| v3 | system_prompt.md | Viết lại prompt (ý tưởng v3 của Nam) với **4 thay đổi gộp**: `clarify` dùng `response_type="text"` khi thiếu thông tin; rule `query` (giữ từ khóa gốc, không đưa "news"/thời gian vào `query`); luồng xác nhận `send` (hỏi `yes_no`, gửi `confirmed=true` sau khi user xác nhận rõ, hủy thì không gửi); trả lời thẳng khi ngoài phạm vi. Bỏ câu chép từ eval. Không phải một giả thuyết đơn lẻ | 0.95 | 0.95 (19/20) | `runs/v3_B_base_openai_20261110T184941408701.json` |

Các chỉ số chi tiết (từ `summary` trong run JSON):

| Version | case_accuracy | tool_routing | argument | multiturn | Case FAIL |
|---|---:|---:|---:|---:|---|
| v0 | 0.65 | 0.70 | 0.65 | 1.000 | R03, R08, R10, R11, R12, R13, R14 |
| v1 | 0.75 | 0.90 | 0.75 | 0.667 | R10, R11, R12, M02, M06 |
| v2 (OpenAI) | 0.95 | 1.00 | 0.95 | 1.000 | R12 |
| v3 (OpenAI) | 0.95 | 0.95 | 0.95 | 1.000 | R10 |

Nhận xét v2 (dựa trên run JSON `v2_B_base_openai_20261110T183148819703.json`, OpenAI gpt-4o-mini, cùng model với v0 và v1):

- Kết quả: 19/20 PASS (0.95), tool routing 1.00, multiturn 1.00, `provider_error_cases=0`, `measured_cases=20`. Chỉ còn R12 FAIL.
- R10, R11 giờ gọi `clarify` và điền `response_type="text"`; M02, M06 và R03, R13 cũng PASS. Các thay đổi này cùng xảy ra khi `tools.yaml` được viết lại, **nhưng không thể gán riêng cho `response_type`** vì v2 sửa mô tả của nhiều tool cùng lúc (`clarify`, `timeline`, `social_search`, `lookup`, `fetch`, `send`...). Vì vậy v2 không đạt chuẩn "một giả thuyết mỗi version"; đây là một hạn chế của nhóm. Chưa có run cô lập để tách đóng góp từng phần.
- R12 vẫn FAIL: agent gọi `clarify` nhưng với `response_type="text"` (hỏi nội dung bản tin) thay vì `yes_no`. Có thể do case "Đăng bản tin này lên Telegram" chưa có nội dung cụ thể để xác nhận; cần xem lại bằng prompt hoặc ví dụ, không chỉ bằng mô tả tool.
- Rủi ro đo lường: một số ví dụ trong mô tả `tools.yaml` (tên người, URL, chủ đề) trùng nội dung `data/eval_base.json`, nên điểm base của v2 có thể cao hơn thực lực. Cần dùng bộ `eval_group.json` (case do nhóm tự viết) để kiểm tra chéo.
- Run Gemini của Nam (`v0_B_base_gemini_...`, `v2_B_base_gemini_...`, model `gemini-3.5-flash-lite`) chỉ để tham khảo, **không dùng trong chuỗi v0→v3** vì khác model với v0/v1. Gemini v2 đạt 0.90 (18/20), FAIL R03, R12; Gemini v0 đạt 0.65.
- Hash `tools_hash` của cùng một nội dung `tools.yaml` khác nhau giữa các máy (`474f8a0277b2` trên máy Đức, `eb21b1702350` trên máy Nam) vì khác kết thúc dòng CRLF/LF, không phải khác nội dung.

Nhận xét v3 (OpenAI gpt-4o-mini; prompt `718f89bc937b`; base: `v3_B_base_openai_20261110T184941408701.json`, group: `v3_B_group_openai_20261110T185010179172.json`):

- Base: 19/20 (0.95), routing 0.95, multiturn 1.00, `provider_error_cases=0`, `measured_cases=20`. Sửa được R12 (trước đó v2 hỏi `text` thay vì `yes_no`) nhưng **R10 hồi quy** (prompt v2 và prompt gốc của Nam đều PASS R10; nguyên nhân chưa kiểm chứng, mới chỉ có 1 run mỗi cấu hình nên chưa phân biệt được với nhiễu mẫu): với "Tóm tắt 5 tweet mới nhất giúp mình", agent gọi `social_search(query="tweet")` thay vì `clarify`. Vì vậy `case_accuracy` **không tăng** so với v2 (0.95 → 0.95).
- Group (10 case nhóm): 9/10 (0.90). Chỉ G09 FAIL: ở lượt cuối agent gọi đúng `lookup(topic=news, timeframe=day)` nhưng gọi **thêm** `social_search`.
- **Đối chứng `v2-artifact`** (prompt v2 + `tools.yaml` đã có `artifact`, chạy bộ group, run `v2-artifact_B_group_openai_20261110T184249362732.json`): **10/10**, G06 và G09 đều PASS. Nghĩa là trên bộ group, prompt v3 (9/10) và bản gốc của Nam (8/10) **không tốt hơn** prompt v2 cùng tools; G09 là hồi quy do prompt v3, không phải điểm yếu có sẵn. Chưa có run base cho cấu hình `v2-artifact`, nên phần base vẫn lẫn ảnh hưởng của tool `artifact`.
- Chưa thể kết luận v3 tốt hơn v2: (1) mẫu nhỏ, một run; (2) `tools.yaml` đã có thêm tool `artifact` của Quang (tools_hash `198864b46581`) so với v2 (`474f8a0277b2`), nên không hoàn toàn like-for-like.
- So sánh với bản v3 gốc của Nam chạy trên cùng OpenAI (prompt `fe948272671c`, run `v3-nam_B_base_openai_20261110T184712292671.json` và `v3-nam_B_group_openai_20261110T184801942989.json`): base **1.00 (20/20)** nhưng group chỉ **0.80 (8/10)**. Hai case FAIL là G06 (đã được user xác nhận rõ mà agent vẫn hỏi lại `clarify` thay vì `send(confirmed=true)`) và G09. Prompt gốc chép nguyên văn câu của case R12 ("Đăng bản tin này lên Telegram...") cùng các ví dụ `"AI"`, `"tuần này"` trong prompt, và rule "luôn hỏi yes_no" khiến luồng xác nhận gửi bị hỏi lại. Chênh lệch base 1.00 so với group 0.80 là **dấu hiệu** bản gốc tune theo bộ base nhưng chưa chứng minh (chênh 1–2 case, một run mỗi bên; cả hai bản v3 đều FAIL G09 mà prompt v2 qua được).
- Bản v3 chính thức của nhóm là bản đã viết lại (không chép từ eval, có rule không hỏi lại sau xác nhận rõ ràng): G06 PASS nhưng R10 và G09 vẫn là điểm yếu, dự kiến xử lý ở v4.
- Lưu ý bộ case: lượt đầu của G06, G07 trùng nguyên văn câu của R12 và lượt đầu của G09 trùng R01 (chỉ một lượt, không phải cả case). Run `v1_B_group_openai_...` dùng phiên bản cũ của bộ group (có case G05 tên mơ hồ) nên không so sánh trực tiếp với các run group sau này.
- Hash phụ thuộc kết thúc dòng: `system_prompt.md` ghi LF trên đĩa nhưng git có thể chuyển CRLF khi checkout trên Windows, nên `prompt_hash` có thể đổi theo máy dù nội dung giống nhau; nên thêm `.gitattributes` (`* text eol=lf`) ở vòng sau.
- Hạn chế đã biết: case R12 mong `clarify(yes_no)` ngay khi user chưa đưa nội dung. Hành vi đúng thực tế có thể là hỏi nội dung trước; ta chấp nhận để khớp bộ base, ghi lại đây như một giới hạn của cách chấm.
- Run Gemini của Nam (`v3_B_base_gemini_20261110T183600784007.json`: base 1.00, metric_before 0.90 của Gemini v2) chỉ để tham khảo, không nằm trong chuỗi so sánh vì khác model.

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

Trạng thái các case FAIL của v0 sau v3 (OpenAI, base `v3_B_base_openai_20261110T184941408701.json`):

| Case ID | v0 | v1 | v2 | v3 | Ghi chú |
|---|---|---|---|---|---|
| R03_web_news_routing | FAIL | PASS | PASS | PASS | `query` giữ từ khóa gốc nhờ rule query |
| R13_parallel_web_and_tweets | FAIL | PASS | PASS | PASS | |
| R08_out_of_scope | FAIL | PASS | PASS | PASS | PASS vì không gọi tool; agent vẫn trả lời thẳng, cần review thủ công |
| R14_out_of_scope_coding | FAIL | PASS | PASS | PASS | như R08 |
| R10_missing_handle | FAIL | FAIL | PASS | **FAIL** | v1: thiếu `response_type`; v3: gọi `social_search(query="tweet")` thay vì `clarify` (hồi quy) |
| R11_missing_url | FAIL | FAIL | PASS | PASS | |
| R12_confirm_before_send | FAIL | FAIL | FAIL | PASS | v2: hỏi `text` thay vì `yes_no` |

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
