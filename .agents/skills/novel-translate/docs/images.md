# Ảnh trong chương

Phần của skill `novel-translate`. Chỉ thêm, thay hay xoá ảnh khi user yêu cầu. Chi tiết và lý do: `chapter-image-guide.md` ở repo root.

1. **File ảnh** đặt trong `translations/<slug>/vi/images/`:
   - tên chữ thường, chỉ gồm `a-z`, `0-9`, `-`, có tiền tố số chương: `ch012-ban-do-tang-1.webp`;
   - định dạng `.webp` (nên dùng), `.png`, `.jpg`/`.jpeg`;
   - rộng tối đa 1600px, nên dưới 500KB.
2. **Dòng ảnh** trong chương: nằm riêng một dòng, có dòng trống trước và sau, cả dòng đúng dạng
   ```
   ![Bản đồ tầng 1 của Tháp](images/ch012-ban-do-tang-1.webp)
   ```
   - Đường dẫn tương đối tính từ file chương: không `/` ở đầu, không URL `http(s)://`, không chứa `)`, không có tiêu đề kiểu `"title"`.
   - Chú thích được để trống, không chứa `]`.
   - Không đặt ảnh lẫn trong đoạn văn, không dùng thẻ `<img>`.
   - Dòng ảnh không tính là đoạn dịch, nên `qa_check.py` không đếm nó.
3. **Không ghi đè ảnh đã push.** Muốn thay ảnh thì tạo file tên mới (vd thêm `-v2`) rồi sửa dòng `![..](..)` trong chương. Lý do: app chỉ tải lại chương khi sha của file `.md` đổi, ghi đè ảnh cùng tên thì app vẫn hiện ảnh cũ đã cache. GitHub Action chặn push có ảnh bị sửa. Chỉ xoá file ảnh khi không còn chương nào dùng.
4. Kiểm tra bằng `python scripts/build_index.py`: script báo `[LỖI] <file>:<dòng>` khi ảnh không tồn tại (kể cả sai chữ hoa/thường), sai đuôi file, đường dẫn tuyệt đối hoặc trỏ ra ngoài repo, hay khi một dòng có `![` mà không đúng dạng ở bước 2. Commit ảnh **cùng lúc** với chương dùng nó.
