# Team

## Thông tin nhóm

- Tên nhóm:nhóm 101
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY03-Nhom101-ResearchAgentToolEval` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/Minhduc7904/K5-L3B-DAY03-Nhom101-ResearchAgentToolEval

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Nguyễn Minh Đức | 2A202603751 |  | [Minhduc7904](https://github.com/Minhduc7904) |         |
|   2 | Đỗ Lý Hoàng Nam | 2A202603777 |  | [DoLyHoangNam](https://github.com/DoLyHoangNam) | Tối ưu Prompt & Tools (CP1, CP2) |
|   3 | Nguyễn Ngọc Quang | 2A202603773 |  | [shoxieje](https://github.com/shoxieje) | Giao diện web (CP5), tool mới `artifact` (CP3) |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## NguyenMinhDuc-2A202603751

### Phần việc phụ trách

-

### Đóng góp cụ thể

-

### Bằng chứng

-

## DoLyHoangNam-2A202603777

### Phần việc phụ trách

- Cấu hình môi trường, thiết lập API keys và chạy đánh giá Baseline `v0` hợp lệ (Checkpoint 1).
- Tối ưu hóa file khai báo công cụ `tools.yaml` ở Version 2 (Checkpoint 2 - v2).
- Tinh chỉnh `system_prompt.md` ở Version 3 đưa agent đạt điểm tuyệt đối 100% (Checkpoint 2 - v3).

### Đóng góp cụ thể

- Thiết lập môi trường ảo `.venv`, cấu hình `.env`, kiểm thử pass 100% bộ contract test (`pytest`).
- Thực hiện chạy eval Baseline `v0` chuẩn hợp lệ (20/20 cases, 0 provider error, 65% accuracy), phân tích 7 failure cases ban đầu và cập nhật bảng B1, B2 trong `group_report.md`.
- Tối ưu hóa toàn diện `starter_v0/artifacts/tools.yaml` (v2): định nghĩa rõ ràng ranh giới khi nào dùng / khi nào không dùng, phân biệt `lookup` và `social_search`, chuẩn hóa quy ước tham số (`response_type='text'/'yes_no'`, `screenname`, `topic`, `timeframe`), đưa accuracy từ 75% lên 90% (tool routing và multiturn đạt tuyệt đối 100%).
- Tinh chỉnh `starter_v0/artifacts/system_prompt.md` (v3): bổ sung quy tắc trích xuất giữ nguyên từ khóa query và boundary xác nhận an toàn trước khi `send`, đưa hệ thống đạt điểm tuyệt đối 100% (20/20 cases PASS).
- Ghi nhận đầy đủ các mốc `v0`, `v2`, `v3` vào `starter_v0/artifacts/version_log.csv`.

### Bằng chứng

- Commits trên GitHub: `af28f33` (checkpoint 1), `c558dc3` (CP2: v2 - 90% accuracy), `cb90f10` (CP2: v3 - 100% accuracy (20/20 passed)).
- Run logs minh chứng:
  - `starter_v0/runs/v0_B_base_gemini_20261110T175736805773.json` (Accuracy: 65%)
  - `starter_v0/runs/v2_B_base_gemini_20261110T182232420866.json` (Accuracy: 90%)
  - `starter_v0/runs/v3_B_base_gemini_20261110T183600784007.json` (Accuracy: 100% tuyệt đối)
- Báo cáo cá nhân chi tiết: `report/team/2A202603777_DoLyHoangNam.md`.

## NguyenNgocQuang-2A202603773

### Phần việc phụ trách

- Giao diện web cho agent (CP5)
- Tool mới `artifact`: biến câu trả lời thành trang web tương tác hiển thị ngay trong khung chat (CP3)

### Đóng góp cụ thể

- Viết máy chủ `starter_v0/server.py` và trang chat `starter_v0/web/`; mỗi phiên chat trên web tự lưu transcript vào `starter_v0/transcripts/`
- Viết tool `starter_v0/tools/artifact/`, khai báo trong `tools.yaml`, hiển thị trang trong khung an toàn trên giao diện, kèm 7 unit test

### Bằng chứng

- Commit `a2d2ae3` (giao diện web), `06dfa1d` (tool `artifact`)
- Báo cáo cá nhân: `report/team/2A202603773_NguyenNgocQuang.md`
