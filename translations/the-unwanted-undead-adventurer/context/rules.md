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
- (#114) Cụm từ liên kết "in turn": dịch là "đến lượt mình", "kéo theo đó", "kéo theo hệ quả là" theo ngữ cảnh liên đới hành động (tránh dịch máy thành "đổi lại" gây nhầm lẫn sang sự trao đổi/thỏa hiệp).
- (#115) Tránh dịch máy đại từ phiếm chỉ "you" thành "bạn" trong độc thoại tự sự ngôi thứ nhất (ví dụ: "bạn có thể tìm thấy" → "có thể tìm thấy", "nơi bạn có thể thưởng thức" → "nơi người ta có thể thưởng thức", "bạn có thể hình dung" → "đủ hiểu / có thể hình dung", "hơn bạn tưởng" → "hơn người ta tưởng").
- (#117) Thành ngữ "have one's fill" / "had my fill" trong ngữ cảnh chịu đựng đau đớn/phiền phức: dịch là "chịu đựng quá đủ", "phát ngấy" (tránh dịch sai thành "ngán ngẩm").
- (#120) Không viết hoa tùy tiện danh từ chung (như "quả cầu" / "khối cầu" khi miêu tả cấu trúc ma pháp trận).
- (#124) Cấu trúc diễn đạt ước lượng "anywhere from [X] to [Y]": dịch là "trong khoảng từ X đến Y" hoặc "tầm từ X đến Y" (tránh dịch thô từng chữ "anywhere" thành "ở bất cứ đâu").
- (#125) Thành ngữ "more [X] where that came from": dịch là "còn nhiều [X] tương tự như thế", "đâu chỉ có thế, còn nhiều [X] nữa" (tránh dịch máy thành "từ gốc rễ vấn đề").
- (#129) Tránh dùng cách gọi ước lệ kiểu cổ trang "nàng [Tên]" (như "nàng Rina") cho nhân vật nữ đời thường; tránh dùng từ lễ nghi sai thứ bậc như "diện kiến" khi nói về hậu bối (thay bằng "gặp mặt").
- (#140) Pravda khi nói chuyện với Rentt và Jinlin (kể cả những lúc bực bội, la mắng nghiêm khắc) luôn xưng "bà", gọi "cháu / hai đứa / các cháu" — giữ nhất quán với pronouns.md, tránh chuyển sang xưng hô "ta" kiểu xa cách hoặc kiếm hiệp.
- (#145) Cụm từ "for the most part": dịch là "nhìn chung", "thông thường", "phần lớn trường hợp" (tránh dịch máy thành "phần lớn thời gian").
- (#146) Thành ngữ "at a loss for words": dịch là "lúng túng chẳng biết nói gì", "ngượng ngùng cạn lời" (tránh dịch sai lệch thành "bực dọc đến chẳng thốt nên lời").
- (#146) Cấu trúc đối đáp "mind if I..." / "I'd definitely mind" trong hội thoại đời thường: chuyển ngữ tự nhiên theo ngữ cảnh can ngăn / từ chối khéo thay vì dịch thô chữ "phiền" (ví dụ: "cháu can chú đấy ạ!").
- (#150) Cấu trúc "doubt [something]": dịch là "cho rằng... khó lòng / không nghĩ là..." (tránh dịch ngược nghĩa thành "ngờ rằng...").
- (#150) Từ "cackle / cackling": dịch là "cười the thé / cười man rợ / cười rợn người" (tránh dịch là "cười khúc khích").
- (#152) Thành ngữ "live up to one's reputation": dịch là "quả không hổ danh", "thực sự danh bất hư truyền" (tránh dịch lặp nghĩa thành "không hổ danh với danh tiếng").
- (#152, #153) Tránh dùng tiếng lóng hiện đại/phương ngữ lệch tông fantasy phương Tây (như "ngon tuyệt cú mèo", "xạo ke") và tránh dịch máy "Yeah" thành "Vâng" trong đối thoại ngang hàng (dùng "Phải đấy", "Đúng vậy").
- (#160) Thành ngữ "hit (someone) where it hurts": dịch là "chạm đúng vào chỗ đau / đánh trúng điểm yếu của ai" (tránh dịch sai lệch thành "đánh trúng tim đen" vì mang nghĩa dã tâm, mưu tính xấu xa).
- (#162) Câu dẫn thoại đi liền sau lời thoại kết thúc bằng dấu hỏi "?" hoặc dấu cảm thán "!" (như "..." tôi hỏi, "..." cô nói, "..." người đó gào lên): viết thường chữ cái đầu câu dẫn thoại (tránh dịch máy theo thói quen viết hoa tiếng Anh "..." I asked -> "..." Tôi hỏi).
- (#165) Thuật ngữ vũ khí: Khi miêu tả chiêu thức chặn đòn bằng dao/kiếm, phân biệt "the flat" (bản dao / bản kiếm - mặt dẹt của lưỡi), "the spine" (sống dao / sống kiếm), "the edge" (lưỡi dao / lưỡi kiếm); dịch đúng "the flat" là "bản dao", tránh dịch nhầm thành "sống dao".
- (#166) Cụm từ phủ định ước lượng "not... just anywhere" / "couldn't be found just anywhere": dịch là "không phải ở đâu cũng có thể tìm thấy / không phải cứ tìm bừa ở đâu cũng thấy", tránh dịch máy thành "không thể tìm thấy ở bất cứ nơi đâu" gây mâu thuẫn phủ định tuyệt đối.
- (#168) Tránh dịch thô thành ngữ "deadly serious" thành "nghiêm túc đến chết người" (chuyển ngữ tự nhiên thành "nghiêm túc đến tột độ / vô cùng nghiêm túc"); phân biệt rõ từ "novice" (kẻ mới nhập môn / người mới học) với "vague" (mơ hồ), tránh dịch nhầm "as a novice" thành "kẻ mơ hồ".
- (#179) Từ "brutal" khi miêu tả sự khắt khe / dữ dội / ghê gớm của nghệ thuật biểu diễn hoặc diễn xuất: dịch là "ghê gớm", "khắc nghiệt", tránh dịch là "tàn nhẫn" (mang nghĩa độc ác, vô nhân đạo).
- (#180) Cụm từ "projection magic item": dịch là "ma cụ trình chiếu hình ảnh" hoặc "ma cụ tạo ảnh chiếu", tránh ghép thừa chữ thành "tạo hình ảnh chiếu".
- (#183) Thành ngữ "That was a close one": dịch là "Suýt nữa thì nguy" hoặc "Nguy hiểm trong gang tấc" (tránh dùng "suýt soát" vì "suýt soát" chỉ dùng để chỉ số lượng/mức độ xấp xỉ).
- (#188) Thành ngữ "feel like a sack of bricks": dịch là "nặng trịch như đeo chì / nặng như đeo đá", tránh dịch thô từng chữ thành "nặng như một bao gạch".
- (#189) Từ "convenient" khi nói về người đa năng, giải quyết được nhiều việc: dịch là "có [ai] đúng là tiện thật / hữu dụng / đa năng", tránh dịch máy thành "tiện dụng" (vốn chỉ dùng cho đồ vật).
- (#192) Tên quái vật cơ bản (Goblin, Slime, Khô Lâu): luôn viết hoa theo đúng glossary.md, tránh viết thường "goblin" lẫn lộn.
- (#192) Cụm từ đệm "you know" cuối câu thoại an ủi/giải thích: dịch là "... mà / ... đấy thôi", tránh dịch thô thành "bạn biết đấy / anh biết đấy / ngài biết đấy".
- (#195) Cụm từ "magic trick": dịch là "màn ảo thuật" hoặc "trò ảo thuật" (tránh lặp từ dịch máy thành "ảo thuật ma thuật").
- (#204) Luôn viết hoa danh từ chủng tộc/quái vật Ma Cà Rồng và danh hiệu Thợ Săn Ma Cà Rồng trong mọi văn cảnh theo đúng glossary.md.
- (#209) Rina Rupaage khi nói chuyện với tiền bối mạo hiểm giả hoặc đồng đội lớn tuổi hơn (Rentt, Lorraine, Nive...) luôn tự xưng "tôi", gọi "anh Rentt", "chị Lorraine", "chị Nive", không tự xưng "em" — nhất quán với pronouns.md.
- (#216) Cụm từ "smiled vaguely": dịch là "mỉm cười gượng gạo / cười gượng xã giao", tránh dịch máy thô từng chữ thành "nở nụ cười mơ hồ".
- (#216) Từ "carriage": trong thế giới truyện có nhiều cỗ xe do quái vật hoặc thú bò sát (như Thằn Lằn Bò Trườn) kéo, dịch là "cỗ xe / xe kéo" thay vì tự động dịch thành "cỗ xe ngựa" khi văn cảnh không phải do ngựa kéo.
- (#216) Lính gác cổng thành (kể cả vương đô hay các thị trấn): luôn xưng hô chuẩn mực "tôi - anh/chị/cậu/các vị" theo văn phong fantasy đời thường, tuyệt đối không dùng "ta - ngươi" kiểu kiếm hiệp/tiên hiệp.
- (#219) Cụm từ "last will and testament": dịch là "bản di chúc" hoặc "di chúc thừa kế", tránh dịch thô tách rời hai từ đồng nghĩa pháp lý thành "bản di chúc và thư để lại".
- (#221) Đại từ số ít "they": cẩn thận khi chuyển ngữ đại từ ngôi thứ ba trung tính số ít "they / them" chỉ một nhân vật cụ thể (như Jean Seebeck / Tổng Hội Trưởng) tránh dịch máy thành số nhiều "họ" (chuyển thành "ông ấy / ngài ấy / người đó").
- (#221) Xưng hô đối với Ingo Faina: Rentt trong lời dẫn chuyện và đối thoại luôn gọi là "cha tôi" hoặc "cha", không dùng "bố tôi".
- (#221) Cụm từ "last resort": dịch là "giải pháp cuối cùng" hoặc "hạ sách", tránh ghép thừa từ thành "hạ sách cuối cùng".
- (#222) Xưng hô đối với Sơ Lillian: luôn dùng "Sơ Lillian / sơ ấy / sơ" trong cả đối thoại lẫn lời dẫn chuyện, tránh dùng "cô ấy" gây suồng sã và thiếu tự nhiên với nữ tu lớn tuổi.
- (#224) Cụm từ "accumulative malice disease": raw dùng thay thế cho "Accumulative Miasma Disease", dịch thống nhất là "Bệnh Tích Tụ Chướng Khí" theo glossary.md (tránh dịch lệch thành "bệnh tích tụ ác ý").
- (#224) Danh xưng giáo phẩm Abbess (Nữ Tu Viện Trưởng): là phẩm trật cao cấp tương đương Giám mục/Hồng y, giao tiếp trang trọng dùng "ngài / Nữ Tu Viện Trưởng / Mẹ Bề Trên", không gọi hạ cấp thành "sơ" (Sister); trong lời dẫn chuyện gọi "cô ấy / Nữ Tu Viện Trưởng Elza", tránh dùng "sơ ấy" gây nhầm lẫn với Sơ Lillian.
- (#226) Tên quán trọ Falcon’s Rest Inn tại vương đô nơi Augurey lưu trú: dịch là "Quán Trọ Falcon's Rest" (nguyên tác 鷹の羽休め亭 - quán trọ chim ưng dừng cánh).
- (#230) Phân biệt "Holy Tree" và "Venerable Holy Tree": "Holy Tree" dịch là "Thánh Thụ" (cái cây thần/thực thể linh thiêng của High Elf); "Venerable Holy Tree" dịch là "Cổ Thánh Thụ" (thường xuất hiện trong danh xưng xứ sở "Land of the Venerable Holy Tree" → "Vùng Đất Cổ Thánh Thụ"), tránh dịch nhầm "Holy Tree" thành "Cổ Thánh Thụ".
- (#234) Danh từ chung "monster(s)": dịch thống nhất là "quái vật", không dùng từ Hán Việt "ma vật".
- (#237) Phân biệt "Skeleton" (quái vật Undead → viết hoa "Khô Lâu") và danh từ chung "skeleton" chỉ bộ khung xương cơ thể ("my skeleton" → "bộ xương / khung xương"), tránh dịch máy thành "Khô Lâu".
- (#238) Cụm từ "pulling the strings behind the curtains": dịch là "kẻ giật dây sau bức màn" (tránh nhầm thuật ngữ "Pulling" trong game là "dụ quái").
- (#238) Cụm từ "average Joes": dịch là "những người dân bình thường / thường dân" (thành ngữ chỉ người bình thường, không phải tên riêng người tên Joe).
- (#239) Cụm từ "plain-Jane villager": dịch là "cô thôn nữ bình thường / mộc mạc" (thành ngữ tiếng Anh chỉ cô gái bình thường, tránh nhầm tên riêng Jane).
- (#243) Tránh dùng từ ngữ công nghệ hiện đại như "dây điện" trong bối cảnh kỳ ảo trung cổ khi miêu tả các hiệu ứng ma pháp điện/sấm sét (dùng "chấn song sét / vệt lôi điện / tia điện / luồng điện").
- (#243) Thành ngữ "real-life": dịch linh hoạt ("ngoài đời thực / thực sự / bằng xương bằng thịt") tùy theo đối tượng, tránh dịch máy "bằng xương bằng thịt" cho các sinh vật dạng bán thể lỏng hoặc nguyên tố phi thể xác.
- (#248) Cụm từ "turned into paste" / "crushed to a pulp": dịch thống nhất là "đè bẹp dí thành tương" hoặc "nghiền nát bấy thành tương" (tránh dùng "tương cà" lệch bối cảnh fantasy trung cổ).
- (#250) Tránh dùng đại từ ước lệ cổ trang "nàng" khi dịch "she" chỉ công chúa (dùng "cô ấy"); luôn viết hoa đầy đủ các danh hiệu hoàng tộc ("Đệ Nhất Công Chúa", "Nhị Công Chúa", "Đệ Nhất Hoàng Tử").
- (#254) Cụm từ "on the contrary" khi mang nghĩa tiếp nối/bổ sung mức độ ("thậm chí / tệ hơn nữa là"): dịch là "trái lại / thậm chí", tránh dịch máy thành "ngược lại".
- (#255) Xưng hô của Rentt đối với Spriggan: luôn xưng "tôi", gọi "ông" một cách đĩnh đạc, bình đẳng, không dùng kính ngữ quá đà ("dạ", "ạ") biến Rentt thành đứa trẻ khép nép.
- (#255) Từ "fairy": dịch là "nàng tiên" khi chỉ tiên nữ tí hon có cánh (như Tilya ở #140), dịch là "loài tiên / chủng tiên" khi nói về phân loài cổ tích thần thoại (như Spriggan ở #255).
