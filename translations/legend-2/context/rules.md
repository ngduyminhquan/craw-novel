# Quy tắc dịch — Legend 2

Quy tắc cứng, áp dụng cho mọi chương. Mâu thuẫn giữa file này và các file context khác thì file này thắng.
Thêm quy tắc mới khi gặp một trường hợp cần xử lý thống nhất về sau (ghi kèm chương phát hiện).

## Tên riêng

- Tên nhân vật Nhật Bản: phiên âm Romaji chuẩn Hepburn, không dấu (vd `佐伯玲二` → `Saeki Reiji`, `タクム・スズノセ` → `Suzunose Takumu`).
- Tên nhân vật, địa danh phương Tây / dị giới (Katakana): dùng phiên âm Latin chuẩn đã thống nhất với phần `legend-1` (vd `レイ` → `Rei`, `セト` → `Set`, `エルジィン` → `Elgin`, `ギルム` → `Gilm`, `ダスカー` → `Daska`, `ヴィヘラ` → `Vihera`, `ニールセン` → `Nielsen`, `ボブ` → `Bob`, `ガメリオン` → `Gamelion`).
- Bản dịch luôn dùng MỘT cách viết đã chốt trong `characters.md` và `glossary.md`; các cách viết khác trong raw ghi vào cột `Alias`.

## Thuật ngữ, kỹ năng, danh hiệu, vật phẩm

- Tên kỹ năng, ma thuật, danh hiệu, chức nghiệp, vật phẩm ma thuật: dịch sang tiếng Việt / Hán Việt ngắn gọn, tự nhiên, đồng bộ 100% với `legend-1` (vd `魔獣術` → `Ma Thú Thuật`, `デスサイズ` → `Lưỡi Hái Tử Thần`, `ミスティリング` → `Nhẫn Sương Mù`, `ドラゴンローブ` → `Áo Choàng Rồng`, `黄昏の槍` → `Thương Hoàng Hôn`, `ネブラの瞳` → `Con Mắt Nebula`).
- Mọi thuật ngữ phải có trong `glossary.md` TRƯỚC khi dùng trong bản dịch. Đã chốt thì dùng đúng chữ đó ở mọi chương.
- Cấp bậc mạo hiểm giả và quái vật (`ランクB` → `Hạng B`, `ランクS` → `Hạng S`).

## Định dạng

- Dòng đầu file: `# Chương N: <tiêu đề dịch>` với N là cột `#` trong `progress.md`.
- Mỗi đoạn raw là một đoạn dịch trên một dòng, cách nhau một dòng trống. Không gộp, không tách, không bỏ đoạn, không ngắt một đoạn ra nhiều dòng.
- App đọc file theo dòng, không render Markdown: `*`, `_` hiện nguyên ký tự. Ảnh và dòng điều hướng theo `chapter-image-guide.md` ở repo root.
- Lời thoại (`「...」` trong raw): chuyển thành ngoặc kép thẳng `"..."`.
- Lời niệm chú, thông báo hệ thống, tên vật phẩm hiển thị trong tâm trí (`『...』` trong raw): chuyển thành `[...]` hoặc ngoặc kép tùy ngữ cảnh; thông báo hệ thống và tên kỹ năng/vật phẩm hiển thị dùng `[...]`.
- Suy nghĩ nội tâm (`（...）` trong raw): giữ trong ngoặc đơn `(...)`.
- Không dùng in nghiêng/in đậm Markdown (`*...*`, `_..._`).

## Ghi chú translator

- Bỏ hẳn mọi ghi chú tác giả/translator nếu không thuộc nội dung truyện.

## Riêng truyện này

- (#1) Phần tiếp nối trực tiếp từ chương 3000 của `legend-1` (chương #1 của `legend-2` tương ứng với chương 3001 của bộ gốc).
- (#1) Tiếng kêu của Set (`グルゥ`, `グルルゥ`, `グルルルゥ`) dịch tự nhiên theo ngữ cảnh (`"Grrr"`, `"Gừưư"`, `"Gùuu"`).
