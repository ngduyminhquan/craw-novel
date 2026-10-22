# Webnovel & Novellunar Chapter Crawler (Multi-Thread Batch)

Bộ công cụ Python tự động cào toàn bộ các chương của truyện **Everyone Else Is A Returnee** (và các truyện khác) từ hai nguồn:
1. **Webnovel** (Chương 1 -> 289): [`crawl_webnovel.py`](crawl_webnovel.py)
2. **Novellunar** (Chương 290 -> 360): [`crawl_novellunar.py`](crawl_novellunar.py)

Mỗi chương được lưu thành một file `.txt` riêng biệt với định dạng chuẩn UTF-8 trong cùng thư mục `Everyone Else Is A Returnee/`.

---

## Cơ chế hoạt động (3 luồng song song, mỗi luồng 20 chương/đợt)

- **Chạy đa luồng theo từng đợt (Round)**:
  - Mặc định **3 luồng** chạy song song.
  - Mỗi luồng tải **20 chương** trong 1 đợt (tổng 1 đợt = 3 x 20 = 60 chương).
  - Khi cả 3 luồng tải xong 20 chương của đợt đó, script sẽ tự động chuyển sang đợt tiếp theo.
  - Quá trình lặp lại liên tục cho đến khi tải hết toàn bộ truyện.

---

## Cài đặt thư viện

Cài đặt các thư viện cần thiết bằng lệnh:

```bash
pip install -r requirements.txt
```

*(Các thư viện chính gồm: `requests`, `beautifulsoup4`, `lxml`)*

---

## 1. Cào từ Webnovel (Chương 1 đến 289)

```bash
python crawl_webnovel.py
```

- **Mục tiêu**: `https://www.webnovel.com/vi/book/20846713406621205/55960120064004058`
- **Tùy chọn**:
  ```bash
  # Tùy chỉnh 3 luồng, 20 chương/đợt:
  python crawl_webnovel.py -t 3 -c 20

  # Tải từ một chương cụ thể (ví dụ chương 50):
  python crawl_webnovel.py -s 50

  # Giới hạn số lượng chương tải (ví dụ 30 chương):
  python crawl_webnovel.py -n 30
  ```

---

## 2. Cào từ Novellunar (Chương 290 đến 360)

```bash
python crawl_novellunar.py
```

- **Mục tiêu**: `https://novellunar.com/novel/everyone-else-is-a-returnee`
- Mặc định tải tiếp từ **chương 290** đến hết chương 360 và lưu vào thư mục `Everyone Else Is A Returnee/` đã có từ trước.
- **Tùy chọn**:
  ```bash
  # Tùy chỉnh số luồng và số chương mỗi đợt:
  python crawl_novellunar.py -t 3 -c 20

  # Tải từ một chương cụ thể khác (ví dụ từ chương 300):
  python crawl_novellunar.py -s 300

  # Giới hạn số lượng tải (ví dụ tải 10 chương):
  python crawl_novellunar.py -n 10

  # Ghi đè file nếu đã tồn tại:
  python crawl_novellunar.py --overwrite
  ```

---

## Cấu trúc thư mục sau khi cào hoàn tất

```text
craw-novel/
├── crawl_webnovel.py
├── crawl_novellunar.py
├── requirements.txt
├── README.md
└── Everyone Else Is A Returnee/
    ├── Chapter_001 - Prologue.txt
    ├── Chapter_002 - I Live Alone (1).txt
    ├── ...
    ├── Chapter_289 - I Will Prepare – 8.txt
    ├── Chapter_290 - Chapter 288_ I Will Prepare – 6.txt
    ├── Chapter_291 - Chapter 289_ I Will Prepare – 7.txt
    ├── ...
    └── Chapter_360 - Chapter 358_ Apocrypha (5).txt
```
