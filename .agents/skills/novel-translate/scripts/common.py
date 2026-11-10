"""Hàm dùng chung cho các script của skill novel-translate (chỉ dùng thư viện chuẩn)."""
import argparse
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
_NOTE_LONG = r"(?:(?:TL|Translator[’']?s?|Editor[’']?s?|Author[’']?s?)\s*notes?|Translation\s+changes?)"
_NOTE_KW = rf"(?:(?:T/N|E/N|P/R)\b\s*:?|(?:TL|ED|PR)\s*:|{_NOTE_LONG}\b\s*:?)"
# Ghi chú kẹp trong câu: "I can fly!" (T/N: Said in English)
# Cho phép một tầng ngoặc lồng bên trong: "(T/N: Holy Knight -> Paladin. (Kang HaJin's job))"
INLINE_NOTE_RE = re.compile(
    rf"\s*(?:\(\s*{_NOTE_KW}(?:[^()]|\([^()]*\))*\)|\[\s*{_NOTE_KW}(?:[^\[\]]|\[[^\[\]]*\])*\])",
    re.IGNORECASE)
# Dòng chỉ có tiêu đề ghi chú ("Editors Note.") — từ đây đến hết file là lời nhắn của translator/editor
NOTE_HEADER_RE = re.compile(rf"^(?:T/N|E/N|{_NOTE_LONG}|Ghi chú tác giả)\s*[:.]?\s*$", re.IGNORECASE)
SEPARATOR_RE = re.compile(r"^[=\-_*~]{3,}$")
# Dòng ảnh, giống regex app và scripts/build_index.py (chapter-image-guide.md). Ảnh không phải đoạn dịch.
IMAGE_RE = re.compile(r"^!\[([^\]]*)]\(([^)]+)\)$")

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


class ArgParser(argparse.ArgumentParser):
    """ArgumentParser báo rõ nguyên nhân thường gặp khi gọi từ PowerShell 5.1:
    chuỗi có dấu " lồng bên trong bị tách thành nhiều tham số."""

    def error(self, message):
        if "unrecognized arguments" in message:
            message += ("\nGỢI Ý: thường là do chuỗi truyền vào có dấu \" lồng bên trong, PowerShell đã tách nó "
                        "thành nhiều tham số. Bỏ dấu \" trong nội dung (dùng '...'), hoặc ghi nội dung vào file "
                        "rồi truyền --file <file> nếu lệnh có.")
        super().error(message)


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
    # Chỉ tách theo ';' — alias có thể chứa dấu phẩy (vd lỗi gõ của raw "Deathgod's, Black Spear")
    return [a.strip() for a in (value or "").split(";") if a.strip()]


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


# ---------- Tiếng Nhật ----------

CJK_RE = re.compile(r"[぀-ヿ㐀-䶿一-鿿豈-﫿ｦ-ﾟ]")
# Chữ katakana (bỏ dấu chấm giữa ・ U+30FB). Dùng làm ranh giới cho thuật ngữ katakana,
# để "レイ" không khớp trong "スレイプニル" hay "レイン".
KATA = "ァ-ヺー-ヿ"
# Sau tên được phép có ッ (gọi "セトッ!") hoặc ー (kéo dài "レイー!").
KATA_AFTER = "ァ-ヂツ-ヺヽ-ヿ"


# Chữ thuộc hệ không bao giờ có trong bản dịch tiếng Việt từ raw Anh/Nhật: Kirin, Hebrew, Ả Rập, Devanagari,
# Thái, Hangul. Model hay lẫn các chữ này khi sinh văn bản (vd "Khiยัง", "ма thuật").
ODD_SCRIPT_RE = re.compile(r"[Ѐ-ӿ֐-׿؀-ۿऀ-ॿ฀-๿가-힯]+")


def has_cjk(s):
    return bool(CJK_RE.search(s or ""))


def is_kata(ch):
    return "ァ" <= ch <= "ヺ" or "ー" <= ch <= "ヿ"


def detect_lang(text):
    """'ja' nếu raw chủ yếu là chữ Nhật, ngược lại 'en'."""
    sample = "".join((text or "").split())[:5000]
    if not sample:
        return "en"
    return "ja" if len(CJK_RE.findall(sample)) / len(sample) > 0.2 else "en"


def raw_lang(novel, text=""):
    """Ngôn ngữ raw: khoá `raw_lang` trong novel.json, không có thì đoán từ `text`."""
    return novel.get("raw_lang") or detect_lang(text)


@lru_cache(maxsize=None)
def term_regex(term, case_sensitive=False):
    if has_cjk(term):
        # Tiếng Nhật không có khoảng trắng và kanji cũng là \w: tìm theo chuỗi con.
        # Riêng đầu/cuối là katakana thì không được dính liền katakana khác.
        pre = f"(?<![{KATA}])" if is_kata(term[0]) else ""
        post = f"(?![{KATA_AFTER}])" if is_kata(term[-1]) else ""
        return re.compile(pre + re.escape(term) + post)
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
    if lines and not lines[0].strip().startswith(("\"", "“", "[", "「", "『")) and not IMAGE_RE.match(lines[0].strip()):
        lines = lines[1:]  # dòng đầu là tiêu đề chương
    out = []
    for line in lines:
        s = line.strip()
        if NOTE_HEADER_RE.match(s):
            break
        if not s or SEPARATOR_RE.match(s) or IMAGE_RE.match(s) or s in ignore:
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


# ---------- Layout 2 (novel.json có "layout": 2) ----------
# Truyện layout 1 (cũ) giữ nguyên: câu hỏi nằm trong progress.md, tóm tắt trong một file summaries.md.
# Layout 2: câu hỏi ở questions.md, quyết định ở decisions/, tóm tắt chia theo arc trong context/summaries/,
# cộng context/story-so-far.md.

STORY_LIMIT = 6000          # số ký tự tối đa của story-so-far.md (khoảng 2k token)
ARC_MAX = 20                # số chương tối đa của một arc (arc dài hơn bị chia thành nhiều phần)
ARC_SUMMARY_HEADER = "## Tóm tắt arc"
STORY_MARK_RE = re.compile(r"<!--\s*cập nhật đến arc\s+(\d+)")
CHAPTER_REF_RE = re.compile(r"\[#(\d+)")


QUESTIONS_HEADER = (
    "# Câu hỏi chờ quyết\n\n"
    "<!-- Mỗi dòng một câu: - [#chương] vấn đề — đề xuất. Ghi bằng progress.py ask; orchestrator quyết bằng "
    "orchestrate.py resolve, câu đã quyết chuyển sang decisions/. -->\n\n")


def layout(novel):
    return int(novel.get("layout", 1))


def questions_path(novel):
    return novel["dir"] / "questions.md"


def decisions_path(novel, item):
    """File quyết định theo khoảng 100 chương, lấy số chương đầu tiên dạng [#N] trong mục."""
    m = CHAPTER_REF_RE.search(item)
    d = novel["dir"] / "decisions"
    if not m:
        return d / "chung.md"
    lo = (int(m.group(1)) - 1) // 100 * 100 + 1
    return d / f"{lo:04d}-{lo + 99:04d}.md"


def story_path(novel):
    return novel["context"] / "story-so-far.md"


def summaries_dir(novel):
    return novel["context"] / "summaries"


def sections(text):
    """[(tiêu đề '## ...', nội dung)] theo thứ tự; phần trước tiêu đề '## ' đầu tiên có tiêu đề None."""
    parts = re.split(r"(?m)^## +(.*)$", text)
    out = [(None, parts[0])]
    for i in range(1, len(parts) - 1, 2):
        out.append((parts[i].strip(), parts[i + 1]))
    return out


def chapter_summaries(text):
    """{số chương: tóm tắt} từ các mục '## N'."""
    out = {}
    for head, body in sections(text):
        m = re.match(r"#?(\d+)\b", head or "")
        if m:
            out[int(m.group(1))] = body.strip()
    return out


def arc_summary_text(text):
    for head, body in sections(text):
        if head and ("## " + head).strip() == ARC_SUMMARY_HEADER:
            return body.strip()
    return ""


def all_summaries(novel):
    """{số chương: tóm tắt} của mọi chương, theo layout của truyện."""
    if layout(novel) < 2:
        # Giữ đúng cách đọc cũ của layout 1.
        p = novel["context"] / "summaries.md"
        text = read_text(p) if p.exists() else ""
        parts = re.split(r"(?m)^## +#?(\d+)\b", text)
        return {int(parts[i]): parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)}
    out = {}
    d = summaries_dir(novel)
    if d.exists():
        for p in sorted(d.glob("arc-*.md")):
            out.update(chapter_summaries(read_text(p)))
    return out


def arcs(novel, rows):
    """Chia chương thành các arc (chỉ layout 2). novel.json "arc_rule":
         {"pattern": "<regex có group 1 lấy tên arc từ cột Tiêu đề>", "max": 20}
       Chương liền nhau cùng tên arc là một arc; arc dài hơn `max` bị chia thành nhiều phần
       (chia từ đầu, phần cuối ngắn quá 1/4 thì gộp vào phần trước, để thêm chương mới không đổi số các arc cũ).
       Không có pattern thì cứ `max` chương là một arc.
       Trả về [{no, name, part, parts, idxs, first, last}], no đánh số từ 1."""
    rule = novel.get("arc_rule") or {}
    size = int(rule.get("max", ARC_MAX))
    pat = re.compile(rule["pattern"]) if rule.get("pattern") else None
    runs = []
    for r in sorted(rows, key=lambda r: r["idx"]):
        m = pat.search(r["tiêu đề"]) if pat else None
        name = m.group(1).strip() if m else ""
        if runs and runs[-1][0] == name:
            runs[-1][1].append(r["idx"])
        else:
            runs.append((name, [r["idx"]]))
    out = []
    for name, idxs in runs:
        chunks = [idxs[i:i + size] for i in range(0, len(idxs), size)]
        if len(chunks) > 1 and len(chunks[-1]) <= size // 4:
            tail = chunks.pop()
            chunks[-1] = chunks[-1] + tail
        for k, c in enumerate(chunks, 1):
            out.append({"no": len(out) + 1, "name": name, "part": k, "parts": len(chunks),
                        "idxs": c, "first": c[0], "last": c[-1]})
    return out


def arc_label(a):
    part = f" (phần {a['part']}/{a['parts']})" if a["parts"] > 1 else ""
    name = f" — {a['name']}" if a["name"] else ""
    return f"Arc {a['no']}{name}{part} · #{a['first']}–#{a['last']}"


def arc_of(arc_list, idx):
    return next((a for a in arc_list if idx in a["idxs"]), None)


def arc_file(novel, a):
    return summaries_dir(novel) / f"arc-{a['no']:03d}.md"


def story_arc(novel):
    """Số arc mà story-so-far.md đã cập nhật đến (0 nếu chưa có)."""
    p = story_path(novel)
    m = STORY_MARK_RE.search(read_text(p)) if p.exists() else None
    return int(m.group(1)) if m else 0


def missing_arc_summaries(novel, rows):
    """Các arc đã dịch xong (mọi chương done/reviewed/skip) mà thiếu tóm tắt arc
    hoặc story-so-far.md chưa cập nhật tới arc đó. Chỉ layout 2."""
    if layout(novel) < 2:
        return []
    status = {r["idx"]: r["trạng thái"] for r in rows}
    done_story = story_arc(novel)
    out = []
    for a in arcs(novel, rows):
        if not all(status[i] in (*TRANSLATED, "skip") for i in a["idxs"]):
            break
        if all(status[i] == "skip" for i in a["idxs"]):
            continue
        p = arc_file(novel, a)
        if not (p.exists() and arc_summary_text(read_text(p))) or done_story < a["no"]:
            out.append(a)
    return out
