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
- (#57) Thành ngữ "count one's chickens before they hatch": dịch là "tính chuyện chưa đâu vào đâu", "tính cua trong lỗ" (tránh dịch sai thành "chưa đỗ ông nghè đã đe hàng tổng").
- (#34) Đơn vị tiền đồng ("bronze coin" / "bronze piece"): dịch là "đồng xu đồng" (tránh dịch lặp âm thành "đồng đồng").
- (#64) Cụm từ "my past life" của Rentt: dịch là "thời còn sống" hoặc "quãng đời trước đây" (tránh dịch là "kiếp trước" gây nhầm sang chuyển sinh).
- (#76) Thành ngữ "a means to an end": dịch là "cách thức/phương tiện để đạt mục đích" hoặc "cái cớ" theo ngữ cảnh (tránh dịch sai thành "biện pháp tạm thời").
- (#77) Ngôi thứ ba khi Lorraine nói với Alize về Rentt: dùng "anh ấy" (thay vì "anh ta") để giữ sắc thái hòa nhã, đúng mối quan hệ thầy trò và đồng đội bảo hộ.
- (#77) Độc thoại nội tâm tự trách mình của Rentt (dạng "what were you even doing?"): dùng "mày" hoặc "mình" (ví dụ "Rentt Faina ơi, rốt cuộc hồi đó mày đang làm cái trò gì vậy hả?"), không dùng "anh".
- (#78) Thành ngữ "a walk in the park": dịch là "chuyện dạo chơi nhẹ nhàng", "chuyện dễ dàng" (tránh dịch thô từng chữ thành "đi dạo chơi ngoài công viên").
- (#89) Cụm từ đệm "you see" trong độc thoại tự sự ngôi thứ nhất: dịch là "thực ra thì", "vốn dĩ" hoặc "nói cho cùng" (tránh dịch máy thành "anh thấy đấy").
- (#102) Thành ngữ "stand out like a sore thumb": dịch là "đập ngay vào mắt", "lạc lõng/chướng mắt thấy rõ" (tránh dịch thô từng chữ thành "như một ngón tay cái sưng vù").
- (#108) Thành ngữ "to say the least": dịch là "nói một cách nhẹ nhàng nhất thì" hoặc "ít nhất cũng phải nói là" (tránh dịch sai thành "nói giảm nói tránh").
