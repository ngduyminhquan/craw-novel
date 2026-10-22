#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script cào truyện từ Novellunar (https://novellunar.com)
Hỗ trợ:
- Chạy 3 luồng song song, mỗi luồng cào 20 chương cho mỗi đợt.
- Tự động tiếp tục các đợt tiếp theo cho đến hết toàn bộ truyện.
- Mặc định cào tiếp từ chương 290 vào thư mục 'Everyone Else Is A Returnee' đã có từ trước.
- Mỗi chapter lưu thành một file .txt riêng biệt, tên file chuẩn UTF-8 có số thứ tự.
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

# Đảm bảo console trên Windows hiển thị tiếng Việt và Unicode không bị lỗi cp1252
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_URL = "https://novellunar.com/novel/everyone-else-is-a-returnee"
DEFAULT_START_CHAPTER = 290

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
    "Origin": "https://novellunar.com",
    "Referer": "https://novellunar.com/",
}

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


def sanitize_filename(filename: str, max_length: int = 120) -> str:
    """Làm sạch tên file để tương thích an toàn trên Windows."""
    filename = filename.replace('\ufffd', '-')
    filename = re.sub(r'[\\/*?:"<>|]', '_', filename)
    filename = "".join(ch for ch in filename if ord(ch) >= 32)
    filename = filename.strip()
    if len(filename) > max_length:
        filename = filename[:max_length].rstrip()
    filename = filename.rstrip('. ')
    return filename or "untitled"


def clean_story_content(raw_html: str) -> list[str]:
    """Phân tích HTML nội dung chapter của Novellunar thành danh sách các đoạn text sạch."""
    if not raw_html:
        return []

    # Sửa lỗi ký tự \ufffd do lỗi encoding trên web gốc (thường là dấu trích dẫn "...")
    cleaned_html = raw_html.replace('\ufffd', '"')

    soup = BeautifulSoup(cleaned_html, "html.parser")
    paragraphs = []

    p_tags = soup.find_all("p")
    if p_tags:
        for p in p_tags:
            t = p.get_text().strip()
            t = html.unescape(t)
            t = t.replace('\r\n', '\n').replace('\r', '\n')
            if t:
                paragraphs.append(t)
    else:
        for line in soup.get_text().splitlines():
            t = line.strip()
            t = html.unescape(t)
            if t:
                paragraphs.append(t)

    return paragraphs


def parse_novellunar_url(url: str):
    """
    Trích xuất novel_slug và chapter_number (nếu có) từ URL novellunar.
    Ví dụ:
      - https://novellunar.com/novel/everyone-else-is-a-returnee -> ('everyone-else-is-a-returnee', None)
      - https://novellunar.com/novel/everyone-else-is-a-returnee/chapter/282 -> ('everyone-else-is-a-returnee', 282)
    """
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    parts = path.split("/")

    slug = "everyone-else-is-a-returnee"
    chap_num = None

    for i, p in enumerate(parts):
        if p == "novel" and i + 1 < len(parts):
            slug = parts[i + 1]
        if p in ["chapter", "chapters"] and i + 1 < len(parts):
            num_match = re.search(r'\d+', parts[i + 1])
            if num_match:
                chap_num = int(num_match.group(0))

    return slug, chap_num


def fetch_all_chapters(session: requests.Session, novel_slug: str):
    """
    Lấy danh sách tất cả các chapter của truyện từ backend API của Novellunar.
    """
    api_url = f"https://novelarrow.com/api-web/novels/{novel_slug}/chapters"
    resp = session.get(api_url, timeout=15)
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code} khi tải danh sách chapter từ {api_url}")

    data = resp.json()
    items = data.get("items", [])
    chapters = []
    for idx, item in enumerate(items, start=1):
        cid = item.get("chapter_id", f"chapter-{idx}")
        # Trích xuất số thứ tự từ chapter_id (ví dụ: chapter-290 -> 290)
        num_match = re.search(r'\d+', cid)
        c_num = int(num_match.group(0)) if num_match else idx
        c_name = item.get("chapter_name", f"Chapter {c_num}")
        chapters.append({
            "number": c_num,
            "cid": cid,
            "title": c_name.strip(),
        })

    return chapters


def fetch_chapter_content(session: requests.Session, novel_slug: str, chapter_id: str, max_retries: int = 3):
    """
    Tải nội dung chapter từ backend API của Novellunar.
    """
    api_url = f"https://novelarrow.com/api-web/novels/{novel_slug}/chapters/{chapter_id}"

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            resp = session.get(api_url, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                ci = data.get("item", {}).get("chapterInfo", {})
                ch_name = ci.get("chapter_name", "").strip()
                raw_html = ci.get("chapter_content", "")
                return ch_name, raw_html
            elif resp.status_code in [429, 500, 502, 503, 504]:
                time.sleep(1.0 * attempt)
                last_error = RuntimeError(f"HTTP {resp.status_code}")
            else:
                raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:100]}")
        except Exception as e:
            last_error = e
            time.sleep(0.8 * attempt)

    raise last_error or RuntimeError(f"Không thể tải nội dung chapter {chapter_id}")


def worker_task(
    worker_id: int,
    chapter_chunk: list,
    novel_slug: str,
    output_dir: str,
    pad_width: int,
    total_catalog_count: int,
    delay: float,
    overwrite: bool,
    stats: dict,
):
    """
    Công việc của 1 luồng: duyệt qua danh sách các chương được phân công (tối đa 20 chương).
    """
    session = create_session()

    for item in chapter_chunk:
        c_num = item["number"]
        cid = item["cid"]
        title_hint = item["title"]

        # Định dạng tên file: Chapter_290 - Ten_Chuong.txt
        clean_title = sanitize_filename(title_hint)
        filename = f"Chapter_{c_num:0{pad_width}d} - {clean_title}.txt"
        filepath = os.path.join(output_dir, filename)

        # Kiểm tra nếu file đã có sẵn
        if not overwrite and os.path.exists(filepath) and os.path.getsize(filepath) > 50:
            sync_print(
                f"[Luồng {worker_id}] [{c_num:0{pad_width}d}/{total_catalog_count:0{pad_width}d}] "
                f"Đã có sẵn (Bỏ qua): {filename}"
            )
            with stats_lock:
                stats["skipped"] += 1
            continue

        try:
            ch_name, raw_html = fetch_chapter_content(session, novel_slug, cid)
            paragraphs = clean_story_content(raw_html)

            # Cập nhật tên file nếu lấy được tiêu đề từ API
            display_title = ch_name if ch_name else title_hint
            clean_display_title = sanitize_filename(display_title)
            filename = f"Chapter_{c_num:0{pad_width}d} - {clean_display_title}.txt"
            filepath = os.path.join(output_dir, filename)

            # Ghép nội dung
            text_blocks = []
            underline = "=" * min(max(len(display_title), 10), 60)
            text_blocks.append(f"{display_title}\n{underline}")
            if paragraphs:
                text_blocks.extend(paragraphs)
            else:
                text_blocks.append("[Nội dung chương trống hoặc không tải được]")

            full_text = "\n\n".join(text_blocks)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(full_text)

            line_count = len(full_text.splitlines())
            sync_print(
                f"[Luồng {worker_id}] [{c_num:0{pad_width}d}/{total_catalog_count:0{pad_width}d}] "
                f"Đã lưu: {filename} ({line_count} dòng)"
            )
            with stats_lock:
                stats["downloaded"] += 1

        except Exception as err:
            sync_print(
                f"[Luồng {worker_id}] [{c_num:0{pad_width}d}/{total_catalog_count:0{pad_width}d}] "
                f"[X] Thất bại CID {cid}: {err}"
            )
            with stats_lock:
                stats["failed"] += 1

        if delay > 0:
            time.sleep(delay)


def crawl_novellunar(
    url: str = DEFAULT_URL,
    start_chapter: int = DEFAULT_START_CHAPTER,
    output_dir: str = None,
    delay: float = 0.25,
    limit: int = None,
    overwrite: bool = False,
    num_threads: int = 3,
    chunk_size: int = 20,
    round_delay: float = 1.0,
):
    """
    Hàm chính điều phối cào truyện từ Novellunar:
    - Chạy 3 luồng song song, mỗi luồng tải 20 chương cho mỗi đợt.
    - Xong đợt 3 luồng sẽ tự động sang đợt tiếp theo cho đến khi hoàn tất.
    """
    main_session = create_session()

    novel_slug, url_chap = parse_novellunar_url(url)
    if url_chap is not None and start_chapter == DEFAULT_START_CHAPTER:
        start_chapter = url_chap

    sync_print("=" * 68)
    sync_print("          NOVELLUNAR MULTI-THREAD BATCH CRAWLER         ")
    sync_print("=" * 68)
    sync_print(f"[*] URL mục tiêu       : {url}")
    sync_print(f"[*] Novel Slug         : {novel_slug}")
    sync_print(f"[*] Bắt đầu từ chương  : {start_chapter}")
    sync_print(f"[*] Cấu hình đa luồng  : {num_threads} luồng, mỗi luồng tải {chunk_size} chương/đợt")
    sync_print(f"[*] Tổng tải mỗi đợt   : Tối đa {num_threads * chunk_size} chương")

    # Mặc định lưu vào thư mục 'Everyone Else Is A Returnee' để tiếp nối các chương trước
    if not output_dir:
        folder_name = "Everyone Else Is A Returnee"
        output_dir = os.path.join(os.getcwd(), folder_name)

    os.makedirs(output_dir, exist_ok=True)
    sync_print(f"[*] Thư mục lưu file   : {os.path.abspath(output_dir)}")
    sync_print("=" * 68)

    # Tải danh sách toàn bộ các chương
    sync_print("[*] Đang tải danh sách chương từ Novellunar...")
    try:
        all_chapters = fetch_all_chapters(main_session, novel_slug)
    except Exception as e:
        sync_print(f"[X] Lỗi: Không thể lấy danh sách chương: {e}")
        sys.exit(1)

    total_chapters_count = len(all_chapters)
    pad_width = max(3, len(str(total_chapters_count)))
    sync_print(f"[✓] Đã tìm thấy {total_chapters_count} chương trên Novellunar.")

    # Lọc các chương từ start_chapter trở đi
    chapters_to_crawl = [c for c in all_chapters if c["number"] >= start_chapter]

    if not chapters_to_crawl:
        sync_print(f"[!] Không tìm thấy chương nào từ #{start_chapter} trở đi.")
        return

    if limit and limit > 0:
        chapters_to_crawl = chapters_to_crawl[:limit]
        sync_print(f"[*] Giới hạn tải: {len(chapters_to_crawl)} chương.")

    total_needed = len(chapters_to_crawl)
    round_capacity = num_threads * chunk_size
    total_rounds = math.ceil(total_needed / round_capacity)

    first_num = chapters_to_crawl[0]["number"]
    last_num = chapters_to_crawl[-1]["number"]
    sync_print(f"[*] Cần tải tổng cộng  : {total_needed} chương (Từ #{first_num} đến #{last_num})")
    sync_print(f"[*] Kế hoạch           : Chia thành {total_rounds} đợt (Round)")
    sync_print("=" * 68)

    stats = {"downloaded": 0, "skipped": 0, "failed": 0}
    start_time = time.time()

    for round_num in range(1, total_rounds + 1):
        round_start_idx = (round_num - 1) * round_capacity
        round_end_idx = min(round_start_idx + round_capacity, total_needed)
        round_chapters = chapters_to_crawl[round_start_idx:round_end_idx]

        r_first = round_chapters[0]["number"]
        r_last = round_chapters[-1]["number"]

        sync_print("\n" + "-" * 68)
        sync_print(
            f" [>>>] BẮT ĐẦU ĐỢT {round_num}/{total_rounds}: "
            f"Chương #{r_first} -> #{r_last} (Gồm {len(round_chapters)} chương)"
        )
        sync_print("-" * 68)

        # Chia cho num_threads luồng
        threads = []
        for t_idx in range(num_threads):
            t_start = t_idx * chunk_size
            t_end = min(t_start + chunk_size, len(round_chapters))
            if t_start >= len(round_chapters):
                break

            chunk = round_chapters[t_start:t_end]
            w_id = t_idx + 1
            w_first = chunk[0]["number"]
            w_last = chunk[-1]["number"]
            sync_print(f"   -> Luồng {w_id}: Phụ trách {len(chunk)} chương (từ #{w_first} đến #{w_last})")

            t = threading.Thread(
                target=worker_task,
                args=(
                    w_id,
                    chunk,
                    novel_slug,
                    output_dir,
                    pad_width,
                    total_chapters_count,
                    delay,
                    overwrite,
                    stats,
                ),
                daemon=True,
            )
            threads.append(t)

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        sync_print(
            f"[✓] ĐÃ HOÀN TẤT ĐỢT {round_num}/{total_rounds}! "
            f"(Đã tải: {stats['downloaded']}, Đã có: {stats['skipped']}, Lỗi: {stats['failed']})"
        )

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
            "Script cào truyện từ Novellunar (https://novellunar.com):\n"
            "Chạy 3 luồng song song, mỗi luồng tải 20 chương cho mỗi đợt.\n"
            "Mặc định cào tiếp từ chương 290 đến hết truyện."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "url",
        nargs="?",
        default=DEFAULT_URL,
        help=f"Đường dẫn (URL) truyện trên Novellunar.\nMặc định: {DEFAULT_URL}",
    )
    parser.add_argument(
        "-s", "--start",
        dest="start_chapter",
        type=int,
        default=DEFAULT_START_CHAPTER,
        help=f"Chương bắt đầu cào (Mặc định: {DEFAULT_START_CHAPTER}).",
    )
    parser.add_argument(
        "-o", "--output-dir",
        dest="output_dir",
        default=None,
        help="Thư mục lưu các file .txt. Mặc định là 'Everyone Else Is A Returnee'.",
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
        "-n", "--limit",
        dest="limit",
        type=int,
        default=None,
        help="Số lượng chương tối đa cần tải (Mặc định: tải đến hết truyện).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Ghi đè file nếu đã tồn tại.",
    )

    args = parser.parse_args()

    crawl_novellunar(
        url=args.url,
        start_chapter=args.start_chapter,
        output_dir=args.output_dir,
        delay=args.delay,
        limit=args.limit,
        overwrite=args.overwrite,
        num_threads=args.threads,
        chunk_size=args.chunk_size,
        round_delay=args.round_delay,
    )


if __name__ == "__main__":
    main()
