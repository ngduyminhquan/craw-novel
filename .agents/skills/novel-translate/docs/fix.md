# Sửa theo kết quả review

Phần của skill `novel-translate` (đọc `SKILL.md` trước). Dùng khi được giao báo cáo review kèm file quyết định của orchestrator.

1. Đọc file quyết định **trước** (brief thường chép sẵn nội dung). File này có quyền cao hơn báo cáo review: chỉ sửa các mục được **chấp nhận**, mục nào ghi cách sửa riêng thì sửa đúng cách đó, mục bị **bác** thì bỏ qua dù báo cáo review có đề xuất.
2. Sửa thẳng trong `vi/Chapter_NNN.md`, không đụng vào dòng ảnh và dòng điều hướng. Một lỗi có cùng kiểu (cùng thuật ngữ, cùng cặp xưng hô) thì sửa hết mọi chỗ trong các chương được giao, không chỉ chỗ được chỉ ra.
3. Cập nhật context theo các đề xuất đã được chấp nhận, bằng `ctx.py` như bước B4 trong `SKILL.md` (không sửa dòng xưng hô cũ mà thêm dòng mới). `rules.md`, `style.md` thì sửa thẳng.
4. Chạy `qa_check.py <slug> <range>` cho đến khi hết `[LỖI]`, và `lint_context.py <slug>`.
5. Đánh dấu: `progress.py <slug> set <range> reviewed`. Nếu brief bảo giữ nguyên trạng thái thì bỏ qua bước này.
6. Báo cáo: số lỗi đã sửa trong từng chương, những thay đổi context, các mục không sửa được và lý do.
