"""Khởi tạo thư mục dịch cho một truyện: novel.json, progress.md, context/*, vi/.

    python .agents/skills/novel-translate/scripts/init_novel.py --raw "<thư mục raw>" --slug <slug> --title "<tên truyện>"

Chạy lại an toàn: không ghi đè file context đã có; progress.md chỉ được thêm các chương mới.
"""
import argparse
import json
import re
import shutil
from pathlib import Path

from common import (PROGRESS_HEADER, RAW_NAME_RE, ROOT, STORY_NO_RE, TRANSLATIONS,
                    die, load_progress, read_text, utf8_stdout)

TEMPLATES = Path(__file__).resolve().parents[1] / "templates"
CONTEXT_FILES = ["rules.md", "style.md", "characters.md", "pronouns.md", "glossary.md", "summaries.md"]


def norm_title(title):
    t = STORY_NO_RE.sub("", title)
    t = re.sub(r"[–—\-_:!?.,()'’\"]", " ", t.lower())
    return re.sub(r"\s+", " ", t).strip()


def scan_raw(raw_dir):
    chapters = []
    for p in sorted(raw_dir.glob("*.txt")):
        m = RAW_NAME_RE.match(p.name)
        if not m:
            print(f"  bỏ qua file không đúng mẫu tên: {p.name}")
            continue
        story = STORY_NO_RE.match(m.group(2))
        chapters.append({
            "idx": int(m.group(1)),
            "story": story.group(1) if story else "",
            "file": p.name,
            # bỏ ký tự định dạng ẩn (soft hyphen U+00AD, zero-width...) lẫn trong tên file raw
            "title": re.sub(r"[­​-‏﻿]", "", STORY_NO_RE.sub("", m.group(2))).strip().replace("|", "/"),
            "norm": norm_title(m.group(2)),
        })
    chapters.sort(key=lambda c: c["idx"])
    return chapters


def mark_duplicates(chapters):
    seen = {}
    for c in chapters:
        c["status"], c["note"] = "todo", ""
        first = seen.get(c["norm"])
        if first is not None:
            c["status"] = "skip"
            c["note"] = f"trùng nội dung #{first} (bản dịch EN khác) — kiểm tra lại trước khi bỏ"
        else:
            seen[c["norm"]] = c["idx"]


def write_progress(path, title, chapters):
    lines = [
        f"# Tiến độ — {title}",
        "",
        "Trạng thái: `todo` chưa dịch · `done` đã dịch, qua QA, đã cập nhật context · `reviewed` đã review và sửa · `skip` bỏ qua (trùng, không cần dịch).",
        "Cột `#` là số thứ tự file raw, cũng là số chương dùng trong bản dịch. `Chương truyện` là số chương ghi trong tên file raw (nếu có).",
        "",
        PROGRESS_HEADER,
        "|---|---|---|---|---|---|",
    ]
    for c in chapters:
        lines.append(f"| {c['idx']} | {c['story']} | {c['file']} | {c['title']} | {c['status']} | {c['note']} |")
    lines += [
        "",
        "## Cần user xác nhận",
        "",
        "<!-- Agent ghi vào đây các mâu thuẫn thuật ngữ/xưng hô/quyết định chưa chắc. Mỗi dòng: - [#chương] vấn đề — đề xuất -->",
        "",
        "## Đã quyết",
        "",
        "<!-- Mục đã giải quyết chuyển xuống đây. Mỗi dòng: - [#chương] vấn đề → quyết định (người quyết) -->",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True, help="thư mục chứa Chapter_XXX - <title>.txt")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--title", required=True)
    args = ap.parse_args()

    raw_dir = Path(args.raw)
    if not raw_dir.is_absolute():
        raw_dir = (ROOT / raw_dir).resolve()
    if not raw_dir.is_dir():
        die(f"không thấy thư mục raw: {raw_dir}")

    d = TRANSLATIONS / args.slug
    (d / "context").mkdir(parents=True, exist_ok=True)
    (d / "vi").mkdir(exist_ok=True)

    cfg_path = d / "novel.json"
    if not cfg_path.exists():
        cfg = {"title": args.title, "slug": args.slug, "raw_dir": raw_dir.relative_to(ROOT).as_posix()}
        cfg_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for name in CONTEXT_FILES:
        target = d / "context" / name
        if not target.exists():
            text = read_text(TEMPLATES / name).replace("{title}", args.title)
            target.write_text(text, encoding="utf-8")
            print(f"  tạo context/{name}")

    chapters = scan_raw(raw_dir)
    mark_duplicates(chapters)
    progress = d / "progress.md"
    if progress.exists():
        novel = {"dir": d}
        known = {r["idx"] for r in load_progress(novel)}
        new = [c for c in chapters if c["idx"] not in known]
        if new:
            text = read_text(progress).splitlines()
            last_row = max(i for i, l in enumerate(text) if l.strip().startswith("|"))
            text[last_row + 1:last_row + 1] = [
                f"| {c['idx']} | {c['story']} | {c['file']} | {c['title']} | {c['status']} | {c['note']} |" for c in new
            ]
            progress.write_text("\n".join(text) + "\n", encoding="utf-8")
        print(f"progress.md đã có, thêm {len(new)} chương mới.")
    else:
        write_progress(progress, args.title, chapters)
        print(f"tạo progress.md với {len(chapters)} chương.")

    dups = [c for c in chapters if c["status"] == "skip"]
    for c in dups:
        print(f"  nghi trùng: #{c['idx']} {c['file']} — {c['note']}")
    print(f"Xong: {d.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
