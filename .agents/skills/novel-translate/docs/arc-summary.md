# Tóm tắt arc và story-so-far (layout 2)

Phần của skill `novel-translate` (đọc `SKILL.md` trước).

Truyện dài không thể đưa tóm tắt mọi chương vào mỗi lần dịch. Layout 2 nén theo ba tầng: tóm tắt chương (bước B4), tóm tắt arc, và `story-so-far.md`. `prepare.py` chỉ in `story-so-far`, tóm tắt 2 arc trước và tóm tắt chương của arc hiện tại.

Arc chia theo `arc_rule` trong `novel.json`, mỗi arc tối đa khoảng 20 chương. Arc gốc dài hơn bị chia thành nhiều phần, mỗi phần tính là một arc riêng. Xem arc của một chương bằng `ctx.py <slug> arc N`.

Khi mọi chương của một arc đã dịch xong (`orchestrate.py next` báo `action=arc-summary`, hoặc `ctx.py <slug> arc` liệt kê arc thiếu):

1. `ctx.py <slug> show-summaries <range của arc>`: đọc tóm tắt các chương. Chỉ đọc lại bản dịch khi tóm tắt không đủ để hiểu một diễn biến quan trọng.
2. Viết **tóm tắt arc** 5–10 dòng (tối đa 2000 ký tự): mục tiêu và diễn biến chính, kết quả, nhân vật mới quan trọng, thay đổi về quan hệ, sức mạnh, vật phẩm, địa điểm, và mạch còn dở chuyển sang arc sau. Ghi bằng `ctx.py <slug> set-arc-summary <arc> --file <file>`.
3. Đọc `story-so-far.md` hiện tại (file nhỏ, đọc trực tiếp được). Viết lại toàn bộ, tối đa 6000 ký tự, gồm ba phần:
   - `Bối cảnh`: thế giới, nhân vật chính, các mối quan hệ cốt lõi. Chỉ đổi khi có thay đổi lớn.
   - `Diễn biến`: các arc đã qua theo thứ tự thời gian. Arc càng cũ càng nén ngắn, nhiều arc cũ có thể gộp chung một câu. Giữ những chi tiết mà chương sau còn nhắc lại: lời hứa, kẻ thù còn sống, vật phẩm quan trọng, bí mật đã lộ.
   - `Đang dở`: các mạch chưa khép, mục tiêu hiện tại của nhân vật chính.

   Ghi bằng `ctx.py <slug> set-story <arc> --file <file>`. Lệnh từ chối khi file quá 6000 ký tự: nén các arc cũ lại rồi ghi lại.
4. Kiểm tra bằng `python .agents/skills/novel-orchestrator/scripts/orchestrate.py <slug> verify-arc <arc>`.
