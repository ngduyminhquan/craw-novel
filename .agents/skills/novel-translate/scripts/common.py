"""Hàm dùng chung cho các script của skill novel-translate (chỉ dùng thư viện chuẩn)."""
import json
import re
from functools import lru_cache
import sys
from pathlib import Path

# scripts -> novel-translate -> skills -> .agents -> repo root
ROOT = Path(__file__).resolve().parents[4]
TRANSLATIONS = ROOT / "translations"

RAW_NAME_RE = re.compile(r"^Chapter_(\d+)\s*-\s*(.+)\.txt$")
STORY_NO_RE = re.compile(r"^Chapter\s+(\d+)_?\s*", re.IGNORECASE)
TN_RE = re.compile(r"\b(T/N|E/N|P/R|TL\s*note|Translator[’']?s?\s*note|TL:|Editor[’']?s?\s*note|ED:|PR:"
                   r"|Translation\s+changes?\s*:)", re.IGNORECASE)
# Từ viết tắt trần (TL, ED, PR) chỉ là ghi chú khi có dấu ':' ngay sau, để "[Probably.]" hay "[Ed is here]"
# không bị coi là ghi chú. Dạng có "/" (T/N, E/N, P/R) đủ đặc trưng nên không cần ':'.
_NOTE_LONG = r"(?:(?:TL|Translator[’']?s?|Editor[’']?s?|Author[’']?s?)\s*note|Translation\s+changes?)"
_NOTE_KW = rf"(?:(?:T/N|E/N|P/R)\b\s*:?|(?:TL|ED|PR)\s*:|{_NOTE_LONG}\b\s*:?)"
# Ghi chú kẹp trong câu: "I can fly!" (T/N: Said in English)
# Cho phép một tầng ngoặc lồng bên trong: "(T/N: Holy Knight -> Paladin. (Kang HaJin's job))"
INLINE_NOTE_RE = re.compile(
    rf"\s*(?:\(\s*{_NOTE_KW}(?:[^()]|\([^()]*\))*\)|\[\s*{_NOTE_KW}(?:[^\[\]]|\[[^\[\]]*\])*\])",
    re.IGNORECASE)
# Dòng chỉ có tiêu đề ghi chú ("Editors Note.") — từ đây đến hết file là lời nhắn của translator/editor
NOTE_HEADER_RE = re.compile(rf"^(?:T/N|E/N|{_NOTE_LONG})\s*[:.]?\s*$", re.IGNORECASE)
SEPARATOR_RE = re.compile(r"^[=\-_*~]{3,}$")

STATUSES = ("todo", "done", "reviewed", "skip")
TRANSLATED = ("done", "reviewed")  # đã có bản dịch


def utf8_stdout():
    # Console Windows mặc định không phải UTF-8, in tiếng Việt sẽ lỗi.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except AttributeError:
            pass


def die(msg):
    print(f"LỖI: {msg}", file=sys.stderr)
    sys.exit(1)


def read_text(path):
    return Path(path).read_text(encoding="utf-8-sig", errors="replace")


# ---------- Truyện ----------

def novel_dir(slug):
    d = TRANSLATIONS / slug
    if not (d / "novel.json").exists():
        die(f"chưa khởi tạo truyện '{slug}' (không thấy {d / 'novel.json'}). Chạy init_novel.py trước.")
    return d


def load_novel(slug):
    d = novel_dir(slug)
    cfg = json.loads(read_text(d / "novel.json"))
    cfg["dir"] = d
    cfg["raw_path"] = ROOT / cfg["raw_dir"]
    cfg["vi_path"] = d / "vi"
    cfg["context"] = d / "context"
    return cfg


def vi_file(novel, idx):
    return novel["vi_path"] / f"Chapter_{idx:03d}.md"


# ---------- Bảng markdown ----------

def _cells(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def parse_tables(path):
    """Trả về list các bảng; mỗi bảng là list dict {tên cột viết thường: giá trị}."""
    path = Path(path)
    if not path.exists():
        return []
    tables, header, rows = [], None, []
    lines = read_text(path).splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        is_row = line.startswith("|")
        if header is None:
            if is_row and i + 1 < len(lines) and re.match(r"^\|?\s*:?-{2,}", lines[i + 1].strip()):
                header = [h.lower() for h in _cells(line)]
                rows = []
                i += 2
                continue
        elif is_row:
            cells = _cells(line)
            cells += [""] * (len(header) - len(cells))
            rows.append(dict(zip(header, cells)))
        else:
            tables.append(rows)
            header = None
            continue
        i += 1
    if header is not None:
        tables.append(rows)
    return tables


def table_with(path, column):
    """Gộp mọi bảng trong file có cột `column`."""
    out = []
    for t in parse_tables(path):
        if t and column in t[0]:
            out.extend(r for r in t if any(v for v in r.values()))
    return out


def split_aliases(value):
    return [a.strip() for a in re.split(r"[;,]", value or "") if a.strip()]


def is_placeholder(value):
    v = (value or "").strip()
    return not v or v in {"-", "?", "…", "..."} or v.startswith("<")


def entries(path):
    """Các dòng trong bảng có cột EN (glossary, characters): [{en, aliases, vi, row}]."""
    out = []
    for r in table_with(path, "en"):
        en = r.get("en", "").strip()
        if is_placeholder(en):
            continue
        out.append({
            "en": en,
            "aliases": split_aliases(r.get("alias", "")),
            "vi": r.get("vi", "").strip(),
            "row": r,
        })
    return out


@lru_cache(maxsize=None)
def term_regex(term, case_sensitive=False):
    flags = 0 if case_sensitive else re.IGNORECASE
    return re.compile(r"(?<![\w’'])" + re.escape(term) + r"(?![\w’'])", flags)


def contains(text, term, case_sensitive=False):
    return bool(term_regex(term, case_sensitive).search(text))


def contains_term(raw_text, term):
    """Tìm thuật ngữ trong raw. Thuật ngữ có chữ hoa thì so đúng hoa/thường,
    để 'unique traces' không bị tính là phẩm cấp 'Unique'."""
    return contains(raw_text, term, case_sensitive=term != term.lower())


# ---------- Raw ----------

def strip_notes(line):
    """Bỏ ghi chú translator kẹp trong dòng; trả về "" nếu cả dòng chỉ là ghi chú."""
    s = INLINE_NOTE_RE.sub("", line).strip()
    if TN_RE.match(s):  # dòng bắt đầu bằng "T/N: ..." không có ngoặc
        return ""
    return s


def clean_raw(text, ignore=()):
    """Các đoạn truyện của raw: bỏ dòng tiêu đề, dòng phân cách, ghi chú translator/editor
    (giữ phần truyện của dòng có ghi chú kẹp giữa), bỏ phần lời nhắn cuối chương,
    và các dòng nằm trong `ignore` (so nguyên dòng sau khi strip)."""
    ignore = {s.strip() for s in ignore}
    lines = text.splitlines()
    if lines and not lines[0].strip().startswith(("\"", "“", "[")):
        lines = lines[1:]  # dòng đầu là tiêu đề chương
    out = []
    for line in lines:
        s = line.strip()
        if NOTE_HEADER_RE.match(s):
            break
        if not s or SEPARATOR_RE.match(s) or s in ignore:
            continue
        s = strip_notes(s)
        if s:
            out.append(s)
    return out


def raw_file(novel, row):
    return novel["raw_path"] / row["file raw"]


def raw_paragraphs(novel, row):
    """clean_raw áp thêm danh sách `raw_ignore_lines` trong novel.json
    (dòng raw không phải truyện mà rules.md quyết định bỏ, vd bảng chú giải ký hiệu)."""
    return clean_raw(read_text(raw_file(novel, row)), novel.get("raw_ignore_lines", []))


# ---------- Progress ----------

PROGRESS_HEADER = "| # | Chương truyện | File raw | Tiêu đề | Trạng thái | Ghi chú |"


def progress_path(novel):
    return novel["dir"] / "progress.md"


def load_progress(novel):
    rows = table_with(progress_path(novel), "file raw")
    for r in rows:
        r["idx"] = int(r["#"])
    return rows


def save_progress(novel, rows):
    path = progress_path(novel)
    text = read_text(path)
    lines = text.splitlines()
    start = next(i for i, l in enumerate(lines) if l.strip() == PROGRESS_HEADER)
    end = start + 2
    while end < len(lines) and lines[end].strip().startswith("|"):
        end += 1
    body = [
        f"| {r['idx']} | {r['chương truyện']} | {r['file raw']} | {r['tiêu đề']} | {r['trạng thái']} | {r['ghi chú']} |"
        for r in rows
    ]
    lines[start + 2:end] = body
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def get_row(rows, idx):
    for r in rows:
        if r["idx"] == idx:
            return r
    die(f"không có chương #{idx} trong progress.md")


def parse_range(spec):
    """'5' -> [5]; '1-10' -> [1..10]; '1,3,5-7' -> [1,3,5,6,7]."""
    out = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            out.extend(range(int(a), int(b) + 1))
        elif part:
            out.append(int(part))
    return out
