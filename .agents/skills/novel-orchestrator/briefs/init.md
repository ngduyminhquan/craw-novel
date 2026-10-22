Chế độ orchestrator. Dùng skill `novel-translate`: đọc `.agents/skills/novel-translate/SKILL.md` trước, gồm cả mục "Chạy dưới orchestrator".

Repo: $root

Việc: khởi tạo truyện `$slug` theo mục A của skill.
- Raw: `$raw`
- Tên truyện: `$title`
- Lệnh bước 1: `python .agents/skills/novel-translate/scripts/init_novel.py --raw "$raw" --slug $slug --title "$title"`

Bước A3 không chờ user: ghi các quyết định vào file context, rồi liệt kê lại trong báo cáo để orchestrator duyệt.

Tiêu chí xong:
- `translations/$slug/` đã có `progress.md` và đủ các file context.
- Đã kiểm tra các chương bị đánh dấu `skip` vì nghi trùng.
- `style.md`, `characters.md`, `pronouns.md`, `glossary.md` đã điền từ 3–5 chương đầu.

Không dịch chương nào. Không chạy git.

Báo cáo gồm:
- danh sách chương `skip`, xác nhận trùng thật hay không;
- góc nhìn và giọng kể đã ghi trong `style.md`;
- đại từ người kể dùng cho từng nhân vật chính;
- xưng hô các cặp chính;
- 10–20 thuật ngữ quan trọng nhất (EN → VI);
- câu hỏi cần quyết, mỗi câu kèm phương án đã tạm chọn.
