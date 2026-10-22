#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script cào truyện từ Webnovel (https://www.webnovel.com)
Hỗ trợ:
- Chạy đa luồng theo đợt (Ví dụ: 3 luồng song song, mỗi luồng tải 20 chương).
- Xong mỗi đợt 3 luồng sẽ tự động sang đợt tiếp theo cho đến khi hoàn tất toàn bộ truyện.
- Mỗi chapter được lưu thành một file .txt riêng biệt, tên file có số thứ tự zero-padding.
"""

import argparse
import html
import math
import os
import re
import sys
import threading
import time
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Đảm bảo console trên Windows hiển thị được tiếng Việt và Unicode không bị lỗi mã trang cp1252
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_URL = "https://www.webnovel.com/vi/book/20846713406621205/55960120064004058"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
    "Referer": "https://www.webnovel.com/",
    "Origin": "https://www.webnovel.com",
}

# Khóa đồng bộ in ra màn hình để tránh chữ từ nhiều luồng bị đè lên nhau
print_lock = threading.Lock()
stats_lock = threading.Lock()


def sync_print(*args, **kwargs):
    """In đồng bộ an toàn qua các luồng."""
    with print_lock:
        print(*args, **kwargs)


def create_session() -> requests.Session:
    """Tạo requests Session có cấu hình retry và connection pool."""
    session = requests.Session()
    session.headers.update(HEADERS)
    retries = Retry(
        total=5,
        backoff_factor=1.0,
        status_forcelist=[429, 500, 502, 503, 504],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retries, pool_connections=10, pool_maxsize=10)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def get_csrf_token(session: requests.Session) -> str:
    """Lấy hoặc kích hoạt _csrfToken cookie từ Webnovel."""
    csrf = session.cookies.get("_csrfToken")
    if not csrf:
        try:
            session.get("https://www.webnovel.com/stories/novel", timeout=10)
            csrf = session.cookies.get("_csrfToken", "")
        except Exception:
            pass
    return csrf or ""


def sanitize_filename(filename: str, max_length: int = 120) -> str:
    """Làm sạch tên file để tương thích an toàn trên Windows/Linux/macOS."""
    # Thay thế các ký tự cấm trên Windows: \ / : * ? " < > |
    filename = re.sub(r'[\\/*?:"<>|]', '_', filename)
    filename = "".join(ch for ch in filename if ord(ch) >= 32)
    filename = filename.replace('\ufffd', '-')
    filename = filename.strip()
    if len(filename) > max_length:
        filename = filename[:max_length].rstrip()
    filename = filename.rstrip('. ')
    return filename or "untitled"


def clean_paragraph_text(raw_text: str) -> str:
    """Loại bỏ thẻ HTML rác, watermark chống trộm và giải mã ký tự HTML."""
    if not raw_text:
        return ""

    text = re.sub(r'<\/?pirate[^>]*>', '', raw_text, flags=re.IGNORECASE)
    text = re.sub(r'Find authorized novels in Webnovel.*', '', text, flags=re.IGNORECASE)

    soup = BeautifulSoup(text, "html.parser")
    cleaned = soup.get_text()
    cleaned = html.unescape(cleaned)
    cleaned = cleaned.replace('\r\n', '\n').replace('\r', '\n')
    return cleaned.strip()


def parse_novel_url(url: str):
    """
    Trích xuất book_id và chapter_id từ URL webnovel.
    """
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    parts = path.split("/")

    book_id = None
    chapter_id = None

    for i, part in enumerate(parts):
        if part == "book" and i + 1 < len(parts):
            book_part = parts[i + 1]
            match = re.search(r'(\d{10,25})', book_part)
            if match:
                book_id = match.group(1)
            if i + 2 < len(parts):
                chap_part = parts[i + 2]
                chap_match = re.search(r'(\d{10,25})', chap_part)
                if chap_match:
                    chapter_id = chap_match.group(1)
            break

    if not book_id:
        all_numbers = re.findall(r'\b\d{15,25}\b', url)
        if len(all_numbers) >= 1:
            book_id = all_numbers[0]
        if len(all_numbers) >= 2:
            chapter_id = all_numbers[1]

    return book_id, chapter_id


def fetch_catalog(session: requests.Session, book_id: str):
    """
    Tải danh sách toàn bộ các chapter từ trang catalog của truyện.
    Trả về danh sách các dict chứa {index, cid, title, volume}.
    """
    urls_to_try = [
        f"https://www.webnovel.com/book/{book_id}/catalog",
        f"https://www.webnovel.com/vi/book/{book_id}/catalog",
    ]

    for url in urls_to_try:
        try:
            resp = session.get(url, timeout=15)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, "lxml")
                volumes = soup.select(".volume-item")
                chapters = []
                for vol_idx, vol in enumerate(volumes, start=1):
                    vol_title_elem = vol.find("h4")
                    vol_title = vol_title_elem.get_text(strip=True) if vol_title_elem else f"Volume {vol_idx}"
                    for li in vol.select("li"):
                        cid = li.get("data-cid") or li.get("data-report-cid")
                        a_tag = li.find("a")
                        title = a_tag.get("title") if a_tag else ""
                        if not title and a_tag:
                            title = a_tag.get_text(strip=True)
                        if cid:
                            chapters.append({
                                "index": len(chapters) + 1,
                                "cid": str(cid),
                                "title": title.strip() if title else f"Chapter {len(chapters) + 1}",
                                "volume": vol_title,
                            })
                if chapters:
                    return chapters
        except Exception as e:
            sync_print(f"[!] Lỗi khi tải catalog từ {url}: {e}")

    return None


def fetch_chapter_content(session: requests.Session, book_id: str, chapter_id: str, max_retries: int = 3):
    """
    Gọi Webnovel PCM API để lấy thông tin và nội dung của một chapter.
    Tự động retry nếu gặp sự cố mạng hoặc lỗi tạm thời.
    """
    csrf = get_csrf_token(session)
    api_url = (
        f"https://www.webnovel.com/go/pcm/chapter/getContent"
        f"?_csrfToken={csrf}&bookId={book_id}&chapterId={chapter_id}&encryptType=3&_fsae=0"
    )

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            resp = session.get(api_url, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == 0:
                    return data.get("data", {})
                else:
                    msg = data.get("msg") or f"Code {data.get('code')}"
                    raise RuntimeError(f"API báo lỗi: {msg}")
            elif resp.status_code in [429, 500, 502, 503, 504]:
                time.sleep(1.0 * attempt)
                last_error = RuntimeError(f"HTTP {resp.status_code}")
            else:
                raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:100]}")
        except Exception as e:
            last_error = e
            time.sleep(0.8 * attempt)

    raise last_error or RuntimeError("Không thể tải nội dung chapter")


def extract_chapter_text(chapter_data: dict) -> tuple[str, str, str, str]:
    """
    Trích xuất tiêu đề, nội dung plain text, nextChapterId và ghi chú tác giả.
    Trả về: (chapter_name, full_text, next_chapter_id, author_notes)
    """
    ci = chapter_data.get("chapterInfo", {})
    chapter_name = ci.get("chapterName", "").strip()
    next_chapter_id = str(ci.get("nextChapterId") or "").strip()

    paragraphs = []

    if "contents" in ci and isinstance(ci["contents"], list):
        for item in ci["contents"]:
            if isinstance(item, dict) and "content" in item:
                cleaned = clean_paragraph_text(item["content"])
                if cleaned:
                    paragraphs.append(cleaned)
    elif "content" in ci and isinstance(ci["content"], str) and ci["content"]:
        raw_text = ci["content"]
        if "<p>" in raw_text:
            parts = re.split(r'</?p[^>]*>', raw_text)
            for part in parts:
                cleaned = clean_paragraph_text(part)
                if cleaned:
                    paragraphs.append(cleaned)
        else:
            for line in raw_text.splitlines():
                cleaned = clean_paragraph_text(line)
                if cleaned:
                    paragraphs.append(cleaned)

    notes_obj = ci.get("notes")
    author_notes = ""
    if isinstance(notes_obj, dict) and notes_obj.get("note"):
        author_notes = clean_paragraph_text(notes_obj.get("note"))

    text_blocks = []
    if chapter_name:
        underline = "=" * min(max(len(chapter_name), 10), 60)
        text_blocks.append(f"{chapter_name}\n{underline}")

    if paragraphs:
        text_blocks.extend(paragraphs)
    else:
        if ci.get("vipStatus") == 1:
            text_blocks.append("[Chương này có phí / VIP trên Webnovel - không thể đọc tự do]")
        else:
            text_blocks.append("[Nội dung chương trống hoặc không tải được]")

    if author_notes:
        text_blocks.append("\n" + "-" * 30)
        text_blocks.append(f"Ghi chú tác giả:\n{author_notes}")

    full_text = "\n\n".join(text_blocks)
    return chapter_name, full_text, next_chapter_id, author_notes


def worker_task(
    worker_id: int,
    chapter_chunk: list,
    book_id: str,
    output_dir: str,
    pad_width: int,
    total_chapters: int,
    delay: float,
    overwrite: bool,
    stats: dict,
):
    """
    Công việc của 1 luồng: duyệt qua danh sách các chương được phân công (tối đa 20 chương).
    """
    session = create_session()
    # Khởi tạo CSRF cho session riêng của luồng
    get_csrf_token(session)

    for item in chapter_chunk:
        cid = item["cid"]
        ch_index = item.get("index", 1)
        title_hint = item.get("title", f"Chapter {ch_index}")

        clean_title = sanitize_filename(title_hint)
        filename = f"Chapter_{ch_index:0{pad_width}d} - {clean_title}.txt"
        filepath = os.path.join(output_dir, filename)

        # Kiểm tra file đã có chưa
        if not overwrite and os.path.exists(filepath) and os.path.getsize(filepath) > 50:
            sync_print(
                f"[Luồng {worker_id}] [{ch_index:0{pad_width}d}/{total_chapters:0{pad_width}d}] "
                f"Đã có sẵn (Bỏ qua): {filename}"
            )
            with stats_lock:
                stats["skipped"] += 1
            continue

        try:
            ch_data = fetch_chapter_content(session, book_id, cid)
            ch_title, full_text, _, _ = extract_chapter_text(ch_data)

            if ch_title:
                clean_ch_title = sanitize_filename(ch_title)
                filename = f"Chapter_{ch_index:0{pad_width}d} - {clean_ch_title}.txt"
                filepath = os.path.join(output_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(full_text)

            line_count = len(full_text.splitlines())
            sync_print(
                f"[Luồng {worker_id}] [{ch_index:0{pad_width}d}/{total_chapters:0{pad_width}d}] "
                f"Đã lưu: {filename} ({line_count} dòng)"
            )
            with stats_lock:
                stats["downloaded"] += 1

        except Exception as err:
            sync_print(
                f"[Luồng {worker_id}] [{ch_index:0{pad_width}d}/{total_chapters:0{pad_width}d}] "
                f"[X] Thất bại CID {cid}: {err}"
            )
            with stats_lock:
                stats["failed"] += 1

        if delay > 0:
            time.sleep(delay)


def crawl_novel(
    url: str = DEFAULT_URL,
    output_dir: str = None,
    delay: float = 0.3,
    start_index: int = 1,
    limit: int = None,
    overwrite: bool = False,
    num_threads: int = 3,
    chunk_size: int = 20,
    round_delay: float = 1.0,
):
    """
    Hàm chính điều phối cào truyện:
    - Chia toàn bộ chương thành các đợt (round).
    - Mỗi đợt gồm `num_threads` luồng chạy song song (mặc định: 3 luồng).
    - Mỗi luồng tải `chunk_size` chương (mặc định: 20 chương).
    - Đợi cả 3 luồng hoàn thành đợt hiện tại rồi mới tiếp tục chạy đợt tiếp theo.
    """
    main_session = create_session()

    book_id, initial_cid = parse_novel_url(url)
    if not book_id:
        sync_print(f"[X] Lỗi: Không thể trích xuất book_id từ URL: {url}")
        sys.exit(1)

    sync_print("=" * 68)
    sync_print("          WEBNOVEL MULTI-THREAD BATCH CRAWLER         ")
    sync_print("=" * 68)
    sync_print(f"[*] URL mục tiêu       : {url}")
    sync_print(f"[*] Book ID            : {book_id}")
    if initial_cid:
        sync_print(f"[*] Chapter ID đầu     : {initial_cid}")
    sync_print(f"[*] Cấu hình đa luồng  : {num_threads} luồng, mỗi luồng tải {chunk_size} chương/đợt")
    sync_print(f"[*] Tổng tải mỗi đợt   : Tối đa {num_threads * chunk_size} chương")

    # Lấy thông tin sách
    get_csrf_token(main_session)
    test_cid = initial_cid if initial_cid else "0"
    book_title = f"Book_{book_id}"
    author_name = "Unknown"
    total_chapters_meta = 0

    try:
        sample_data = fetch_chapter_content(main_session, book_id, test_cid)
        book_info = sample_data.get("bookInfo", {})
        book_title = book_info.get("bookName", book_title)
        author_name = book_info.get("authorName", author_name)
        total_chapters_meta = book_info.get("totalChapterNum", 0)
    except Exception as e:
        sync_print(f"[!] Không thể lấy trước thông tin sách: {e}")

    sync_print(f"[*] Tên truyện         : {book_title}")
    sync_print(f"[*] Tác giả            : {author_name}")
    sync_print(f"[*] Tổng số chương web : {total_chapters_meta}")

    if not output_dir:
        safe_book_dir = sanitize_filename(book_title)
        output_dir = os.path.join(os.getcwd(), safe_book_dir)

    os.makedirs(output_dir, exist_ok=True)
    sync_print(f"[*] Thư mục lưu file   : {os.path.abspath(output_dir)}")
    sync_print("=" * 68)

    # Tải danh mục chương
    sync_print("[*] Đang tải danh mục chương (Catalog)...")
    catalog_chapters = fetch_catalog(main_session, book_id)

    if not catalog_chapters:
        sync_print("[X] Lỗi: Không thể lấy danh mục chương để phân chia đa luồng.")
        sys.exit(1)

    total_catalog = len(catalog_chapters)
    pad_width = max(3, len(str(total_catalog)))
    sync_print(f"[✓] Đã tìm thấy {total_catalog} chương trong danh mục.")

    # Tìm vị trí bắt đầu
    start_pos = 0
    if initial_cid:
        for idx, ch in enumerate(catalog_chapters):
            if ch["cid"] == initial_cid:
                start_pos = idx
                break
        if start_pos > 0:
            sync_print(f"[*] Bắt đầu tải từ chương ID {initial_cid} (Chương thứ #{start_pos + 1} của truyện).")

    if start_index > 1:
        start_pos = max(start_pos, start_index - 1)

    chapters_to_crawl = catalog_chapters[start_pos:]

    if limit and limit > 0:
        chapters_to_crawl = chapters_to_crawl[:limit]
        sync_print(f"[*] Giới hạn tổng số chương cần tải: {len(chapters_to_crawl)} chương.")

    total_needed = len(chapters_to_crawl)
    if total_needed == 0:
        sync_print("[!] Không có chương nào cần tải.")
        return

    # Phân chia thành các đợt (Round)
    round_capacity = num_threads * chunk_size
    total_rounds = math.ceil(total_needed / round_capacity)

    sync_print(f"[*] Kế hoạch: Chia {total_needed} chương thành {total_rounds} đợt (Round).")
    sync_print("=" * 68)

    stats = {"downloaded": 0, "skipped": 0, "failed": 0}
    start_time = time.time()

    for round_num in range(1, total_rounds + 1):
        round_start_idx = (round_num - 1) * round_capacity
        round_end_idx = min(round_start_idx + round_capacity, total_needed)
        round_chapters = chapters_to_crawl[round_start_idx:round_end_idx]

        first_ch_idx = round_chapters[0]["index"]
        last_ch_idx = round_chapters[-1]["index"]

        sync_print("\n" + "-" * 68)
        sync_print(
            f" [>>>] BẮT ĐẦU ĐỢT {round_num}/{total_rounds}: "
            f"Chương #{first_ch_idx} -> #{last_ch_idx} (Gồm {len(round_chapters)} chương)"
        )
        sync_print("-" * 68)

        # Chia round_chapters cho num_threads luồng
        threads = []
        for t_idx in range(num_threads):
            t_start = t_idx * chunk_size
            t_end = min(t_start + chunk_size, len(round_chapters))
            if t_start >= len(round_chapters):
                break  # Không còn chương cho luồng này trong đợt

            chunk = round_chapters[t_start:t_end]
            w_id = t_idx + 1
            w_first = chunk[0]["index"]
            w_last = chunk[-1]["index"]
            sync_print(f"   -> Luồng {w_id}: Phụ trách {len(chunk)} chương (từ #{w_first} đến #{w_last})")

            t = threading.Thread(
                target=worker_task,
                args=(
                    w_id,
                    chunk,
                    book_id,
                    output_dir,
                    pad_width,
                    total_catalog,
                    delay,
                    overwrite,
                    stats,
                ),
                daemon=True,
            )
            threads.append(t)

        # Khởi chạy tất cả các luồng trong đợt này
        for t in threads:
            t.start()

        # Đợi toàn bộ các luồng trong đợt này kết thúc
        for t in threads:
            t.join()

        sync_print(
            f"[✓] ĐÃ HOÀN TẤT ĐỢT {round_num}/{total_rounds}! "
            f"(Đã tải: {stats['downloaded']}, Đã có: {stats['skipped']}, Lỗi: {stats['failed']})"
        )

        # Nghỉ nhẹ giữa các đợt nếu còn đợt tiếp theo
        if round_num < total_rounds and round_delay > 0:
            time.sleep(round_delay)

    elapsed = time.time() - start_time
    sync_print("\n" + "=" * 68)
    sync_print("                            TẤT CẢ ĐÃ XONG!                         ")
    sync_print("=" * 68)
    sync_print(f"[✓] Tổng tải mới      : {stats['downloaded']} chương")
    sync_print(f"[↷] Bỏ qua (đã có)    : {stats['skipped']} chương")
    if stats["failed"] > 0:
        sync_print(f"[X] Lỗi               : {stats['failed']} chương")
    sync_print(f"[⏱] Tổng thời gian     : {elapsed:.1f} giây")
    sync_print(f"[📁] Thư mục lưu       : {os.path.abspath(output_dir)}")
    sync_print("=" * 68)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Script cào truyện từ Webnovel chạy đa luồng theo đợt:\n"
            "Chạy N luồng song song (mặc định 3 luồng), mỗi luồng cào C chương (mặc định 20 chương).\n"
            "Xong đợt sẽ tiếp tục các đợt tiếp theo đến hết truyện."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "url",
        nargs="?",
        default=DEFAULT_URL,
        help=f"Đường dẫn (URL) truyện hoặc chương truyện cần cào.\nMặc định: {DEFAULT_URL}",
    )
    parser.add_argument(
        "-o", "--output-dir",
        dest="output_dir",
        default=None,
        help="Thư mục lưu các file .txt. Mặc định là tên của truyện.",
    )
    parser.add_argument(
        "-t", "--threads",
        type=int,
        default=3,
        help="Số luồng chạy song song trong mỗi đợt (Mặc định: 3 luồng).",
    )
    parser.add_argument(
        "-c", "--chunk-size",
        dest="chunk_size",
        type=int,
        default=20,
        help="Số chương mỗi luồng xử lý trong 1 đợt (Mặc định: 20 chương/luồng).",
    )
    parser.add_argument(
        "-d", "--delay",
        type=float,
        default=0.25,
        help="Thời gian nghỉ (giây) giữa các request trong mỗi luồng (Mặc định: 0.25s).",
    )
    parser.add_argument(
        "--round-delay",
        type=float,
        default=1.0,
        help="Thời gian nghỉ (giây) giữa các đợt (Mặc định: 1.0s).",
    )
    parser.add_argument(
        "-s", "--start",
        dest="start_index",
        type=int,
        default=1,
        help="Chương bắt đầu tải theo số thứ tự (Mặc định: 1).",
    )
    parser.add_argument(
        "-n", "--limit",
        dest="limit",
        type=int,
        default=None,
        help="Số lượng chương tối đa cần tải (Mặc định: tải tất cả đến hết).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Ghi đè file nếu đã tồn tại.",
    )

    args = parser.parse_args()

    crawl_novel(
        url=args.url,
        output_dir=args.output_dir,
        delay=args.delay,
        start_index=args.start_index,
        limit=args.limit,
        overwrite=args.overwrite,
        num_threads=args.threads,
        chunk_size=args.chunk_size,
        round_delay=args.round_delay,
    )


if __name__ == "__main__":
    main()
