Chế độ orchestrator. Dùng skill `novel-translate`: đọc `.agents/skills/novel-translate/SKILL.md` trước, gồm cả mục "Chạy dưới orchestrator".

Repo: $root

Việc: sửa các chương $range của truyện `$slug` theo mục D của skill.
- Báo cáo review: `$review_report`
- File quyết định của orchestrator: `$decisions`. File này có quyền cao hơn báo cáo review: chỉ sửa mục được chấp nhận, sửa đúng cách ghi trong file.

Không sửa chương nào ngoài $range. Không chạy git.

Tiêu chí xong:
- Đã xử lý mọi mục được chấp nhận.
- Đã cập nhật context theo file quyết định.
- `python .agents/skills/novel-translate/scripts/qa_check.py $slug $range` không còn `[LỖI]`.
- Các chương $range trong `progress.md` là `reviewed`.

Báo cáo gồm:
- số lỗi đã sửa ở từng chương;
- thay đổi trong context;
- mục không sửa được, kèm lý do.
