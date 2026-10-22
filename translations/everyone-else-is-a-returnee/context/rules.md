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
- Nhấn mạnh/suy nghĩ nội tâm trong raw dùng in nghiêng hoặc ngoặc đơn thì giữ đúng kiểu đó.
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
