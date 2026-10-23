#!/usr/bin/env python3
"""Sinh index.json ở gốc repo theo index-json-spec.md.

Chạy từ gốc repo: python scripts/build_index.py

- sha lấy từ Git index (`git ls-files -s`). File chưa stage hoặc đã sửa mà
  chưa stage thì lấy bằng `git hash-object` (sha sẽ có sau khi commit nội dung
  hiện tại) và in cảnh báo.
- Nội dung không đổi so với index.json cũ thì giữ nguyên `generatedAt`, nên
  file không đổi và không sinh commit rác.
"""

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRANSLATIONS = "translations"
INDEX_FILE = ROOT / "index.json"
CHAPTER_RE = re.compile(r"^Chapter_(\d+)\.md$")
SCHEMA_VERSION = 1


class DataError(Exception):
    pass


def git(*args, stdin=None):
    result = subprocess.run(
        ["git", *args], cwd=ROOT, input=stdin, capture_output=True
    )
    if result.returncode != 0:
        msg = result.stderr.decode("utf-8", "replace").strip()
        raise DataError(f"git {' '.join(args)} lỗi: {msg}")
    return result.stdout.decode("utf-8")


def staged_shas():
    """path -> sha của các file chương trong Git index."""
    shas = {}
    out = git("ls-files", "-s", "-z", "--", f"{TRANSLATIONS}/*/vi/Chapter_*.md")
    for entry in filter(None, out.split("\0")):
        meta, path = entry.split("\t", 1)
        _mode, sha, stage = meta.split()
        if stage != "0":
            raise DataError(f"{path}: đang conflict (stage {stage})")
        shas[path] = sha
    return shas


def unstaged_paths():
    """Các file chương có thay đổi chưa stage so với Git index."""
    out = git("diff", "--name-only", "-z", "--", f"{TRANSLATIONS}/*/vi/Chapter_*.md")
    return set(filter(None, out.split("\0")))


def hash_objects(paths):
    if not paths:
        return {}
    out = git("hash-object", "--stdin-paths", stdin="\n".join(paths).encode("utf-8"))
    return dict(zip(paths, out.split()))


def read_title(novel_dir, slug):
    novel_json = novel_dir / "novel.json"
    if not novel_json.is_file():
        return slug
    try:
        data = json.loads(novel_json.read_text(encoding="utf-8-sig"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise DataError(f"{novel_json.relative_to(ROOT).as_posix()}: JSON sai định dạng ({e})")
    if not isinstance(data, dict):
        raise DataError(f"{novel_json.relative_to(ROOT).as_posix()}: phải là một object JSON")
    title = data.get("title")
    if title is None:
        return slug
    if not isinstance(title, str):
        raise DataError(f"{novel_json.relative_to(ROOT).as_posix()}: `title` phải là chuỗi")
    return title.strip() or slug


def read_chapter_title(path):
    try:
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as e:
        raise DataError(f"{path.relative_to(ROOT).as_posix()}: không phải UTF-8 ({e})")
    for line in text.splitlines():
        if line.strip():
            return line[2:].strip() if line.startswith("# ") else ""
    return ""


def collect_chapters(novel_dir):
    vi_dir = novel_dir / "vi"
    if not vi_dir.is_dir():
        return []
    by_number = {}
    for f in sorted(vi_dir.iterdir()):
        m = CHAPTER_RE.match(f.name)
        if not m or not f.is_file():
            continue
        number = int(m.group(1))
        rel = f.relative_to(ROOT).as_posix()
        if number in by_number:
            raise DataError(f"trùng chương {number}: {by_number[number]['path']} và {rel}")
        by_number[number] = {
            "number": number,
            "title": read_chapter_title(f),
            "path": rel,
        }
    return [by_number[n] for n in sorted(by_number)]


def build_novels():
    base = ROOT / TRANSLATIONS
    if not base.is_dir():
        return []
    novels = []
    for d in sorted((p for p in base.iterdir() if p.is_dir()), key=lambda p: p.name):
        novels.append({
            "slug": d.name,
            "title": read_title(d, d.name),
            "chapters": collect_chapters(d),
        })
    return novels


def fill_shas(novels):
    staged = staged_shas()
    dirty = unstaged_paths()
    chapters = [c for n in novels for c in n["chapters"]]
    fallback = [c["path"] for c in chapters if c["path"] not in staged or c["path"] in dirty]
    computed = hash_objects(fallback)
    for path in fallback:
        state = "chưa git add" if path not in staged else "có thay đổi chưa stage"
        print(f"[cảnh báo] {path}: {state}, sha tính theo nội dung hiện tại", file=sys.stderr)
    for c in chapters:
        c["sha"] = computed.get(c["path"]) or staged[c["path"]]


def load_old():
    if not INDEX_FILE.is_file():
        return None
    try:
        return json.loads(INDEX_FILE.read_text(encoding="utf-8-sig"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def utf8_stdout():
    # Console Windows mặc định cp1252, in tiếng Việt sẽ lỗi.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except AttributeError:
            pass


def main():
    utf8_stdout()
    try:
        novels = build_novels()
        fill_shas(novels)
    except DataError as e:
        print(f"[LỖI] {e}", file=sys.stderr)
        return 1

    old = load_old()
    unchanged = (
        isinstance(old, dict)
        and old.get("schemaVersion") == SCHEMA_VERSION
        and old.get("novels") == novels
        and isinstance(old.get("generatedAt"), str)
    )
    if unchanged:
        generated_at = old["generatedAt"]
    else:
        generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    index = {
        "schemaVersion": SCHEMA_VERSION,
        "generatedAt": generated_at,
        "novels": novels,
    }
    text = json.dumps(index, ensure_ascii=False, indent=2) + "\n"
    with open(INDEX_FILE, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)

    total = sum(len(n["chapters"]) for n in novels)
    status = "không đổi" if unchanged else "đã cập nhật"
    print(f"index.json {status}: {len(novels)} truyện, {total} chương")
    return 0


if __name__ == "__main__":
    sys.exit(main())
