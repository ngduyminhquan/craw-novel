#!/usr/bin/env python3
"""Script tải raw truyện Legend (Kakuyomu).

Mặc định tải Legend 1 (work_id: 16816452219415512391, 3000 chương) vào thư mục `Legend/`.
Hỗ trợ chạy tiếp (resume) nếu bị ngắt giữa chừng, tải đa luồng và chọn khoảng chương.

Cách dùng:
    python scripts/crawl_legend.py
    python scripts/crawl_legend.py --start 1 --end 100
    python scripts/crawl_legend.py --workers 10 --out "Legend"
"""

import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_WORK_ID = "16816452219415512391"
DEFAULT_OUT_DIR = ROOT / "Legend"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

NEXT_DATA_RE = re.compile(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', re.S)
BODY_RE = re.compile(r'<div class="widget-episodeBody[^"]*"[^>]*>(.*?)</div>', re.S)
P_RE = re.compile(r"<p[^>]*>(.*?)</p>", re.S)
RUBY_RE = re.compile(
    r"<ruby>\s*(?:<rb>)?(.*?)(?:</rb>)?\s*(?:<rp>.*?</rp>)?\s*<rt>(.*?)</rt>\s*(?:<rp>.*?</rp>)?\s*</ruby>",
    re.S,
)
TAG_RE = re.compile(r"<[^>]+>")
INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def utf8_stdout():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except AttributeError:
            pass


def fetch_html(url: str, retries: int = 4, timeout: int = 20) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            if attempt == retries:
                raise RuntimeError(f"Không thể tải {url} sau {retries} lần thử: {e}") from e
            time.sleep(1.5 * attempt)
    raise RuntimeError(f"Không thể tải {url}")


def sanitize_filename(name: str) -> str:
    cleaned = INVALID_FILENAME_CHARS.sub("_", name).strip()
    return re.sub(r"\s+", " ", cleaned)


def fetch_toc(work_id: str) -> list[dict]:
    """Lấy danh sách toàn bộ chương từ trang mục lục Kakuyomu."""
    url = f"https://kakuyomu.jp/works/{work_id}"
    page = fetch_html(url)
    m = NEXT_DATA_RE.search(page)
    if not m:
        raise RuntimeError("Không tìm thấy __NEXT_DATA__ trên trang Kakuyomu.")

    data = json.loads(m.group(1))
    state = data["props"]["pageProps"]["__APOLLO_STATE__"]
    work_key = f"Work:{work_id}"
    if work_key not in state:
        raise RuntimeError(f"Không tìm thấy dữ liệu {work_key} trong state.")

    work = state[work_key]
    toc_refs = work.get("tableOfContentsV2") or work.get("tableOfContents") or []

    episodes = []
    idx = 1
    for toc_ref in toc_refs:
        toc_obj = state.get(toc_ref["__ref"], {})
        chapter_ref = toc_obj.get("chapter")
        arc_title = ""
        if chapter_ref and chapter_ref.get("__ref") in state:
            arc_title = state[chapter_ref["__ref"]].get("title", "").strip()

        for ep_ref in toc_obj.get("episodeUnions", []):
            ep_obj = state.get(ep_ref["__ref"], {})
            ep_id = ep_obj.get("id")
            ep_title = ep_obj.get("title", f"第{idx}話").strip()
            full_title = f"{arc_title} - {ep_title}" if arc_title else ep_title
            episodes.append({
                "index": idx,
                "id": ep_id,
                "ep_title": ep_title,
                "arc_title": arc_title,
                "full_title": full_title,
                "url": f"https://kakuyomu.jp/works/{work_id}/episodes/{ep_id}",
            })
            idx += 1

    return episodes


def html_to_paragraphs(body_html: str) -> list[str]:
    """Chuyển HTML nội dung chương của Kakuyomu sang danh sách dòng văn bản."""
    lines = []
    for p_match in P_RE.finditer(body_html):
        p_full = p_match.group(0)
        p_inner = p_match.group(1)
        if 'class="blank"' in p_full:
            lines.append("")
            continue
        # Chuyển <ruby><rb>漢字</rb><rt>かんじ</rt></ruby> -> 漢字(かんじ)
        text = RUBY_RE.sub(r"\1(\2)", p_inner)
        text = text.replace("<br />", "\n").replace("<br>", "\n")
        text = TAG_RE.sub("", text)
        text = html.unescape(text)
        # Bỏ khoảng trắng đầu dòng kiểu Nhật (　) hoặc giữ nguyên nội dung sạch
        lines.append(text.rstrip())
    return lines


def download_episode(ep: dict, out_dir: Path, pad_width: int, overwrite: bool = False) -> str:
    safe_title = sanitize_filename(ep["full_title"])
    filename = f"Chapter_{ep['index']:0{pad_width}d} - {safe_title}.txt"
    filepath = out_dir / filename

    if filepath.exists() and filepath.stat().st_size > 0 and not overwrite:
        return "skipped"

    page = fetch_html(ep["url"])
    m = BODY_RE.search(page)
    if not m:
        raise RuntimeError(f"Không tìm thấy nội dung chương trong {ep['url']}")

    paragraphs = html_to_paragraphs(m.group(1))
    content = f"{ep['full_title']}\n\n" + "\n".join(paragraphs).strip() + "\n"
    filepath.write_text(content, encoding="utf-8")
    return "downloaded"


def main():
    utf8_stdout()
    parser = argparse.ArgumentParser(description="Tải raw truyện từ Kakuyomu")
    parser.add_argument("--work-id", default=DEFAULT_WORK_ID, help="Kakuyomu Work ID (mặc định: Legend 1)")
    parser.add_argument("--out", default=str(DEFAULT_OUT_DIR), help="Thư mục lưu file raw")
    parser.add_argument("--start", type=int, default=1, help="Chương bắt đầu (mặc định: 1)")
    parser.add_argument("--end", type=int, default=0, help="Chương kết thúc (mặc định: 0 = hết)")
    parser.add_argument("--workers", type=int, default=16, help="Số luồng tải song song (mặc định: 16)")
    parser.add_argument("--delay", type=float, default=0.0, help="Độ trễ nhỏ giữa các request (giây)")
    parser.add_argument("--overwrite", action="store_true", help="Ghi đè các chương đã tải")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Đang lấy mục lục từ https://kakuyomu.jp/works/{args.work_id} ...", flush=True)
    episodes = fetch_toc(args.work_id)
    total_eps = len(episodes)
    print(f"Tìm thấy tổng cộng {total_eps} chương.", flush=True)

    pad_width = max(3, len(str(total_eps)))
    start_idx = max(1, args.start)
    end_idx = args.end if args.end > 0 else total_eps
    target_eps = [ep for ep in episodes if start_idx <= ep["index"] <= end_idx]

    print(
        f"Chuẩn bị tải {len(target_eps)} chương (từ #{start_idx} đến #{end_idx}) "
        f"vào '{out_dir}' với {args.workers} luồng...",
        flush=True,
    )

    downloaded = 0
    skipped = 0
    failed = []
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(download_episode, ep, out_dir, pad_width, args.overwrite): ep
            for ep in target_eps
        }

        done_count = 0
        for fut in as_completed(futures):
            ep = futures[fut]
            done_count += 1
            try:
                status = fut.result()
                if status == "downloaded":
                    downloaded += 1
                else:
                    skipped += 1
                if done_count % 50 == 0 or done_count == len(target_eps):
                    elapsed = time.time() - start_time
                    print(
                        f"[{done_count}/{len(target_eps)}] "
                        f"Đã tải: {downloaded} | Bỏ qua (đã có): {skipped} | Lỗi: {len(failed)} "
                        f"({elapsed:.1f}s)",
                        flush=True,
                    )
            except Exception as e:
                failed.append((ep["index"], str(e)))
                print(f"[LỖI] Chương #{ep['index']} ({ep['full_title']}): {e}", file=sys.stderr, flush=True)

    print("\n--- Hoàn tất ---")
    print(f"Tổng số xử lý : {len(target_eps)}")
    print(f"Tải mới       : {downloaded}")
    print(f"Đã có sẵn     : {skipped}")
    print(f"Lỗi           : {len(failed)}")
    if failed:
        for idx, err in failed[:10]:
            print(f"  - Chương #{idx}: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
