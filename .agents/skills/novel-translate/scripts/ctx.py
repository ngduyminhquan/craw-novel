"""Tra cứu và ghi file context bằng lệnh, không phải mở cả file (context của truyện dài rất lớn).

Tra cứu (mọi truyện):
    python ctx.py <slug> find <từ>                       # tìm theo EN / Alias / VI trong glossary + characters
    python ctx.py <slug> show-char <tên>                 # dòng bảng + mục chi tiết của một nhân vật
    python ctx.py <slug> pronouns <tên> [<tên 2>]        # xưng hô liên quan tới nhân vật (hoặc một cặp)
    python ctx.py <slug> show-summaries <range>          # tóm tắt các chương
    python ctx.py <slug> grep <chuỗi/regex> [--range A-B] # tìm trong các bản dịch đã có (giữ nhất quán)
    python ctx.py <slug> arc [N]                         # layout 2: arc chứa chương N; bỏ N thì in các arc thiếu tóm tắt

Ghi (chỉ truyện layout 2 — novel.json có "layout": 2; layout 1 sửa thẳng file như cũ):
    python ctx.py <slug> add-term --en X [--alias "a; b"] --vi Y --kind <loại> --ch N [--note ...] [--force]
    python ctx.py <slug> add-char --en X [--alias "a; b"] --vi Y --role ... --ch N [--detail "..."]...
    python ctx.py <slug> char-note <tên> "<nội dung>" [--replace <nhãn>]   # thêm (hoặc thay) một dòng mục chi tiết
    python ctx.py <slug> add-alias <tên/thuật ngữ> "<alias>"
    python ctx.py <slug> set <glossary|characters> <tên/thuật ngữ> <cột> "<giá trị>"
    python ctx.py <slug> add-narrator <tên> "<người kể gọi>" N ["<ghi chú>"]
    python ctx.py <slug> add-pronoun <A> <B|*> "<A xưng>" "<A gọi B>" N ["<ghi chú>"]
    python ctx.py <slug> add-summary N "<tóm tắt>" [--replace]
    python ctx.py <slug> set-arc-summary <số arc> "<tóm tắt arc>"
    python ctx.py <slug> set-story <số arc> --file <file>

Mọi lệnh nhận nội dung dài có thể dùng --file <file UTF-8> thay cho chuỗi (tránh lỗi dấu " của PowerShell).
Lệnh ghi tự kiểm tra trùng, ký tự '|', tên xưng hô không có trong characters.md...; phạm lỗi thì không ghi gì.
"""
import argparse
import re
import sys

from common import (ARC_SUMMARY_HEADER, ArgParser, STORY_LIMIT, _cells, all_summaries, arc_file, arc_label, arc_of, arcs,
                    arc_summary_text, die, entries, layout, load_novel, load_progress, missing_arc_summaries,
                    parse_range, read_text, sections, split_aliases, story_arc, story_path,
                    table_with, utf8_stdout)
from lint_context import KINDS

ARC_SUMMARY_LIMIT = 2000
SEP_RE = re.compile(r"^\|?\s*:?-{2,}")


# ---------- file / bảng ----------

def ctx_file(novel, name):
    return novel["context"] / f"{name}.md"


def load_lines(path):
    return read_text(path).splitlines() if path.exists() else []


def save_lines(path, lines):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip("\n") + "\n", encoding="utf-8")


def find_table(lines, col, path):
    """(dòng tiêu đề, danh sách cột viết thường, dòng ngay sau dòng cuối của bảng) của bảng đầu tiên có cột `col`."""
    for i, line in enumerate(lines):
        if line.strip().startswith("|") and i + 1 < len(lines) and SEP_RE.match(lines[i + 1].strip()):
            cols = [c.lower() for c in _cells(line)]
            if col in cols:
                end = i + 2
                while end < len(lines) and lines[end].strip().startswith("|"):
                    end += 1
                return i, cols, end
    die(f"{path.name}: không thấy bảng có cột '{col}'")


def cell(value, name):
    v = (value or "").strip()
    if "|" in v or "\n" in v:
        die(f"{name}: không được chứa '|' hay xuống dòng: {v!r}")
    return v


def make_row(cols, values):
    return "| " + " | ".join(values.get(c, "") for c in cols) + " |"


def append_row(path, col, values):
    lines = load_lines(path)
    _, cols, end = find_table(lines, col, path)
    lines.insert(end, make_row(cols, values))
    save_lines(path, lines)


def text_arg(args, attr="text"):
    if getattr(args, "file", None):
        return read_text(args.file).strip()
    value = getattr(args, attr, None)
    if not value:
        die("thiếu nội dung: truyền chuỗi hoặc --file <file>")
    return value.strip()


def need_layout2(novel):
    if layout(novel) < 2:
        die("lệnh ghi của ctx.py chỉ dùng cho truyện layout 2 (novel.json có \"layout\": 2). "
            "Truyện layout 1 sửa thẳng file context như cũ.")


# ---------- tra cứu ----------

def all_entries(novel):
    return ([("glossary", e) for e in entries(ctx_file(novel, "glossary"))]
            + [("characters", e) for e in entries(ctx_file(novel, "characters"))])


def keys(e):
    return {e["en"].lower(), *(a.lower() for a in e["aliases"])}


def owner(novel, term):
    t = term.strip().lower()
    return next(((f, e) for f, e in all_entries(novel) if t in keys(e)), None)


def removed_terms(novel):
    out, inside = set(), False
    for line in load_lines(ctx_file(novel, "glossary")):
        if line.startswith("## "):
            inside = line.startswith("## Đã loại")
        elif inside and line.startswith("- "):
            out.add(re.split(r"\s+[—-]\s+", line[2:], maxsplit=1)[0].strip().strip("`").lower())
    return out


def resolve(novel, name, fname=None):
    """Tìm đúng một mục theo EN, Alias hoặc VI. fname giới hạn trong glossary/characters.
    Không có mục khớp nguyên vẹn thì thử khớp một phần (vd 'Takumu' cho 'Suzunose Takumu');
    chỉ dùng khi ra đúng một mục."""
    n = name.strip().lower()
    pool = [(f, e) for f, e in all_entries(novel) if fname is None or f == fname]
    hits = [(f, e) for f, e in pool if n in keys(e) or n == e["vi"].lower()]
    exact = [(f, e) for f, e in hits if n in keys(e)]
    hits = exact if len(exact) == 1 else hits
    if not hits and n:
        hits = [(f, e) for f, e in pool if any(n in t for t in [*keys(e), e["vi"].lower()])]
        if len(hits) == 1:
            print(f"('{name}' khớp một phần với {hits[0][0]}: {hits[0][1]['en']})", file=sys.stderr)
    if len(hits) != 1:
        where = "".join(f"\n  {f}: {e['en']} -> {e['vi']}" for f, e in hits)
        die(f"cần đúng 1 mục khớp '{name}', thấy {len(hits)}.{where or ' Thêm mục trước (add-term / add-char).'}")
    return hits[0]


def char_key(novel, name):
    if name.strip() == "*":
        return "*"
    return resolve(novel, name, "characters")[1]["en"]


def row_line(e):
    return " | ".join(v for v in e["row"].values())


def cmd_find(novel, q):
    q = q.strip().lower()
    n = 0
    for f, e in all_entries(novel):
        if any(q in t for t in [*keys(e), e["vi"].lower()]):
            print(f"{f}: {row_line(e)}")
            n += 1
    for t in sorted(removed_terms(novel)):
        if q in t:
            print(f"glossary (Đã loại, không thêm lại): {t}")
            n += 1
    if not n:
        print(f"(không có mục nào chứa '{q}')")


def detail_section(lines, e):
    """(dòng '### ...', dòng kết thúc) của mục chi tiết nhân vật, hoặc (None, None)."""
    names = {*keys(e), e["vi"].lower()}
    for i, line in enumerate(lines):
        if line.startswith("### ") and line[4:].strip().lower() in names:
            end = next((j for j in range(i + 1, len(lines)) if lines[j].startswith(("### ", "## "))), len(lines))
            return i, end
    return None, None


def cmd_show_char(novel, name):
    _, e = resolve(novel, name, "characters")
    print(row_line(e))
    lines = load_lines(ctx_file(novel, "characters"))
    start, end = detail_section(lines, e)
    print("\n".join(lines[start:end]).rstrip() if start is not None else "(chưa có mục chi tiết)")


def cmd_pronouns(novel, names):
    ks = {char_key(novel, n).lower() for n in names}
    path = ctx_file(novel, "pronouns")
    for r in table_with(path, "nhân vật"):
        if r.get("nhân vật", "").lower() in ks:
            print(f"Người kể gọi {r['nhân vật']}: {r.get('người kể gọi', '')}  (từ chương {r.get('từ chương', '')}) "
                  f"{r.get('ghi chú', '')}")
    for r in table_with(path, "a"):
        a, b = r.get("a", "").lower(), r.get("b", "").lower()
        hit = (a in ks and b in ks) if len(ks) > 1 else (a in ks or b in ks)
        if hit:
            print(f"{r['a']} → {r['b']}: xưng '{r.get('a xưng', '')}', gọi '{r.get('a gọi b', '')}'  "
                  f"(từ chương {r.get('từ chương', '')}) {r.get('ghi chú', '')}")


def cmd_grep(novel, pattern, spec, limit):
    """Tìm trong các bản dịch đã có (để giữ nhất quán cách dịch với chương trước)."""
    try:
        rx = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
    except re.error as err:
        die(f"regex sai: {err}. Tìm chuỗi thường thì bỏ các ký tự đặc biệt ( ) [ ] * + ?")
    files = sorted(novel["vi_path"].glob("Chapter_*.md"))
    if spec:
        want = set(parse_range(spec))
        files = [f for f in files if int(re.search(r"\d+", f.stem).group()) in want]
    n = 0
    for f in files:
        for k, line in enumerate(read_text(f).splitlines(), 1):
            m = rx.search(line)
            if not m:
                continue
            n += 1
            if n > limit:
                print(f"... còn nữa, thu hẹp --range hoặc tăng --max (đang {limit})")
                return
            a = max(0, m.start() - 60)
            print(f"{f.stem}:{k}: {'…' if a else ''}{line[a:m.end() + 80]}")
    if not n:
        print(f"(không thấy '{pattern}' trong {len(files)} chương)")


def cmd_show_summaries(novel, spec):
    have = all_summaries(novel)
    for i in parse_range(spec):
        print(f"## {i}\n{have.get(i, '(chưa có)')}\n")


def cmd_arc(novel, idx):
    rows = load_progress(novel)
    if idx is not None:
        a = arc_of(arcs(novel, rows), idx)
        print(f"{arc_label(a)}\nfile: {arc_file(novel, a).as_posix()}")
        return
    miss = missing_arc_summaries(novel, rows)
    print(f"story-so-far.md cập nhật đến arc {story_arc(novel)}")
    for a in miss:
        print(f"thiếu: {arc_label(a)}")
    if not miss:
        print("(không có arc nào thiếu tóm tắt)")


# ---------- ghi glossary / characters ----------

def check_new_terms(novel, terms):
    removed = removed_terms(novel)
    seen = set()
    for t in terms:
        cell(t, "EN/Alias")
        low = t.lower()
        if low in seen:
            die(f"'{t}' lặp lại hai lần trong lệnh")
        seen.add(low)
        hit = owner(novel, t)
        if hit:
            die(f"'{t}' đã có ở {hit[0]}.md, dòng '{hit[1]['en']}' -> '{hit[1]['vi']}'. "
                f"Cách viết khác của cùng mục thì dùng add-alias; khác mục thì kiểm tra lại.")
        if low in removed:
            die(f"'{t}' nằm trong '## Đã loại' của glossary.md: không thêm lại, dịch tự nhiên theo ngữ cảnh.")


def cmd_add_term(novel, a):
    aliases = split_aliases(a.alias)
    check_new_terms(novel, [a.en, *aliases])
    vi, note, kind = cell(a.vi, "VI"), cell(a.note, "Ghi chú"), a.kind.strip().lower()
    if kind not in KINDS:
        die(f"--kind '{a.kind}' không hợp lệ, dùng một trong: {', '.join(sorted(KINDS))}")
    if "/" in vi and not note:
        die("VI chỉ ghi MỘT bản dịch. Thật sự cần hai dạng theo ngữ cảnh thì --note phải nói khi nào dùng dạng nào; "
            "tên gọi tắt thì thêm dòng riêng.")
    same = [e for e in entries(ctx_file(novel, "glossary")) if e["vi"].strip().lower() == vi.lower()]
    if same and not a.force:
        die(f"glossary đã có mục dịch là '{vi}': {', '.join(e['en'] for e in same)}. Cùng một thứ thì dùng "
            f"add-alias {same[0]['en']} \"{a.en}\"; khác thứ thật thì thêm --force.")
    append_row(ctx_file(novel, "glossary"), "en", {
        "en": cell(a.en, "EN"), "alias": "; ".join(aliases), "vi": vi, "loại": kind,
        "chương đầu": str(a.ch), "ghi chú": note})
    print(f"glossary +: {a.en} -> {vi} ({kind}, #{a.ch})")


def appear_value(path, ch):
    """Ghi cột 'Xuất hiện' theo đúng kiểu đang dùng trong file ('Chương N' hay '#N')."""
    rows = table_with(path, "en")
    sample = next((r.get("xuất hiện", "") for r in rows if r.get("xuất hiện", "").strip()), "")
    return f"Chương {ch}" if sample.lower().startswith("chương") else f"#{ch}"


def cmd_add_char(novel, a):
    aliases = split_aliases(a.alias)
    check_new_terms(novel, [a.en, *aliases])
    path = ctx_file(novel, "characters")
    vi = cell(a.vi, "VI")
    append_row(path, "en", {"en": cell(a.en, "EN"), "alias": "; ".join(aliases), "vi": vi,
                            "vai trò": cell(a.role, "Vai trò"), "xuất hiện": appear_value(path, a.ch)})
    print(f"characters +: {a.en} -> {vi} (#{a.ch})")
    if a.detail:
        lines = load_lines(path)
        lines = insert_detail(lines, vi, [d if d.startswith("- ") else f"- {d}" for d in a.detail])
        save_lines(path, lines)
        print(f"  + mục chi tiết '### {vi}' ({len(a.detail)} dòng)")


def insert_detail(lines, heading, body):
    """Thêm mục '### heading' vào cuối phần '## Chi tiết' (tạo phần này nếu chưa có)."""
    start = next((i for i, l in enumerate(lines) if l.strip() == "## Chi tiết"), None)
    if start is None:
        return lines + ["", "## Chi tiết", "", f"### {heading}", *body]
    end = next((j for j in range(start + 1, len(lines)) if lines[j].startswith("## ")), len(lines))
    while end > start + 1 and not lines[end - 1].strip():
        end -= 1
    return lines[:end] + ["", f"### {heading}", *body] + lines[end:]


def cmd_char_note(novel, name, text, replace=None):
    _, e = resolve(novel, name, "characters")
    if "\n" in text:
        die("mỗi lần chỉ thêm một dòng; gọi lại lệnh cho dòng tiếp theo")
    line = text if text.startswith("- ") else f"- {text}"
    if replace and not line[2:].lower().startswith(replace.lower()):
        die(f"--replace '{replace}': nội dung phải bắt đầu bằng đúng nhãn đó, vd \"{replace}: ...\"")
    path = ctx_file(novel, "characters")
    lines = load_lines(path)
    start, end = detail_section(lines, e)
    if start is None:
        lines = insert_detail(lines, e["vi"] or e["en"], [line])
        action = "+"
    else:
        old = [i for i in range(start + 1, end)
               if replace and lines[i].lstrip("- ").lower().startswith(replace.lower())]
        if old:
            lines[old[0]] = line
            for i in reversed(old[1:]):
                lines.pop(i)
            action = "thay"
        else:
            while end > start + 1 and not lines[end - 1].strip():
                end -= 1
            lines.insert(end, line)
            action = "+"
    save_lines(path, lines)
    print(f"characters: '{e['en']}' {action} {line}")


def set_cell(novel, fname, name, col, value):
    _, e = resolve(novel, name, fname)
    path = ctx_file(novel, fname)
    lines = load_lines(path)
    head, cols, end = find_table(lines, "en", path)
    if col not in cols:
        die(f"{fname}.md không có cột '{col}'. Các cột: {', '.join(cols)}")
    for i in range(head + 2, end):
        cells = _cells(lines[i])
        cells += [""] * (len(cols) - len(cells))
        if cells[cols.index("en")].strip().lower() == e["en"].lower():
            cells[cols.index(col)] = value
            lines[i] = make_row(cols, dict(zip(cols, cells)))
            save_lines(path, lines)
            return e
    die(f"không thấy dòng '{e['en']}' trong bảng {fname}.md")


def cmd_add_alias(novel, name, alias):
    f, e = resolve(novel, name)
    new = split_aliases(alias)
    check_new_terms(novel, new)
    set_cell(novel, f, e["en"], "alias", "; ".join([*e["aliases"], *new]))
    print(f"{f}: '{e['en']}' + alias {'; '.join(new)}")


def cmd_set(novel, fname, name, col, value):
    col = col.strip().lower()
    if col in ("en", "alias"):
        die("không đổi cột EN/Alias bằng set: EN là khoá mà pronouns.md tham chiếu; thêm alias thì dùng add-alias")
    value = cell(value, col)
    if fname == "glossary" and col == "loại" and value.lower() not in KINDS:
        die(f"Loại '{value}' không hợp lệ, dùng một trong: {', '.join(sorted(KINDS))}")
    e = set_cell(novel, fname, name, col, value)
    print(f"{fname}: '{e['en']}' {col} = {value}")


# ---------- ghi pronouns ----------

def cmd_add_narrator(novel, name, call, ch, note):
    key = char_key(novel, name)
    path = ctx_file(novel, "pronouns")
    call = cell(call, "Người kể gọi")
    for r in table_with(path, "nhân vật"):
        if r.get("nhân vật", "").lower() == key.lower() and r.get("người kể gọi", "").strip() == call:
            die(f"đã có: người kể gọi {key} là '{call}' (từ chương {r.get('từ chương', '')})")
    append_row(path, "nhân vật", {"nhân vật": key, "người kể gọi": call, "từ chương": str(ch),
                                  "ghi chú": cell(note, "Ghi chú")})
    print(f"pronouns + người kể gọi {key}: {call} (từ #{ch})")


def cmd_add_pronoun(novel, a_name, b_name, self_word, call, ch, note):
    a, b = char_key(novel, a_name), char_key(novel, b_name)
    if a == "*":
        die("A phải là một nhân vật cụ thể")
    path = ctx_file(novel, "pronouns")
    self_word, call = cell(self_word, "A xưng"), cell(call, "A gọi B")
    pair = [r for r in table_with(path, "a")
            if r.get("a", "").lower() == a.lower() and r.get("b", "").lower() == b.lower()]
    if pair and pair[-1].get("a xưng", "").strip() == self_word and pair[-1].get("a gọi b", "").strip() == call:
        die(f"đã có: {a} → {b} xưng '{self_word}', gọi '{call}' (từ chương {pair[-1].get('từ chương', '')})")
    append_row(path, "a", {"a": a, "b": b, "a xưng": self_word, "a gọi b": call, "từ chương": str(ch),
                           "ghi chú": cell(note, "Ghi chú")})
    print(f"pronouns + {a} → {b}: xưng '{self_word}', gọi '{call}' (từ #{ch})")


# ---------- ghi tóm tắt ----------

def check_summary_text(text):
    if any(l.lstrip().startswith("#") for l in text.splitlines()):
        die("tóm tắt không được có dòng bắt đầu bằng '#'")


def write_arc_file(path, title, arc_summary, chapters):
    out = [title, ""]
    if arc_summary:
        out += [ARC_SUMMARY_HEADER, "", arc_summary, ""]
    for i in sorted(chapters):
        out += [f"## {i}", chapters[i], ""]
    save_lines(path, out)


def read_arc_file(path):
    text = read_text(path) if path.exists() else ""
    chapters = {}
    for head, body in sections(text):
        m = re.match(r"#?(\d+)\b", head or "")
        if m:
            chapters[int(m.group(1))] = body.strip()
    return arc_summary_text(text), chapters


def cmd_add_summary(novel, idx, text, replace):
    check_summary_text(text)
    rows = load_progress(novel)
    a = arc_of(arcs(novel, rows), idx)
    if a is None:
        die(f"không có chương #{idx} trong progress.md")
    path = arc_file(novel, a)
    arc_sum, chapters = read_arc_file(path)
    if idx in chapters and not replace:
        die(f"chương #{idx} đã có tóm tắt trong {path.name}; muốn ghi đè thì thêm --replace")
    chapters[idx] = text
    write_arc_file(path, f"# {arc_label(a)}", arc_sum, chapters)
    print(f"summaries/{path.name} + ## {idx}")


def get_arc(novel, no):
    a = next((x for x in arcs(novel, load_progress(novel)) if x["no"] == no), None)
    if a is None:
        die(f"không có arc {no}")
    return a


def cmd_set_arc_summary(novel, no, text):
    check_summary_text(text)
    if len(text) > ARC_SUMMARY_LIMIT:
        die(f"tóm tắt arc dài {len(text)} ký tự, tối đa {ARC_SUMMARY_LIMIT}: viết gọn lại")
    a = get_arc(novel, no)
    path = arc_file(novel, a)
    _, chapters = read_arc_file(path)
    write_arc_file(path, f"# {arc_label(a)}", text, chapters)
    print(f"summaries/{path.name}: đã ghi '{ARC_SUMMARY_HEADER}' ({len(text)} ký tự)")


def cmd_set_story(novel, no, text):
    if len(text) > STORY_LIMIT:
        die(f"story-so-far dài {len(text)} ký tự, tối đa {STORY_LIMIT}: nén các arc cũ lại")
    a = get_arc(novel, no)
    p = arc_file(novel, a)
    if not (p.exists() and arc_summary_text(read_text(p))):
        die(f"arc {no} chưa có tóm tắt arc: chạy set-arc-summary {no} trước")
    if no < story_arc(novel):
        die(f"story-so-far đã cập nhật đến arc {story_arc(novel)}, không ghi lùi về arc {no}")
    header = [f"# Câu chuyện tới giờ — {novel.get('title', '')}",
              f"<!-- cập nhật đến arc {no} (#{a['first']}–#{a['last']}). Ghi bằng ctx.py set-story, "
              f"tối đa {STORY_LIMIT} ký tự. -->", ""]
    save_lines(story_path(novel), header + [text])
    print(f"story-so-far.md: cập nhật đến arc {no} ({len(text)}/{STORY_LIMIT} ký tự)")


# ---------- main ----------

def main():
    utf8_stdout()
    ap = ArgParser()
    ap.add_argument("slug")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("find")
    p.add_argument("q", nargs="?")
    p = sub.add_parser("grep")
    p.add_argument("pattern", help="chuỗi hoặc regex, không phân biệt hoa/thường; vd '^# Chương' để xem tiêu đề")
    p.add_argument("--range", help="chỉ tìm trong các chương này, vd 1-12")
    p.add_argument("--max", type=int, default=40, help="số dòng tối đa in ra (mặc định 40)")
    p = sub.add_parser("show-char")
    p.add_argument("name")
    p = sub.add_parser("pronouns")
    p.add_argument("names", nargs="+")
    p = sub.add_parser("show-summaries")
    p.add_argument("range")
    p = sub.add_parser("arc")
    p.add_argument("idx", nargs="?", type=int)

    p = sub.add_parser("add-term")
    p.add_argument("--en", required=True)
    p.add_argument("--alias", default="")
    p.add_argument("--vi", required=True)
    p.add_argument("--kind", required=True)
    p.add_argument("--ch", required=True, type=int)
    p.add_argument("--note", default="")
    p.add_argument("--force", action="store_true", help="cho phép trùng VI với một mục khác")
    p = sub.add_parser("add-char")
    p.add_argument("--en", required=True)
    p.add_argument("--alias", default="")
    p.add_argument("--vi", required=True)
    p.add_argument("--role", required=True)
    p.add_argument("--ch", required=True, type=int)
    p.add_argument("--detail", action="append", help="một dòng của mục chi tiết; lặp lại cho nhiều dòng")
    p = sub.add_parser("char-note")
    p.add_argument("name")
    p.add_argument("text", nargs="?")
    p.add_argument("--file")
    p.add_argument("--replace", metavar="NHÃN",
                   help="thay dòng đang bắt đầu bằng nhãn này (vd 'Kỹ năng') thay vì thêm dòng mới")
    p = sub.add_parser("add-alias")
    p.add_argument("name")
    p.add_argument("alias")
    p = sub.add_parser("set")
    p.add_argument("table", choices=["glossary", "characters"])
    p.add_argument("name")
    p.add_argument("column")
    p.add_argument("value")
    p = sub.add_parser("add-narrator")
    p.add_argument("name")
    p.add_argument("call")
    p.add_argument("ch", type=int)
    p.add_argument("note", nargs="?", default="")
    p = sub.add_parser("add-pronoun")
    p.add_argument("a")
    p.add_argument("b")
    p.add_argument("self_word")
    p.add_argument("call")
    p.add_argument("ch", type=int)
    p.add_argument("note", nargs="?", default="")
    p = sub.add_parser("add-summary")
    p.add_argument("idx", type=int)
    p.add_argument("text", nargs="?")
    p.add_argument("--file")
    p.add_argument("--replace", action="store_true")
    p = sub.add_parser("set-arc-summary")
    p.add_argument("arc", type=int)
    p.add_argument("text", nargs="?")
    p.add_argument("--file")
    p = sub.add_parser("set-story")
    p.add_argument("arc", type=int)
    p.add_argument("text", nargs="?")
    p.add_argument("--file")
    args = ap.parse_args()

    novel = load_novel(args.slug)
    c = args.cmd
    if c == "find" and not args.q:
        die("find cần một từ khoá. Không có lệnh liệt kê toàn bộ glossary/characters (sẽ rất lớn): "
            "tra từng thuật ngữ, hoặc xem thuật ngữ của chương trong output prepare.py.")
    if c == "grep":
        return cmd_grep(novel, args.pattern, args.range, args.max)
    if c == "find":
        return cmd_find(novel, args.q)
    if c == "show-char":
        return cmd_show_char(novel, args.name)
    if c == "pronouns":
        return cmd_pronouns(novel, args.names)
    if c == "show-summaries":
        return cmd_show_summaries(novel, args.range)
    if c == "arc":
        need_layout2(novel)
        return cmd_arc(novel, args.idx)

    need_layout2(novel)
    if c == "add-term":
        cmd_add_term(novel, args)
    elif c == "add-char":
        cmd_add_char(novel, args)
    elif c == "char-note":
        cmd_char_note(novel, args.name, text_arg(args), args.replace)
    elif c == "add-alias":
        cmd_add_alias(novel, args.name, args.alias)
    elif c == "set":
        cmd_set(novel, args.table, args.name, args.column, args.value)
    elif c == "add-narrator":
        cmd_add_narrator(novel, args.name, args.call, args.ch, args.note)
    elif c == "add-pronoun":
        cmd_add_pronoun(novel, args.a, args.b, args.self_word, args.call, args.ch, args.note)
    elif c == "add-summary":
        cmd_add_summary(novel, args.idx, text_arg(args), args.replace)
    elif c == "set-arc-summary":
        cmd_set_arc_summary(novel, args.arc, text_arg(args))
    elif c == "set-story":
        cmd_set_story(novel, args.arc, text_arg(args))


if __name__ == "__main__":
    sys.exit(main())
