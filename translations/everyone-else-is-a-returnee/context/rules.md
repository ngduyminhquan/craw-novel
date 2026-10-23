# Quy tắc dịch — Everyone Else Is A Returnee

Quy tắc cứng, áp dụng cho mọi chương. Mâu thuẫn giữa file này và các file context khác thì file này thắng.
Thêm quy tắc mới khi gặp một trường hợp cần xử lý thống nhất về sau (ghi kèm chương phát hiện).

## Tên riêng

- Tên người Hàn: giữ phiên âm Latin đúng như raw (vd `Yu IlHan`), không chuyển Hán Việt, không tự đổi cách viết hoa/gạch nối.
- Tên phương Tây, thiên thần, thần, quái vật có tên riêng: giữ nguyên như raw.
- Raw đổi translator nên một tên có thể có nhiều cách viết EN. Bản dịch luôn dùng MỘT cách viết đã chốt trong characters.md; các cách viết khác ghi vào cột Alias.

## Thuật ngữ, kỹ năng, danh hiệu, vật phẩm

- Tên kỹ năng, danh hiệu, chức nghiệp, cấp bậc: dịch sang Hán Việt, ngắn gọn, viết hoa chữ cái đầu mỗi chữ (vd `Phản Kích`). Không giữ tiếng Anh trong ngoặc.
- Mọi thuật ngữ phải có trong glossary.md TRƯỚC khi dùng trong bản dịch. Đã chốt thì dùng đúng chữ đó ở mọi chương.
- Đơn vị, chỉ số trò chơi (Lv, HP, MP, EXP, stat...): giữ dạng viết tắt quen thuộc với độc giả game (Lv, HP, MP, EXP).

## Định dạng

- Dòng đầu file: `# Chương N: <tiêu đề dịch>` với N là cột `#` trong progress.md.
- Mỗi đoạn raw là một đoạn dịch, cách nhau một dòng trống. Không gộp, không tách, không bỏ đoạn.
- Lời thoại: ngoặc kép thẳng `"..."`.
- Thông báo hệ thống, lời nói qua thần giao cách cảm, thông tin kỹ năng: giữ trong `[...]` như raw.
- Không dùng in nghiêng/in đậm Markdown (`*...*`, `_..._`): app hiện nguyên dấu `*`. Chữ in nghiêng trong raw (tiếng động, tiếng kêu, nhấn mạnh) viết thường, không có dấu `*`. Suy nghĩ nội tâm raw dùng ngoặc đơn thì giữ ngoặc đơn. Riêng chữ bị che một phần bằng `*` (vd `M** ***t`) thì giữ dấu `*`. (Đổi ngày 2026-10-23 theo yêu cầu user: đã bỏ `*` in nghiêng ở chương 33, 42, 44, 47, 50, 56.)
- Cuối mỗi chương bắt buộc thêm dòng điều hướng dẫn đến chương trước và chương sau (cách nội dung chính một dòng trống) theo mẫu:
  - Chương đầu (`#1`): `[Chương tiếp theo →](Chapter_002.md)`
  - Các chương giữa (`#N`): `[← Chương trước](Chapter_<N-1_3_chữ_số>.md) | [Chương tiếp theo →](Chapter_<N+1_3_chữ_số>.md)` (ví dụ ở chương 2: `[← Chương trước](Chapter_001.md) | [Chương tiếp theo →](Chapter_003.md)`). Nếu chương liền trước/sau bị `skip` thì trỏ tới chương `todo`/`done` hợp lệ kế tiếp.
  - Chương cuối cùng: `[← Chương trước](Chapter_<N-1_3_chữ_số>.md)`

## Ghi chú translator

- Bỏ hẳn mọi ghi chú translator (T/N, TL note...) của raw, không dịch, không chuyển thành chú thích.
- Nếu T/N giải thích một cách chơi chữ cần thiết để hiểu câu, xử lý ngay trong câu dịch (diễn đạt lại) thay vì thêm chú thích.

## Riêng truyện này

- (#1) Các dòng quy ước ký hiệu ở đầu raw ('Thinking', "Speaking", [Higher existence's speaking...]) là ghi chú format của bản dịch EN, bỏ qua không dịch.
- (#8) Khi câu truyện có chú thích `(T/N: ...)` nằm cùng dòng (inline) thì chỉ bỏ phần `(T/N: ...)`, tuyệt đối không bỏ nội dung câu truyện.
- (#12) Bỏ các cụm quy đổi tiền tệ sang USD kẹp trong ngoặc đơn sau số tiền won (vd `(322,561 USD)`), vì đây là ghi chú quy đổi tỷ giá của translator bản tiếng Anh.
- Link điều hướng bỏ qua các chương `skip` trong progress.md: chương #289 trỏ tới #293 và ngược lại (#290–#292 là bản trùng).
- (#1) Ba dòng chú giải ký hiệu ở đầu raw chương 1 đã được thêm vào `raw_ignore_lines` trong `novel.json`.
- (#20) Cụm từ `strong friends` trong raw EN (khẩu hiệu `강한 친구` của Lục quân Hàn Quốc) dịch thoát ý thành `những anh bạn quân đội mạnh mẽ` hoặc `quân đội` để rõ nghĩa.
- (#13) Khi tên chức nghiệp, kỹ năng hoặc danh hiệu bị che một phần bằng dấu sao '*' để tạo tình huống hiểu lầm hài hước (vd 'Bl****d Lancer' làm nhân vật tưởng là 'Blood' nhưng thật ra là 'Blurred'), phải Việt hóa cả cụm từ bị che theo bản dịch đã chốt (giữ chữ cái đầu/cuối và thay phần giữa bằng dấu '*', vd 'Thương Thủ M** ***t' cho 'Thương Thủ Mờ Nhạt') và dịch thoát ý lời giải thích chơi chữ cho khớp tự nhiên bằng tiếng Việt, không để nguyên tiếng Anh.
- (#42) Luôn viết hoa tên vũ khí đặc trưng Súng Bắn Cọc kể cả khi raw tiếng Anh viết thường pile bunker.
