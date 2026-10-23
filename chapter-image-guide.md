HƯỚNG DẪN: NHÚNG ẢNH VÀO CHƯƠNG TRUYỆN (repo craw-novel)
=========================================================

Bổ sung cho: index-json-spec.md
Áp dụng cho: translations/<slug>/vi/Chapter_XXX.md
index.json: KHÔNG đổi cấu trúc, schemaVersion vẫn là 1.


1. CÁCH APP NOVEL READER ĐỌC FILE CHƯƠNG
----------------------------------------

App KHÔNG render Markdown. Nó đọc file theo từng dòng:

  - Dòng có chữ đầu tiên bắt đầu bằng "# " là tiêu đề, app bỏ dòng này
    khỏi nội dung (tiêu đề đã có trong index.json).
  - Dòng trống thì bỏ qua.
  - Dòng điều hướng giữa các chương thì bỏ qua, ví dụ:
        [← Chương trước](Chapter_009.md) | [Chương tiếp theo →](Chapter_011.md)
  - Dòng chỉ chứa đúng một ảnh (xem mục 2) thì thành một khối ảnh.
  - Mọi dòng còn lại là một đoạn văn, giữ nguyên từng ký tự.

Vì vậy những quy ước hiện có PHẢI giữ nguyên:

  - Mỗi đoạn văn nằm trên một dòng, giữa hai đoạn có một dòng trống.
    Không ngắt một đoạn ra nhiều dòng.
  - Dấu * và _ là ký tự bình thường, KHÔNG phải in đậm/in nghiêng.
    Ví dụ chữ bị che "M** ***t" phải được giữ nguyên như vậy.
  - [ ... ] là lời thoại của thực thể cấp cao hoặc giao diện hệ thống,
    không phải link.
  - Dòng điều hướng ở cuối chương phải giữ đúng định dạng:
    [<chữ>](Chapter_<số>.md), nhiều link thì ngăn cách bằng " | ".
    Đổi định dạng là app sẽ hiển thị dòng này như một đoạn văn.


2. CÚ PHÁP NHÚNG ẢNH
--------------------

Mỗi ảnh nằm trên MỘT DÒNG RIÊNG, có dòng trống ở trước và sau:

    Đoạn văn phía trước.

    ![Bản đồ tầng 1 của Tháp](images/ch012-ban-do-tang-1.webp)

    Đoạn văn phía sau.

Quy tắc:

  - Cả dòng phải đúng dạng:  ![<chú thích>](<đường dẫn>)
    Không có chữ nào khác trên dòng đó, kể cả chữ ở trước hay sau.
  - Ảnh nằm giữa một đoạn văn (ví dụ "Xem ![ảnh](a.png) nhé") sẽ KHÔNG
    được nhận là ảnh mà hiển thị như chữ thường. Không dùng kiểu này.
  - <chú thích> có thể để trống: ![](images/abc.webp). Không được chứa
    dấu "]".
  - <đường dẫn> là đường dẫn TƯƠNG ĐỐI tính từ file chương, không được
    chứa dấu ")" và không có tiêu đề kiểu ![a](b.webp "title").
    App ghép đường dẫn này với URL raw của file chương để ra URL ảnh:
      chương: translations/<slug>/vi/Chapter_012.md
      ảnh:    images/ch012-ban-do-tang-1.webp
      =>      https://raw.githubusercontent.com/ngduyminhquan/craw-novel/main/translations/<slug>/vi/images/ch012-ban-do-tang-1.webp
  - Không dùng thẻ HTML <img>.


3. QUY ƯỚC FILE ẢNH
-------------------

  - Thư mục: translations/<slug>/vi/images/
  - Tên file: chữ thường, không dấu, không khoảng trắng, chỉ gồm a-z 0-9 và
    dấu "-". Nên có tiền tố số chương để dễ tìm, ví dụ ch012-ban-do-tang-1.webp
  - Định dạng: .webp (khuyến nghị), .png, .jpg/.jpeg.
  - Kích thước: chiều rộng tối đa 1600px, dung lượng nên dưới 500KB.

  - QUAN TRỌNG: KHÔNG GHI ĐÈ file ảnh đã push. Muốn thay ảnh thì tạo file
    mới với tên khác (ví dụ thêm -v2) rồi sửa dòng ![..](..) trong chương.
    Lý do: app biết chương có thay đổi nhờ sha của file .md. Ghi đè ảnh mà
    giữ nguyên tên thì file .md không đổi, nên app vẫn hiện ảnh cũ đã cache.
  - Chỉ xoá một file ảnh khi không còn chương nào dùng đến nó.


4. CẦN BỔ SUNG VÀO scripts/build_index.py
-----------------------------------------

Không đổi định dạng index.json (ảnh không được liệt kê trong index).
Thêm phần kiểm tra cho mỗi file chương. Có lỗi thì in ra file:dòng gây lỗi
và thoát với mã khác 0:

  a) Với mỗi dòng (đã bỏ khoảng trắng hai đầu) khớp regex
         ^!\[([^\]]*)]\(([^)]+)\)$
     thì kiểm tra:
       - Đường dẫn ảnh không bắt đầu bằng "/" và không phải URL tuyệt đối
         (http://, https://).
       - Ghép đường dẫn với thư mục của file chương ra một file NẰM TRONG
         repo, và file đó tồn tại.
       - Đuôi file là .webp, .png, .jpg hoặc .jpeg (không phân biệt hoa thường).
  b) Một dòng có chứa "![" nhưng KHÔNG khớp regex ở (a), tức là ảnh lẫn
     trong đoạn văn hoặc viết sai cú pháp: báo lỗi.

Regex ở (a) giống hệt regex app dùng. Không sửa một bên mà không sửa bên kia.


5. CẦN BỔ SUNG VÀO .github/workflows/build-index.yml
---------------------------------------------------

  - Thêm "translations/**/images/**" vào bộ lọc paths, nếu translations/**
    hiện tại chưa bao gồm.
  - Thêm một bước chạy TRƯỚC build_index.py: chặn việc ghi đè ảnh. Nếu
    trong lần push có file nằm trong translations/*/vi/images/ bị sửa
    (trạng thái M, ví dụ lấy từ git diff --name-status <before>..<after>)
    thì báo lỗi, ghi rõ tên file và nhắc "đổi tên file thay vì ghi đè".
    Dùng github.event.before và github.sha để lấy khoảng commit.
    Khi github.event.before toàn số 0 (push đầu tiên) thì bỏ qua bước này.


6. TIÊU CHÍ NGHIỆM THU
----------------------

  [ ] Thêm một ảnh hợp lệ vào một chương rồi push: Action chạy thành công,
      sha của đúng chương đó trong index.json đổi.
  [ ] URL ghép theo mục 2 tải được ảnh (HTTP 200).
  [ ] Tham chiếu tới ảnh không tồn tại: build_index.py báo lỗi và thoát với
      mã khác 0, index.json không bị commit.
  [ ] Viết ảnh lẫn trong đoạn văn: build_index.py báo lỗi.
  [ ] Ghi đè một ảnh đã có rồi push: Action báo lỗi ở bước chặn ghi đè.
  [ ] 61 chương hiện có (chưa có ảnh nào) vẫn qua kiểm tra, index.json
      không đổi gì ngoài generatedAt.
