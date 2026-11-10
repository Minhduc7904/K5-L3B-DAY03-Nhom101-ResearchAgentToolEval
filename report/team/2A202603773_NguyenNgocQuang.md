# Báo cáo cá nhân — NguyenNgocQuang-2A202603773

## 1. Thông tin thành viên

- Họ tên: Nguyễn Ngọc Quang
- MSSV: 2A202603773
- Email: 26ai.quangnn3@vinuni.edu.vn
- GitHub: [shoxieje](https://github.com/shoxieje)

## 2. Phần việc phụ trách

- **Giao diện web (CP5):** làm trang chat để người ngoài nhóm có thể dùng thử agent qua trình duyệt, thay vì phải chạy lệnh trong terminal.
- **Tool mới `artifact` (CP3):** cho agent biến câu trả lời thành một trang web nhỏ có thể bấm, nhập, xem ngay trong khung chat (ví dụ: bảng so sánh, máy tính chi phí, biểu đồ).

## 3. Đóng góp cụ thể

### Giao diện web

- Viết `starter_v0/server.py`: một máy chủ nhỏ nhận tin nhắn từ trình duyệt, chuyển cho agent xử lý (dùng lại đúng vòng lặp gọi tool của `chat.py`), rồi trả câu trả lời về.
- Mỗi phiên chat trên web được tự động lưu thành một file transcript trong `starter_v0/transcripts/`, nên mọi lượt dùng thử đều có bằng chứng để chấm, giống như khi chạy `chat.py`.
- Làm trang chat trong `starter_v0/web/`:
  - có sẵn vài câu hỏi mẫu để người dùng bấm thử;
  - hiện danh sách tool agent đã gọi và tham số đã truyền, để thấy agent chọn tool đúng hay sai;
  - đánh dấu rõ khi agent đang chờ người dùng bổ sung thông tin, và báo lỗi rõ ràng khi gọi model thất bại, không che lỗi đi.
- Máy chủ phục vụ cả trang web lẫn phần xử lý trên cùng một cổng, nên chỉ cần mở một đường link (qua Cloudflare Tunnel) là nhóm khác dùng thử được.
- Thêm thư viện cần thiết vào `requirements.txt` và ghi cách chạy trong `starter_v0/web/README.md`.

### Tool `artifact`

- Ý tưởng lấy từ cách Claude (Artifacts) và ChatGPT (Canvas) hiển thị trang web do AI tạo ra, nhưng làm gọn lại thành một tool đơn giản:
  1. Model viết nội dung trang (HTML) và đặt tiêu đề.
  2. Tool bọc nội dung thành một trang hoàn chỉnh và thêm quy tắc chặn: trang **không được gửi dữ liệu ra ngoài** (không gọi mạng), chỉ được tải thư viện vẽ biểu đồ từ hai nguồn công khai.
  3. Giao diện web hiển thị trang trong một **khung riêng biệt**: code trong trang vẫn chạy được (nút bấm, ô nhập hoạt động), nhưng không đọc được dữ liệu của trang chat và không gọi được máy chủ của nhóm.
- Trên giao diện, mỗi trang hiện thành một thẻ dưới câu trả lời, có nút chuyển giữa **Xem trước** và **Code**, và nút **Tải về** file HTML.
- Xử lý trường hợp thực tế: dù đã dặn chỉ gửi phần nội dung, model (Gemini) vẫn hay gửi cả trang hoàn chỉnh. Tool nhận ra điều này và chèn quy tắc chặn vào đúng chỗ thay vì bọc thêm một lớp nữa.
- Khai báo tool trong `artifacts/tools.yaml`, nói rõ khi nào nên dùng (user muốn trang/bảng/biểu đồ tương tác) và khi nào không (câu trả lời ngắn, hoặc chưa có dữ liệu thì phải lấy dữ liệu bằng tool khác trước).
- Viết 8 unit test trong `tests/test_tools_todo.py`: trường hợp bình thường, model gửi cả trang hoàn chỉnh, tiêu đề chứa ký tự lạ, model gửi nội dung rỗng hoặc sai kiểu, nội dung quá dài. Mọi lỗi đều trả về thông báo lỗi chứ không làm sập chương trình.

## 4. Bằng chứng

- File/commit/PR:
  - `a2d2ae3` — CP5: giao diện web và máy chủ (`starter_v0/server.py`, `starter_v0/web/`)
  - `06dfa1d` — tool `artifact` (`starter_v0/tools/artifact/`), cập nhật `server.py`, `web/src/App.tsx`, `artifacts/tools.yaml`, `tests/test_tools_todo.py`
  - Kết quả `pytest` sau khi thêm tool: 78 passed, 0 failed.
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:
  - Dùng Claude Code để hỗ trợ viết code và test. Mọi thay đổi đều được tôi đọc lại và kiểm tra bằng các cách sau, không chỉ tin vào AI:
  - **Chạy test:** `pytest` phải báo 0 failed trước khi commit.
  - **Chạy thật với model:** gửi yêu cầu "làm trang tính chi phí API LLM" qua giao diện web. Gemini chọn đúng tool `artifact`, tạo ra trang khoảng 10 KB, trang hiện đúng trong khung chat và tính đúng kết quả (100.000 token input × 2,5 USD + 20.000 token output × 10 USD trên mỗi 1 triệu token = 0,45 USD).
  - **Thử phá khung an toàn:** tạo một trang thử cố đọc dữ liệu của trang chat, đọc cookie và gửi dữ liệu ra ngoài. Cả ba đều bị chặn.
  - **Tìm ra và sửa lỗi của chính code AI viết:** lần đầu, tool nhầm thẻ `<header>` với phần đầu trang `<head>`. Nếu để vậy, quy tắc chặn sẽ bị đặt sai chỗ và mất tác dụng mà không ai biết. Tôi sửa lại và thêm test riêng cho trường hợp này.

## 5. Tự đánh giá

- **Làm tốt:** giao diện chạy được, người ngoài nhóm dùng thử qua một đường link, và mỗi lượt dùng đều tự lưu transcript làm bằng chứng. Tool `artifact` được kiểm tra cả bằng test lẫn chạy thật, kể cả phần an toàn.
- **Chưa tốt / bài học:**
  - Khi model phải viết cả một trang web dài, câu trả lời có thể mất 30 giây đến hơn một phút. Có lần giao diện đứng ở "Thinking…" rất lâu vì phần gọi Gemini không đặt giới hạn thời gian chờ. Bài học: mọi lần gọi ra ngoài (model hay API) đều nên có giới hạn thời gian, để khi chậm thì báo lỗi rõ ràng thay vì treo.
  - Nội dung trang HTML được gửi lại cho model trong kết quả tool, tốn thêm khoảng 10 nghìn token mỗi lần. Chấp nhận được cho demo, nhưng nếu dùng lâu dài nên chỉ gửi lại tiêu đề.
  - Thêm tool mới làm thay đổi `tools.yaml`, nên các version sau đó phải ghi rõ điều này trong `version_log.csv` để không nhầm việc tăng/giảm điểm là do sửa prompt.
- **Nếu làm lại:** thống nhất với nhóm sớm hơn về thời điểm thêm tool mới, để không trùng lúc nhóm đang đo v2/v3.
