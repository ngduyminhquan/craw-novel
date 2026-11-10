Chế độ orchestrator. Dùng skill `novel-translate`: đọc `.agents/skills/novel-translate/SKILL.md` trước, gồm cả mục "Chạy dưới orchestrator".

Repo: $root

Việc: review các chương $range của truyện `$slug` theo `.agents/skills/novel-translate/docs/review.md` (đọc file này sau `SKILL.md`).

Đọc bắt buộc trước khi review (đọc hết từng file): `.agents/skills/novel-translate/docs/review.md`, `.agents/skills/novel-translate/natural-vietnamese.md` (tiêu chí bắt lỗi văn dịch máy), `translations/$slug/context/rules.md`, `translations/$slug/context/style.md`. Ghi trong báo cáo là đã đọc các file này.

Chỉ đọc. Không sửa bản dịch, file context hay `progress.md`. Không chạy git.

Báo cáo dùng đúng mẫu trong `docs/review.md`: lỗi theo từng chương, đề xuất cập nhật context, câu hỏi. Mỗi lỗi phải có số đoạn, trích nguyên văn chỗ hiện tại và câu đề xuất, để người sửa không phải tìm lại.
