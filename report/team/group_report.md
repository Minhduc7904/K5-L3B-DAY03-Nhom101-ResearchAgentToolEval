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

Research agent giúp tìm tin AI trên web và Twitter/X, đọc bài viết và bài báo khoa học, rồi tóm tắt lại. Agent hỏi lại khi thiếu thông tin, chỉ đăng lên Telegram khi người dùng đã đồng ý, và có thể biến câu trả lời thành một trang web nhỏ bấm được ngay trong khung chat.

**Cách chạy UI:**

Giao diện web gồm một máy chủ Python (`starter_v0/server.py`) và trang chat (`starter_v0/web/`). Thư viện cần thêm (`fastapi`, `uvicorn`) đã có trong `starter_v0/requirements.txt`.

```bash
cd starter_v0
pip install -r requirements.txt
(cd web && npm install && npm run build)   # chỉ cần chạy một lần, hoặc sau khi sửa giao diện
python server.py --provider openai --version v3   # chuỗi v0–v3 của nhóm chạy trên OpenAI gpt-4o-mini; có thể đổi sang --provider gemini
```

Mở http://localhost:8000. Mỗi phiên chat được tự lưu thành file trong `starter_v0/transcripts/`.

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL: https://unless-votes-pairs-bidding.trycloudflare.com  *(link tạm thời của Cloudflare Tunnel, chỉ hoạt động khi máy chạy `server.py` và `cloudflared` còn bật; mỗi lần chạy lại sẽ ra link mới)*

Cách mở link cho team khác: khi máy chủ đang chạy, mở terminal khác và chạy `cloudflared tunnel --url http://localhost:8000`, rồi gửi link `trycloudflare.com` được in ra.

### A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Hỏi lại người dùng khi thiếu thông tin, hoặc xin xác nhận trước khi gửi | không |
| timeline | Lấy các tweet mới nhất của một tài khoản Twitter/X | không |
| social_search | Tìm tweet theo từ khóa hoặc chủ đề | không |
| lookup | Tìm tin tức và bài viết trên web | không |
| fetch | Đọc nội dung của một đường link cụ thể | không |
| format | Trình bày các tin đã tìm được thành một bản tin gọn gàng | không |
| send | Đăng nội dung lên kênh Telegram của nhóm, chỉ khi người dùng đã đồng ý | không |
| policy | Tra cứu quy định nội bộ của công ty | không |
| papers | Tìm bài báo khoa học trên arXiv | không |
| paper_text | Đọc nội dung của một bài báo arXiv | không |
| artifact | Biến câu trả lời thành một trang web nhỏ bấm được (bảng, biểu đồ, máy tính) hiện ngay trong khung chat | **có** |

### A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1. Tin tức AI nổi bật hôm nay có gì?
2. Tóm tắt 5 tweet mới nhất giúp mình (agent sẽ hỏi lại: của tài khoản nào?)
3. Tìm bài báo mới về retrieval-augmented generation trên arXiv
4. Làm cho mình một trang tính chi phí API LLM: nhập số token và giá, hiện tổng tiền
5. Tìm 3 tin AI nổi bật hôm nay rồi đăng lên Telegram giúp mình (agent sẽ hỏi xác nhận trước khi đăng)

## 3. Giải pháp

Chuỗi v0–v3 chạy trên **OpenAI gpt-4o-mini**, bộ base 20 case (`data/eval_base.json`); bộ group 10 case (`data/eval_group.json`) dùng để kiểm tra chéo.

**`system_prompt.md`**
- v0 (starter) cố ý có ba chỉ dẫn xấu: đoán khi thiếu thông tin, gửi ngay khi được nhờ, ép làm trong một bước. Kết quả 13/20 (0.65), 7 case FAIL (xem B2).
- v1: bỏ ba chỉ dẫn xấu, thêm rule gọi `clarify` khi thiếu thông tin và xin xác nhận trước `send`. Kết quả 15/20 (0.75).
- v3: thêm rule điền `query` (giữ từ khóa gốc, không đưa "news"/thời gian vào `query`), luồng xác nhận `send` (hỏi `yes_no`, gửi `confirmed=true` sau khi user xác nhận rõ, hủy thì không gửi), và trả lời thẳng khi ngoài phạm vi. Kết quả base 19/20 (0.95), group 9/10 (0.90). Thay đổi gộp nhiều phần nên không quy được điểm cho từng rule riêng (xem B1).

**`tools.yaml`**
- v2 (Nam viết): viết lại mô tả các tool kèm "dùng khi / không dùng khi", quy ước tham số (`response_type`, handle không có `@`, `topic=news`, `timeframe`, `search_type`) và ranh giới xác nhận của `send` (`confirmed=true` chỉ khi user đã đồng ý). Kết quả base 19/20 (0.95).

**Tool mới: `artifact`** (Quang viết, `tools/artifact/`): biến câu trả lời thành một trang HTML tương tác (bảng lọc được, biểu đồ, máy tính nhỏ) hiện ngay trong khung chat. Agent nên gọi khi user đòi trang/biểu đồ/bảng tương tác hoặc khi dữ liệu có nhiều cột cần so sánh trực quan; không gọi cho câu trả lời ngắn bằng chữ. Có 7 unit test, 4 case eval nhóm (G04, G08, G05, G10) và hiển thị trong UI web.

**Eval nhóm:** 10 case (5 single + 5 multi turn) trong `data/eval_group.json` đo thêm các điểm bộ base chưa phủ: luồng hỏi → xác nhận → gửi, hủy gửi, bỏ `@` ở handle, `timeframe=month`, chuyển tool giữa chừng và tool `artifact`.

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

Bộ 10 case trong `starter_v0/data/eval_group.json` (5 single turn: G01–G05; 5 multi turn: G06–G10), chạy bằng `--suite group` trên OpenAI gpt-4o-mini. Cột Result lấy từ:
- **v3** (bản chính thức): `starter_v0/runs/v3_B_group_openai_20261110T185010179172.json` — 9/10 (0.90).
- **v3 gốc của Nam** (đối chiếu): `starter_v0/runs/v3-nam_B_group_openai_20261110T184801942989.json` — 8/10 (0.80).
- **v2-artifact** (đối chứng: prompt v2 + tools có `artifact`): `starter_v0/runs/v2-artifact_B_group_openai_20261110T184249362732.json` — 10/10 (1.00).

| Case ID | What It Tests | Expected Tool/Behavior | Result v3 | Result v3 gốc (Nam) | Result v2-artifact |
|---|---|---|---|---|---|
| G01_send_needs_confirmation (single) | Nội dung gửi đã rõ nhưng user chưa xác nhận → phải hỏi yes_no, KHÔNG gọi send ngay. | `clarify(response_type=yes_no)`, không gọi `send` | **PASS** | PASS | PASS |
| G02_handle_without_at (single) | Handle người dùng viết có '@' → screenname phải bỏ '@' (karpathy), limit lấy đúng 3. | `timeline(screenname="karpathy", limit=3)` | **PASS** | PASS | PASS |
| G03_timeframe_month (single) | Cụm 'trong tháng này' → lookup với timeframe=month (không dùng mặc định week). | `lookup(timeframe="month")` | **PASS** | PASS | PASS |
| G04_artifact_chart_from_given_data (single) | Dữ liệu đã có sẵn trong câu hỏi và user đòi biểu đồ → phải gọi artifact (tool mới), không chỉ trả lời bằng chữ. | `artifact` (tool mới) | **PASS** | PASS | PASS |
| G05_artifact_not_needed_short_text (single) | Chỉ cần tóm tắt 1 câu bằng văn bản từ đoạn đã cho → KHÔNG được gọi artifact (hay tool nào) thừa. | Không gọi tool | **PASS** | PASS | PASS |
| G06_confirm_then_send (multi) | Sau khi user xác nhận rõ → gọi send với confirmed=true (luồng hỏi → xác nhận → gửi). | `send(confirmed=true)` | **PASS** | FAIL | PASS |
| G07_cancel_send (multi) | User rút lại yêu cầu ở lượt cuối → tuyệt đối không gọi send (cũng không cần tool nào). | Không gọi tool | **PASS** | PASS | PASS |
| G08_artifact_carry_data_from_earlier_turn (multi) | Số liệu được cho ở lượt trước, lượt cuối yêu cầu biểu đồ → gọi artifact dựa trên số liệu đã có (nhớ ngữ cảnh). | `artifact` (tool mới) | **PASS** | PASS | PASS |
| G09_switch_timeline_to_web (multi) | Đổi giữa chừng từ timeline sang lookup (topic=news, timeframe=day); không dính lại tool ở lượt trước. | `lookup(topic="news", timeframe="day")`, không gọi thêm tool khác | **FAIL** | FAIL | PASS |
| G10_artifact_then_cancel (multi) | User bỏ yêu cầu biểu đồ ở lượt cuối, chỉ cần đáp bằng chữ → không được gọi artifact. | Không gọi tool | **PASS** | PASS | PASS |

Ghi chú:
- Tool mới `artifact` (do Quang viết) được kiểm tra bởi 4 case: G04 và G08 (nên gọi), G05 và G10 (không nên gọi).
- Case FAIL của v3: **G09** — lượt cuối gọi đúng `lookup(topic=news, timeframe=day)` nhưng gọi thêm `social_search`. Prompt v2 cùng tools qua được G09 nên đây là hồi quy do prompt v3. Hướng xử lý: giả thuyết riêng cho một version sau (chỉ xử lý yêu cầu ở lượt cuối), cùng với R10.
- Bản v3 gốc của Nam còn FAIL **G06**: user đã xác nhận rõ nhưng agent hỏi `clarify` lại thay vì `send(confirmed=true)`; bộ group bắt được lỗi mà bộ base (20/20) không bắt được.
- Hạn chế: lượt đầu của G06, G07 trùng câu của case R12 và lượt đầu của G09 trùng câu của R01 trong `eval_base.json` (chỉ một lượt, không phải cả case); harness gộp các lượt thành một tin nhắn và chỉ chấm lượt cuối; một run mỗi cấu hình nên chưa loại trừ nhiễu mẫu. Run `v1_B_group_openai_...` dùng phiên bản cũ của bộ case nên không dùng để so sánh.

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

Hai phiên chat thật qua giao diện web (Gemini `gemini-3.8-flash`, prompt v3-gemini `b3626215b74b`). Tên file ghi `v1` chỉ vì nhãn `--version` lúc bật máy chủ, không phải prompt v1.

- Phiên 1: `starter_v0/transcripts/v1_gemini_web_20261110T190630989602.transcript.json`
- Phiên 2: `starter_v0/transcripts/v1_gemini_web_20261110T185836854159.transcript.json`

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| Phiên 1, lượt 1 (yêu cầu thường) | Tin tức AI nổi bật hôm nay có gì? | `lookup(query="AI", topic="news", timeframe="day")` | `v1+pb3626215b74b+t6ef9ae1cf8c8` | Đúng tool, đúng tham số. Agent tóm tắt các tin tìm được |
| Phiên 1, lượt 2 (thiếu thông tin) | Tóm tắt 5 tweet mới nhất giúp mình | `clarify(response_type="text")`: "Bạn muốn xem … từ tài khoản nào?" | như trên | Agent không đoán tài khoản mà hỏi lại |
| Phiên 1, lượt 3 (bổ sung) | Của Andrej Karpathy nhé | `timeline(screenname="karpathy", limit=5)` | như trên | Agent nhớ "5 tweet" từ lượt trước, đổi tên thành handle `karpathy` (không có `@`) và tóm tắt đúng 5 tweet |
| Phiên 2, lượt 1 (yêu cầu gửi) | Tìm 3 tin AI nổi bật hôm nay rồi đăng lên Telegram giúp mình | `clarify(response_type="yes_no")` | như trên | Agent hỏi xác nhận, chưa gửi |
| Phiên 2, lượt 2 (xác nhận) | có | `lookup` → `send(confirmed=true)` | như trên | `status: sent`, tin hiện trên kênh Telegram private của nhóm |

**Ba phiên chat thật trên chuỗi chính thức (OpenAI gpt-4o-mini, prompt v3 `718f89bc937b`, tools `198864b46581`, `v3+p718f89bc937b+t198864b46581`)**, chạy qua link Cloudflare Tunnel:

- Phiên A: `starter_v0/transcripts/v3_openai_web_20261110T191013015667.transcript.json`
- Phiên B: `starter_v0/transcripts/v3_openai_web_20261110T191400882629.transcript.json`
- Phiên C: `starter_v0/transcripts/v3_openai_web_20261110T191448500175.transcript.json`

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| A, lượt 1 (yêu cầu thường) | Tin tức AI hôm nay có gì nổi bật? | `lookup(query="AI", topic="news", timeframe="day")` | v3 / OpenAI | Đúng tool, đúng tham số. Câu trả lời bằng tiếng Anh dù user hỏi tiếng Việt |
| A, lượt 2 (yêu cầu gửi) | Gửi dòng này lên Telegram: "Họp 9h sáng mai" | `clarify` hỏi xác nhận | như trên | Agent không gửi ngay mà xin xác nhận (`waiting_for_user`) |
| A, lượt 3 | không | không gọi tool | như trên | Agent dừng, không gửi |
| A, lượt 4 | gửi các tin tức AI trên qua telegram | không gọi tool (hỏi xác nhận bằng văn bản thường) | như trên | Hỏi xác nhận đúng ý nhưng không dùng tool `clarify` nên giao diện không đánh dấu "đang chờ" |
| A, lượt 5 (xác nhận) | ok | `send(confirmed=true)` | như trên | Đúng luồng, nhưng `send` trả lỗi `RuntimeError: Missing TELEGRAM_BOT_TOKEN…` vì máy chạy phiên này chưa cấu hình Telegram. Agent báo lỗi cho người dùng, không bịa là đã gửi. Bằng chứng `status: sent` nằm ở phiên Gemini phía trên |
| A, lượt 6 | chuyển sang html | `artifact(title="Tin tức AI hôm nay", html=…)` | như trên | `status: rendered`, trang hiện trong khung chat |
| B, lượt 1 | Tweet mới nhất của Sam Altman là gì? | `timeline(screenname="sama", limit=1)` | như trên | Đúng tool, đúng handle |
| B, lượt 2 | oke thế tweet cũ hơn thì sao | `timeline(screenname="sama", limit=5)` | như trên | Gọi lại cùng tool với `limit=5`; tool không hỗ trợ phân trang nên không thật sự lấy được "cũ hơn" (giới hạn của tool) |
| C, lượt 1 (thiếu thông tin) | Tóm tắt bài viết này hộ mình | không gọi tool (hỏi URL bằng văn bản thường) | như trên | Không đoán URL, hỏi lại; nhưng không dùng tool `clarify` |
| C, lượt 2 (bổ sung) | https://aipure.ai/vn/articles/how-to-create-viral-talking-baby-podcast… | `fetch(url=…)` → `format(template="sections")` | như trên | Đọc bài và tóm tắt đúng |

Nhận xét: ở phiên 2 (Gemini), agent hỏi xác nhận trước khi tìm tin, nên người dùng đồng ý khi chưa thấy nội dung. Luồng vẫn đúng yêu cầu (hỏi → đồng ý → gửi), nhưng tốt hơn là cho người dùng xem nội dung trước rồi mới hỏi.

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/<tên>/`) | `starter_v0/tools/artifact/` (`tool.py`, `TOOL.md`), khai báo trong `tools/__init__.py` và `artifacts/tools.yaml`, commit `06dfa1d` | Model viết nội dung trang, tool bọc thành trang hoàn chỉnh và giao diện hiện nó ngay dưới câu trả lời (có nút Xem trước / Code / Tải về). Chạy thật: Gemini tạo trang tính chi phí API, tính đúng 0,45 USD. Eval nhóm có 4 case cho tool này (G04, G08 nên gọi; G05, G10 không nên gọi), cả 4 đều PASS ở v3 | Trang không được gửi dữ liệu ra ngoài (quy tắc chặn trong trang) và chạy trong khung riêng, không đọc được dữ liệu của trang chat. Đã thử cố đọc trang chat, đọc cookie và gửi dữ liệu ra ngoài: cả ba đều bị chặn |
| Unit test tool mới (≥ 3 test/tool) | `starter_v0/tests/test_tools_todo.py` (7 test cho `artifact`, chạy 11 trường hợp); `pytest`: 78 passed, 0 failed | Kiểm tra: trường hợp bình thường, model gửi cả trang hoàn chỉnh, thẻ `<header>`, tiêu đề có ký tự lạ, nội dung rỗng hoặc sai kiểu, nội dung quá dài | Mọi lỗi trả về thông báo lỗi, không làm sập chương trình. Test chạy offline, không gọi mạng |
| UI (lệnh chạy + link dùng thử) | `starter_v0/server.py`, `starter_v0/web/` (commit `a2d2ae3`); lệnh chạy ở mục A1 | Trang chat có câu hỏi mẫu, hiện tool đã gọi và tham số, đánh dấu khi agent chờ người dùng trả lời. Mỗi phiên tự lưu transcript (xem B4) | Lỗi khi gọi model được hiện rõ trên giao diện, không bị che đi. Phần gọi Gemini chưa có giới hạn thời gian chờ, nên khi model chậm thì giao diện có thể đứng ở "Thinking…" khá lâu |

Tool unit tests: 7 test cho tool `artifact` (11 trường hợp). Ví dụ lỗi mà unit test bắt được nhưng eval không bắt được: lúc đầu tool nhầm thẻ `<header>` với phần đầu trang `<head>`, nên đặt quy tắc chặn sai chỗ và quy tắc mất tác dụng. Eval chỉ kiểm tra model có gọi `artifact` hay không, nên vẫn PASS. Chỉ unit test `test_artifact_header_tag_is_not_mistaken_for_head` mới phát hiện ra lỗi này.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 | Không thực hiện | Chưa chạy model Ollama nào |
| Hơn 3 tool mới (≥ 4) | — | Không đạt: nhóm chỉ viết 1 tool mới (`artifact`) | — |
| `send` gửi thật lên Telegram sau xác nhận | `starter_v0/transcripts/v1_gemini_web_20261110T185836854159.transcript.json` (chạy qua web UI, Gemini, prompt v3-gemini `b3626215b74b`; tên file ghi `v1` do nhãn `--version` khi bật server) | Lượt 1: user yêu cầu tìm 3 tin AI rồi đăng → agent gọi `clarify` (`yes_no`) hỏi xác nhận, chưa gửi. Lượt 2: user trả lời "có" → agent gọi `send(confirmed=true)` → `status: sent`, tin hiện trên kênh private của nhóm | Chỉ gửi sau khi user xác nhận ở lượt sau (rule trong `system_prompt.md` + mô tả `send` trong `tools.yaml`); token và chat ID chỉ nằm trong `.env`, đã kiểm tra transcript không chứa token |
| Test challenge (0 skipped / regression test) | `pytest` output | Không đạt: `pytest` báo 78 passed, **14 skipped** (stub TODO của tool có sẵn), chưa có regression test cho bug của tool có sẵn | — |

Test challenge: số bug tìm được trong tool có sẵn (nếu có), cách sửa, và test regression tương ứng.

### B7. Small Local Model Challenge (bonus)

**Nhóm không thực hiện bonus này** (chưa chạy model Ollama nào), nên các bảng dưới để trống.

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

1. **Chuỗi version chạy trên hai model khác nhau.** v0 và v1 chạy OpenAI, còn v0/v2/v3 của một thành viên chạy Gemini, nên mức tăng "0.75 → 0.90" không so sánh được. Cách xử lý: chốt OpenAI gpt-4o-mini cho cả chuỗi, chạy lại v2 và v3 trên OpenAI (`runs/v2_B_base_openai_20261110T183148819703.json`, `runs/v3_B_base_openai_20261110T184941408701.json`), giữ các run Gemini làm tham khảo (`v0-gemini`, `v2-gemini`, `v3-gemini` trong `version_log.csv`).
2. **Bản v3 gốc có dấu hiệu tune theo bộ base.** Prompt chép nguyên văn câu của case R12 và ví dụ "AI", "tuần này"; trên OpenAI đạt 20/20 ở base nhưng chỉ 8/10 ở bộ group (`runs/v3-nam_B_group_openai_20261110T184801942989.json`). Cách xử lý: viết lại prompt không chép từ eval (v3 chính thức), dùng bộ group để kiểm tra chéo.
3. **Hash tools/prompt khác nhau giữa các máy** do khác kết thúc dòng CRLF/LF (cùng nội dung nhưng `tools_hash` `474f8a0277b2` so với `eb21b1702350`). Cách xử lý: ghi chú trong `version_log.csv`; vòng sau nên thêm `.gitattributes`.
4. **`send` lỗi trên máy chưa cấu hình Telegram.** Trong phiên A (`v3_openai_web_20261110T191013015667`) `send(confirmed=true)` trả `RuntimeError: Missing TELEGRAM_BOT_TOKEN…`. Agent báo lỗi trung thực. Bằng chứng gửi thành công nằm ở transcript Gemini của nhóm (B5).
5. **Push bị từ chối do thành viên khác vừa đẩy commit.** Cách xử lý: `git pull --rebase` rồi push lại, không dùng force.
6. **Bộ eval chấm khá chặt.** Harness gộp các lượt multi-turn thành một tin nhắn và chỉ chấm lượt cuối, nên chỉ kiểm tra được hành vi ở lượt cuối.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- **Fix nào thuộc `system_prompt.md`?** Bỏ chỉ dẫn "đoán / gửi ngay / một bước" (v1, 0.65 → 0.75); rule điền `query`; luồng xác nhận `send` và không hỏi lại sau khi user đã xác nhận (v3).
- **Fix nào thuộc `tools.yaml`?** Quy ước `response_type` của `clarify` (v1 gọi đúng `clarify` nhưng bỏ trống `response_type`); mô tả "dùng khi / không dùng khi" và ranh giới xác nhận của `send` (v2). Nhóm không tách được đóng góp riêng của từng phần vì v2 sửa nhiều tool cùng lúc.
- **Failure nào cần review thủ công?** R08 và R14 "PASS" chỉ vì agent không gọi tool, nhưng vẫn trả lời thẳng bài toán/code thay vì từ chối; harness không phân biệt được. Hai lượt agent hỏi xác nhận/hỏi URL bằng văn bản thường thay vì tool `clarify` (phiên A lượt 4, phiên C lượt 1) vẫn đúng ý nhưng giao diện không đánh dấu "đang chờ". Một lần câu trả lời bằng tiếng Anh dù user hỏi tiếng Việt (phiên A lượt 1). Trong R12, agent xin xác nhận gửi khi chưa có nội dung cụ thể; chấm tự động coi là đúng.
- **Nếu có thêm một vòng, nhóm sẽ thử:** (1) v4: chỉ xử lý yêu cầu ở lượt cuối của hội thoại để sửa G09 (gọi thêm `social_search`) và R10 (hồi quy: gọi `social_search` thay vì `clarify`); (2) chạy mỗi cấu hình nhiều lần để ước lượng nhiễu, vì mới có một run mỗi cấu hình; (3) thêm `.gitattributes` để hash tái lập giữa các máy; (4) thêm tool tra cứu tài khoản để xử lý tên người mơ hồ.

## 8. Tài liệu tham khảo

- Đề bài và rubric: `README.md`, `CHECKPOINTS.md`, `RUBRIC.md`, `RULES.md`, `docs/TOOL-SETUP.md` trong repo.
- Dịch vụ dùng cho tool: OpenAI API (model gpt-4o-mini), Tavily (`lookup`), Firecrawl (`fetch`), RapidAPI Twitter API45 (`timeline`, `social_search`), Telegram Bot API (`send`).
- Triển khai link dùng thử: Cloudflare Tunnel (`cloudflared`).
- Tool `artifact` mô phỏng đơn giản hoá cách Claude Artifacts và ChatGPT Canvas hoạt động (xem `starter_v0/tools/artifact/TOOL.md`).
