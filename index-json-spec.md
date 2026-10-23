# Spec: `index.json` cho repo `craw-novel`

## Mục đích

App Novel Reader cần biết repo có những truyện nào, mỗi truyện có những chương nào. Hiện app lấy thông tin này qua GitHub REST API, mà API khi chưa đăng nhập bị giới hạn 60 request/giờ cho mỗi IP.

Cần sinh sẵn một file `index.json` ở gốc repo, liệt kê toàn bộ truyện và chương. App sẽ tải file này qua `raw.githubusercontent.com` (không tính vào giới hạn của API) nên không phải gọi GitHub API nữa.

## Vị trí và cách app đọc

- File: `index.json` ở **gốc repo**, nhánh `main`.
- App tải file từ: `https://raw.githubusercontent.com/ngduyminhquan/craw-novel/main/index.json`
- Nội dung chương app tải từ: `https://raw.githubusercontent.com/ngduyminhquan/craw-novel/main/<chapter.path>`
- Mã hóa UTF-8, **không có BOM**. Thụt lề 2 dấu cách.

## Cấu trúc

```json
{
  "schemaVersion": 1,
  "generatedAt": "2026-10-23T08:15:00Z",
  "novels": [
    {
      "slug": "everyone-else-is-a-returnee",
      "title": "Everyone Else Is A Returnee",
      "chapters": [
        {
          "number": 1,
          "title": "Chương 1: Mở đầu",
          "path": "translations/everyone-else-is-a-returnee/vi/Chapter_001.md",
          "sha": "3b18e512dba79e4c8300dd08aeb37f8e728b8dad"
        },
        {
          "number": 2,
          "title": "Chương 2: Tôi sống một mình (1)",
          "path": "translations/everyone-else-is-a-returnee/vi/Chapter_002.md",
          "sha": "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391"
        }
      ]
    }
  ]
}
```

## Định nghĩa từng trường

### Gốc

| Trường | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `schemaVersion` | int | có | Luôn là `1`. Chỉ tăng khi thay đổi cấu trúc mà bản app cũ không đọc được. |
| `generatedAt` | string | có | Thời điểm sinh file, ISO-8601 UTC (`yyyy-MM-ddTHH:mm:ssZ`). |
| `novels` | array | có | Danh sách truyện, sắp xếp theo `slug` tăng dần. Không có truyện nào thì là `[]`. |

### `novels[]`

| Trường | Kiểu | Bắt buộc | Nguồn dữ liệu |
|---|---|---|---|
| `slug` | string | có | Tên thư mục con trong `translations/`. Ví dụ `translations/everyone-else-is-a-returnee/` cho ra `everyone-else-is-a-returnee`. App dùng slug làm khóa chính, nên **không được đổi** khi truyện đã phát hành. |
| `title` | string | có | Trường `title` trong `translations/<slug>/novel.json`, đã bỏ khoảng trắng hai đầu. Nếu không có file, không có trường này hoặc giá trị rỗng thì dùng `slug`. |
| `chapters` | array | có | Danh sách chương đã dịch, sắp xếp theo `number` tăng dần. Chưa có chương nào thì là `[]`. |

Chỉ tính **thư mục con trực tiếp** của `translations/`, bỏ qua mọi file nằm thẳng trong `translations/`.

### `novels[].chapters[]`

Mỗi chương ứng với **một file** trong `translations/<slug>/vi/` có tên khớp regex `^Chapter_(\d+)\.md$`. File không khớp regex thì bỏ qua.

| Trường | Kiểu | Bắt buộc | Nguồn dữ liệu |
|---|---|---|---|
| `number` | int | có | Số bắt được trong tên file, đã bỏ số 0 ở đầu. `Chapter_001.md` cho ra `1`. |
| `title` | string | có | Dòng đầu tiên **có chữ** của file (sau khi bỏ BOM nếu có), nếu dòng đó bắt đầu bằng `# `: lấy phần sau `# ` và bỏ khoảng trắng hai đầu. Ví dụ `# Chương 1: Mở đầu` cho ra `Chương 1: Mở đầu`. Nếu dòng đó không bắt đầu bằng `# ` thì dùng chuỗi rỗng `""`. |
| `path` | string | có | Đường dẫn file **tính từ gốc repo**, dùng `/` làm dấu phân cách, không có `/` ở đầu. |
| `sha` | string | có | Git blob SHA của file (40 ký tự hex, chữ thường). Đây cũng là giá trị `sha` mà GitHub API trả về cho file đó. |

#### Về `sha`

- `sha` là hash nội dung file do Git tạo ra. App so sánh `sha` để biết chương có bị sửa không: `sha` đổi thì app tải lại, giữ nguyên thì app đọc từ cache.
- Lấy từ Git, **không tự tính** bằng cách khác:
  - `git ls-files -s -- "translations/*/vi/Chapter_*.md"`: cột thứ 2 là sha.
  - hoặc `git rev-parse HEAD:<path>` cho từng file.
- `sha` phải khớp với nội dung file **ở cùng commit** chứa `index.json`.

## Ràng buộc

- Không có hai truyện trùng `slug`. Trong một truyện, không có hai chương trùng `number` (nếu có cả `Chapter_01.md` và `Chapter_001.md` thì báo lỗi và dừng, không tự chọn một file).
- Không thêm trường nào ngoài spec này. App bỏ qua trường lạ, nhưng không được bỏ bớt hay đổi tên trường đã có.
- Thứ tự sắp xếp và định dạng phải ổn định: chạy lại trên cùng nội dung repo thì `index.json` **chỉ khác ở `generatedAt`**.
- Nếu thứ duy nhất thay đổi là `generatedAt` thì **không commit**, để tránh commit rác.

## Sinh file tự động

### Script

- Viết bằng Python 3, chỉ dùng thư viện chuẩn (không cần `pip install`). Đặt tại `scripts/build_index.py`.
- Chạy từ gốc repo: `python scripts/build_index.py`, ghi đè `index.json`.
- Thoát với mã khác 0 khi có lỗi dữ liệu (trùng `number`, `novel.json` sai định dạng JSON, ...) và in rõ file gây lỗi.

### GitHub Action

- File: `.github/workflows/build-index.yml`.
- Kích hoạt:
  - `push` vào `main` khi có thay đổi trong `translations/**` hoặc `scripts/build_index.py`.
  - `workflow_dispatch` để chạy tay.
- Các bước: checkout, chạy script, nếu `index.json` thay đổi (bỏ qua thay đổi chỉ ở `generatedAt`) thì commit với message `chore: update index.json` rồi push lên `main`.
- Cần `permissions: contents: write`.
- Không được tạo vòng lặp: commit do `GITHUB_TOKEN` tạo ra vốn không kích hoạt workflow, và `index.json` cũng không nằm trong bộ lọc `paths`.

## Tiêu chí nghiệm thu

- [ ] Chạy script trên repo hiện tại sinh ra `index.json` có truyện `everyone-else-is-a-returnee` với đủ số chương đang có trong thư mục `vi/`.
- [ ] `number` liên tục khớp với tên file, `title` khớp dòng `# ...` đầu mỗi file.
- [ ] `sha` của mỗi chương trùng với `sha` mà `https://api.github.com/repos/ngduyminhquan/craw-novel/contents/<path>` trả về.
- [ ] Mỗi `path` ghép vào `https://raw.githubusercontent.com/ngduyminhquan/craw-novel/main/` đều tải được (HTTP 200).
- [ ] Chạy script hai lần liên tiếp thì chỉ `generatedAt` khác nhau.
- [ ] Sửa một chương rồi push lên thì Action chạy, `sha` của đúng chương đó đổi, các chương khác giữ nguyên.
- [ ] Thêm một chương mới hoặc một truyện mới rồi push lên thì xuất hiện trong `index.json` đúng thứ tự.
