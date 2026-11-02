# Quy tắc dịch — The Unwanted Undead Adventurer

Quy tắc cứng, áp dụng cho mọi chương. Mâu thuẫn giữa file này và các file context khác thì file này thắng.
Thêm quy tắc mới khi gặp một trường hợp cần xử lý thống nhất về sau (ghi kèm chương phát hiện).

## Tên riêng

- Tên phương Tây: giữ nguyên như raw (Rentt Faina, Lorraine Vivie, Rina Rupaage, Sheila Ibarss, Clope, Luka...).
- Raw đổi translator nên một tên có thể có nhiều cách viết EN. Bản dịch luôn dùng MỘT cách viết đã chốt trong characters.md; các cách viết khác ghi vào cột Alias.

## Thuật ngữ, kỹ năng, danh hiệu, vật phẩm

- Tên kỹ năng, danh hiệu, chức nghiệp, cấp bậc: dịch sang Hán Việt, ngắn gọn, viết hoa chữ cái đầu mỗi chữ (vd `Thiết Cấp`, `Đồng Cấp`, `Ngân Cấp`, `Kim Cấp`, `Bạch Kim Cấp`, `Mithril Cấp`). Không giữ tiếng Anh trong ngoặc.
- Riêng tên câu thần chú hoặc tên cổ ngữ ma pháp đặc thù (Foteia Borivaas, Gie Vieros) giữ nguyên phiên âm như raw.
- Mọi thuật ngữ phải có trong glossary.md TRƯỚC khi dùng trong bản dịch. Đã chốt thì dùng đúng chữ đó ở mọi chương.
- Đơn vị, chỉ số trò chơi (Lv, HP, MP, EXP, stat...): giữ dạng viết tắt quen thuộc với độc giả game (Lv, HP, MP, EXP).

## Định dạng

- Dòng đầu file: `# Chương N: <tiêu đề dịch>` với N là cột `#` trong progress.md.
- Mỗi đoạn raw là một đoạn dịch trên một dòng, cách nhau một dòng trống. Không gộp, không tách, không bỏ đoạn, không ngắt một đoạn ra nhiều dòng.
- App đọc file theo dòng, không render Markdown: `*`, `_` hiện nguyên ký tự. Ảnh và dòng điều hướng theo `chapter-image-guide.md` ở repo root.
- Lời thoại: ngoặc kép thẳng `"..."`.
- Thông báo hệ thống, lời nói qua thần giao cách cảm, thông tin kỹ năng: giữ trong `[...]` như raw.
- Không dùng in nghiêng/in đậm Markdown (`*...*`, `_..._`): app hiện nguyên dấu `*`. Chữ in nghiêng trong raw (tiếng động, tiếng kêu, nhấn mạnh) viết thường, không có dấu `*`. Suy nghĩ nội tâm raw dùng ngoặc đơn thì giữ ngoặc đơn. Riêng chữ bị che một phần bằng `*` (vd `M** ***t`) thì giữ dấu `*`.

## Ghi chú translator

- Bỏ hẳn mọi ghi chú translator (T/N, TL note...) của raw, không dịch, không chuyển thành chú thích.
- Nếu T/N giải thích một cách chơi chữ cần thiết để hiểu câu, xử lý ngay trong câu dịch (diễn đạt lại) thay vì thêm chú thích.

## Riêng truyện này

- (#1) Các cấp bậc mạo hiểm giả: Iron-class → Thiết Cấp, Bronze-class → Đồng Cấp, Silver-class → Ngân Cấp, Gold-class → Kim Cấp, Platinum-class → Bạch Kim Cấp, Mithril-class → Mithril Cấp.
- (#2) Ba nguồn năng lượng của cơ thể: Mana → Ma Lực, Spirit → Khí Lực (sinh mệnh lực), Divinity → Thần Lực (thần thánh lực).
- (#2) Hiện tượng tiến hóa của quái vật: Existential Evolution → Tiến Hóa Bản Thể.
- (#1) Mê cung chính: Labyrinth of the Moon’s Reflection → Mê Cung Nguyệt Ảnh (gốc Nhật là Thủy Nguyệt chi Mê Cung).
- (#4) Danh từ chung "potion" / "healing potion": dịch là "thuốc" / "thuốc hồi phục" (không dịch nhầm thành "độc dược").
- (#12) Thành ngữ "for (the) lack of a better word": dịch là "nói một cách trần trụi thì" hoặc "nói thẳng thừng ra là" (tránh dịch ngược nghĩa thành "nói theo cách dễ nghe nhất").
- (#13) Thành ngữ "if anything": dịch là "nói đúng hơn thì", "trái lại" (tránh dịch nhầm thành "nếu có điều gì xảy ra").
- (#14) Cấu trúc phủ định kép: cẩn thận khi chuyển ngữ sang tiếng Việt tránh đảo ngược nghĩa câu văn (ví dụ "did not have the slightest suspicion that these days would not continue indefinitely" dịch thành "chưa từng mảy may thoáng nghĩ rằng những chuỗi ngày ấy rồi sẽ có lúc không thể tiếp diễn mãi mãi").
- (#49) Thành ngữ "at best": dịch là "xét một cách nhẹ nhàng nhất thì", "có nhìn nhận tích cực nhất thì" hoặc "khá lắm thì cũng" (tránh dịch sai thành "nói giảm nói tránh" như ở chương 48 và 49).
