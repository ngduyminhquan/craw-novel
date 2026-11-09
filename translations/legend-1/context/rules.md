# Quy tắc dịch — Legend 1

Quy tắc cứng, áp dụng cho mọi chương. Mâu thuẫn giữa file này và các file context khác thì file này thắng.
Thêm quy tắc mới khi gặp một trường hợp cần xử lý thống nhất về sau (ghi kèm chương phát hiện).

## Tên riêng

- Tên nhân vật Nhật Bản: phiên âm Romaji chuẩn Hepburn, không dấu (vd `佐伯玲二` → `Saeki Reiji`, `タクム・スズノセ` → `Suzunose Takumu`).
- Tên nhân vật, địa danh phương Tây / dị giới (Katakana): dùng phiên âm Latin chuẩn đã thống nhất của bản Light Novel tiếng Anh chính thức (vd `レイ` → `Rei`, `セト` → `Set`, `ゼパイル・ゾンド` → `Zepairu Zondo`, `エルジィン` → `Elgin`, `ギルム` → `Gilm`).
- Bản dịch luôn dùng MỘT cách viết đã chốt trong `characters.md` và `glossary.md`; các cách viết khác trong raw ghi vào cột `Alias`.

## Thuật ngữ, kỹ năng, danh hiệu, vật phẩm

- Tên kỹ năng, ма thuật, danh hiệu, chức nghiệp, vật phẩm ma thuật: dịch sang tiếng Việt / Hán Việt ngắn gọn, tự nhiên, viết hoa chữ cái đầu mỗi chữ hoặc theo bảng `glossary.md` (vd `魔獣術` → `Ma Thú Thuật`, `死神の大鎌 / デスサイズ` → `Lưỡi Hái Tử Thần`, `ミスティリング` → `Nhẫn Sương Mù`, `ドラゴンローブ` → `Áo Choàng Rồng`).
- Mọi thuật ngữ phải có trong `glossary.md` TRƯỚC khi dùng trong bản dịch. Đã chốt thì dùng đúng chữ đó ở mọi chương.
- Cấp bậc mạo hiểm giả và quái vật (`ランクG` → `Hạng G`, `ランクS` → `Hạng S`).

## Định dạng

- Dòng đầu file: `# Chương N: <tiêu đề dịch>` với N là cột `#` trong `progress.md` (vd `# Chương 1: Đột kích bộ lạc Orc (1)`).
- Mỗi đoạn raw là một đoạn dịch trên một dòng, cách nhau một dòng trống. Không gộp, không tách, không bỏ đoạn, không ngắt một đoạn ra nhiều dòng.
- App đọc file theo dòng, không render Markdown: `*`, `_` hiện nguyên ký tự. Ảnh và dòng điều hướng theo `chapter-image-guide.md` ở repo root.
- Lời thoại (`「...」` trong raw): chuyển thành ngoặc kép thẳng `"..."`.
- Lời niệm chú, thông báo hệ thống, tên vật phẩm hiển thị trong tâm trí (`『...』` trong raw): chuyển thành `[...]` hoặc ngoặc kép tùy ngữ cảnh; thông báo hệ thống và tên kỹ năng/vật phẩm hiển thị dùng `[...]`.
- Suy nghĩ nội tâm (`（...）` trong raw): giữ trong ngoặc đơn `(...)`.
- Không dùng in nghiêng/in đậm Markdown (`*...*`, `_..._`).

## Ghi chú translator

- Bỏ hẳn mọi ghi chú tác giả/translator nếu không thuộc nội dung truyện.

## Riêng truyện này

- (#1) Raw tiếng Nhật gốc trên Kakuyomu. Nhân vật chính chương 1–2 tên là `佐伯玲二` (`Saeki Reiji`), từ chương 3 đổi tên thành `レイ` (`Rei`).
- (#3) Tiếng kêu của Set (`グルゥ`, `グルルゥ`, `グルルルゥ`) dịch tự nhiên theo ngữ cảnh (`"Grrr"`, `"Gừưư"`, `"Gùuu"`).
