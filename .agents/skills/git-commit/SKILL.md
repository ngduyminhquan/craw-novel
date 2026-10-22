---
name: git-commit
description: Dùng khi người dùng yêu cầu commit các thay đổi trong mã nguồn. Kích hoạt để tự động đọc các file thay đổi, suy luận ra nội dung commit tuân thủ Git Convention (Conventional Commits), và đề xuất nội dung cho người dùng phê duyệt trước khi tiến hành commit.
---

# Tự động hóa Commit tuân thủ Git Convention (dành cho Antigravity)

## Tổng quan

Quy trình này hướng dẫn cách đọc các thay đổi mã nguồn hiện tại, suy luận thông điệp commit chuẩn hóa và yêu cầu phê duyệt từ người dùng trước khi tạo commit.

## Quy trình thực hiện

### Bước 1 — Kiểm tra thay đổi (Git Status & Diff)

Chạy các lệnh sau để kiểm định trạng thái và nội dung thay đổi:

```bash
# Xem các tệp tin đã thay đổi
git status

# Xem nội dung chi tiết các thay đổi
git diff
```

### Bước 2 — Suy luận nội dung Commit theo Git Convention

Dựa trên các thay đổi đã phân tích ở Bước 1, soạn thảo thông điệp commit tuân thủ **Conventional Commits** với cấu trúc:

`<type>(<scope>): <description>`

Trong đó `<type>` phải thuộc các loại sau:
- **feat**: Một tính năng mới.
- **fix**: Sửa lỗi.
- **docs**: Thay đổi về tài liệu.
- **style**: Thay đổi về định dạng code (khoảng trắng, dấu chấm phẩy...) không làm thay đổi logic code.
- **refactor**: Tái cấu trúc mã nguồn không sửa lỗi cũng không thêm tính năng mới.
- **test**: Thêm hoặc sửa đổi các bộ kiểm thử.
- **chore**: Các thay đổi phụ trợ khác (cập nhật dependency, cấu hình dự án, cấu trúc thư mục...).

*Ví dụ:* `chore(playwright): initialize playwright project` hoặc `fix(auth): resolve login validation issue`.

### Bước 3 — Đề xuất thông điệp cho người dùng phê duyệt

**BẮT BUỘC:** Hiển thị thông điệp đề xuất và danh sách các tệp tin sẽ được commit lên khung chat để người dùng kiểm tra.
Không được tự ý chạy lệnh `git commit` trước khi nhận được sự đồng ý rõ ràng từ người dùng.

### Bước 4 — Thực hiện commit sau khi được phê duyệt

Sau khi nhận được sự đồng ý (ví dụ: "OK", "Đồng ý", "Chạy đi", v.v.):
1. Đưa các thay đổi vào vùng chờ: `git add .` (hoặc các file cụ thể).
2. Tạo commit: `git commit -m "<thông điệp đã duyệt>"`
