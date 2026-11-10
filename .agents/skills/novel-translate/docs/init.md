# Khởi tạo truyện mới (một lần)

Phần của skill `novel-translate` (đọc `SKILL.md` trước). Dùng khi được giao khởi tạo một truyện.

1. Chạy:
   ```
   python .agents/skills/novel-translate/scripts/init_novel.py --raw "<thư mục raw>" --slug <slug> --title "<tên truyện>"
   ```
   Raw phải có dạng `Chapter_XXX - <tiêu đề>.txt`. Script đánh dấu `skip` các chương nghi trùng (cùng tiêu đề). Mở raw các cặp đó, đối chiếu vài đoạn để xác nhận trùng thật; không trùng thì sửa lại `todo`.

   Truyện mới luôn là layout 2. Script ghi vào `novel.json` các khoá `raw_lang` (`en`/`ja`, đoán từ raw) và `arc_rule`, rồi in ra. Kiểm tra `arc_rule`: `pattern` là regex lấy tên arc (group 1) từ cột `Tiêu đề` của `progress.md`, `max` là số chương tối đa một arc (arc dài hơn bị chia thành nhiều phần). Tiêu đề raw không có tên arc thì để không có `pattern`: cứ `max` chương là một arc.
2. Dựng context ban đầu:
   ```
   python .agents/skills/novel-translate/scripts/extract_terms.py <slug> 1-15 --min 2
   ```
   Đọc lướt 3–5 chương đầu, rồi điền: `style.md` (thể loại, góc nhìn, giọng kể), `characters.md` (nhân vật chính và tính cách), `pronouns.md` (người kể gọi nhân vật chính là gì, xưng hô các cặp chính), `glossary.md` (thuật ngữ xuất hiện nhiều). Lúc này các file còn nhỏ nên điền thẳng được, hoặc dùng các lệnh `ctx.py add-*`.

   Tên riêng không có trong raw thì **không tự đặt**: phiên âm theo đúng quy tắc trong `rules.md` (raw tiếng Nhật: romaji hoặc tên chính thức của bản LN tiếng Anh). Không chắc thì ghi câu hỏi.
3. Báo user các quyết định quan trọng (đại từ người kể dùng cho nhân vật chính, xưng hô các cặp chính, 10–20 thuật ngữ chính) và chờ duyệt trước khi dịch chương đầu tiên. Chạy dưới orchestrator thì ghi vào báo cáo thay vì chờ.
