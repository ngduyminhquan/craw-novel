"""Soát bản dịch so với raw.

    python qa_check.py <slug> <range>
    python qa_check.py <slug> <range> --side    # in từng cặp đoạn raw / bản dịch để tìm chỗ sót, gộp đoạn

Kiểm tra: số đoạn lệch (dấu hiệu bỏ sót), số đoạn [ ], từ tiếng Anh sót lại, T/N còn sót,
thuật ngữ/tên trong glossary + characters có xuất hiện ở raw mà bản dịch không dùng đúng bản dịch,
lẫn lộn kiểu ngoặc kép. Exit 1 nếu có LỖI, 0 nếu chỉ có cảnh báo hoặc sạch.
"""
import argparse
import re
import sys

from common import (CJK_RE, IMAGE_RE, ODD_SCRIPT_RE, TN_RE, contains_term, raw_lang, raw_paragraphs, term_regex, entries, get_row,
                    is_placeholder, load_novel, load_progress, parse_range, raw_file, read_text, utf8_stdout, vi_file)

# Từ tiếng Anh không trùng với âm tiết tiếng Việt không dấu.
ENGLISH = set("""
the and was were with that this what have has his her you your they their them she
is are of for but not from would could should which there been will said
when where who why how into about because just only very then than these those
""".split())
ENGLISH_RE = re.compile(r"\b(" + "|".join(sorted(ENGLISH)) + r")\b", re.IGNORECASE)


# Dòng chỉ gồm link markdown, vd điều hướng "[← Chương trước](Chapter_001.md) | [Chương tiếp theo →](...)"
NAV_RE = re.compile(r"^(\s*\[[^\]]*\]\([^)]*\)\s*\|?)+\s*$")
# Dòng ảnh, giống regex app và scripts/build_index.py (chapter-image-guide.md). Ảnh không phải đoạn dịch.
IMAGE_RE = re.compile(r"^!\[([^\]]*)]\(([^)]+)\)$")
# In nghiêng Markdown "*khụ*", "_nhồm nhoàm_". Không bắt chữ bị che kiểu "M** ***t", "dig*mon"
# (dấu * dính liền chữ cái ở phía ngoài).
ITALIC_RE = re.compile(r"(?<![\w*])\*(?=[^\s*])[^*\n]*?(?<=[^\s*])\*(?![\w*])|(?<![\w_])_(?=[^\s_])[^_\n]*?(?<=[^\s_])_(?![\w_])")


def vi_paragraphs(text):
    return [l.strip() for l in text.splitlines()
            if l.strip() and not l.strip().startswith("#") and not NAV_RE.match(l)
            and not IMAGE_RE.match(l.strip())]


def check(novel, row):
    idx = row["idx"]
    errors, warns = [], []
    vf = vi_file(novel, idx)
    if not vf.exists():
        return [f"không có file bản dịch {vf.as_posix()}"], []
    raw_paras = raw_paragraphs(novel, row)
    raw_text = "\n".join(raw_paras)
    vi_text = read_text(vf)
    vi_paras = vi_paragraphs(vi_text)

    if not vi_text.lstrip().startswith("# "):
        warns.append("thiếu dòng tiêu đề '# Chương N: ...' ở đầu file")
    else:
        title_line = vi_text.lstrip().splitlines()[0]
        raw_title = row.get("tiêu đề", "").strip()
        if raw_title and len(raw_title.split()) >= 2 and raw_title.lower() in title_line.lower():
            warns.append(f"tiêu đề chưa dịch, vẫn là tiếng Anh: {title_line[:90]}")

    # rules.md quy định mỗi đoạn raw là một đoạn dịch, nên thiếu dù một đoạn cũng là lỗi.
    diff = len(vi_paras) - len(raw_paras)
    if diff < 0:
        errors.append(f"số đoạn lệch: raw {len(raw_paras)}, bản dịch {len(vi_paras)} ({diff:+d}) — "
                      "nghi BỎ SÓT hoặc GỘP đoạn, đối chiếu lại từng đoạn")
    elif diff > 0:
        warns.append(f"số đoạn lệch: raw {len(raw_paras)}, bản dịch {len(vi_paras)} ({diff:+d}) — "
                     "có thể tách đoạn thừa")

    ja = raw_lang(novel, raw_text) == "ja"
    # Raw tiếng Nhật: 『』 dịch thành [ ] hay ngoặc kép tùy ngữ cảnh (rules.md), nên không so số đoạn [ ].
    rb = sum(p.startswith("[") for p in raw_paras)
    vb = sum(p.startswith("[") for p in vi_paras)
    if rb != vb and not ja:
        warns.append(f"số đoạn [ ]: raw {rb}, bản dịch {vb}")

    raw_imgs = [l.strip() for l in read_text(raw_file(novel, row)).splitlines() if IMAGE_RE.match(l.strip())]
    if raw_imgs:
        vi_imgs = [l.strip() for l in vi_text.splitlines() if IMAGE_RE.match(l.strip())]
        missing_imgs = [img for img in raw_imgs if img not in vi_imgs]
        if missing_imgs:
            errors.append(f"thiếu dòng ảnh có trong raw: {', '.join(missing_imgs)} — giữ nguyên dòng ảnh ở đúng vị trí")

    for n, line in enumerate(vi_paras, 1):
        if ja and ODD_SCRIPT_RE.search(line):
            errors.append(f"đoạn {n} có ký tự lạ ({', '.join(ODD_SCRIPT_RE.findall(line))[:30]}) — "
                          f"chữ Kirin/Thái/Hangul... lẫn vào, sửa lại: {line[:90]}")
        if ja and CJK_RE.search(line):
            warns.append(f"đoạn {n} còn chữ Nhật ({''.join(CJK_RE.findall(line))[:20]}): {line[:90]}")
        hits = ENGLISH_RE.findall(line)
        if len(hits) >= 2:
            warns.append(f"đoạn {n} còn tiếng Anh ({', '.join(hits[:5])}): {line[:90]}")
        if TN_RE.search(line):
            errors.append(f"đoạn {n} còn ghi chú translator: {line[:90]}")
        m = ITALIC_RE.search(line)
        if m:
            errors.append(f"đoạn {n} dùng dấu */_ để in nghiêng ({m.group(0)[:30]}) — app hiện nguyên ký tự, "
                          f"bỏ dấu theo rules.md: {line[:90]}")
        if "![" in line:
            errors.append(f"đoạn {n} có ảnh lẫn trong đoạn văn, ảnh phải nằm riêng một dòng: {line[:90]}")

    if "\"" in vi_text and "“" in vi_text:
        warns.append("lẫn ngoặc kép thẳng \" và cong “ ” — thống nhất theo rules.md")

    ctx = novel["context"]
    # Xét thuật ngữ dài trước và che phần đã khớp, để "God of Concealment" không bị tính là "God",
    # "Status points" không bị tính là "Status".
    char_entries = entries(ctx / "characters.md")
    char_ids = {id(e) for e in char_entries}
    all_entries = entries(ctx / "glossary.md") + char_entries
    all_entries.sort(key=lambda e: -max(len(t) for t in [e["en"], *e["aliases"]]))
    masked = raw_text
    raw_lower = raw_text.lower()
    for e in all_entries:
        # lọc nhanh bằng tìm chuỗi thường trước, regex chỉ chạy cho thuật ngữ có mặt trong chương
        terms = [t for t in [e["en"], *e["aliases"]] if t.lower() in raw_lower]
        present = any(contains_term(masked, t) for t in terms)
        for t in terms:
            masked = term_regex(t, case_sensitive=t != t.lower()).sub(lambda m: " " * len(m.group(0)), masked)
        if not present:
            continue
        if is_placeholder(e["vi"]):
            warns.append(f"'{e['en']}' có trong raw nhưng chưa có bản dịch trong context")
            continue
        variants = [v.strip() for v in e["vi"].split("/") if v.strip()]
        if id(e) in char_ids:
            # Tên nhân vật giữ nguyên: raw gọi tắt bằng alias (vd "Reta" cho "Reta Kar'iha")
            # và bản dịch cũng dùng đúng alias đó thì không phải lệch.
            variants += [t for t in terms if contains_term(raw_text, t)]
            if ja:
                # Raw tiếng Nhật hay gọi tên ngắn (タクム), alias là chữ Nhật nên không dùng được:
                # chấp nhận bản dịch có một chữ trong tên VI (vd "Takumu" cho "Suzunose Takumu").
                variants += [w for w in re.split(r"[\s·・]+", e["vi"]) if len(w) >= 3]
        if not any(v.lower() in vi_text.lower() for v in variants):
            warns.append(f"'{e['en']}' có trong raw nhưng bản dịch không có '{e['vi']}'")
        elif ja and id(e) not in char_ids and len(variants) == 1 and variants[0] != variants[0].lower():
            # Thuật ngữ viết hoa trong glossary (vd "Dao Mithril") phải giữ đúng chữ hoa ở mọi chỗ.
            # In kèm chữ đứng sau để thấy cả cụm (vd "Số thuật sư" là chức danh, nên thêm thuật ngữ riêng).
            wrong = sorted({m.group(0).strip() for m in re.finditer(re.escape(variants[0]) + r"(?:\s+\w+)?",
                                                                     vi_text, re.IGNORECASE)
                            if not m.group(0).startswith(variants[0])})
            if wrong:
                warns.append(f"'{e['vi']}' bị viết hoa/thường khác glossary: {', '.join(wrong)} — sửa lại chữ hoa, "
                             "hoặc nếu là cụm khác (chức danh...) thì thêm thuật ngữ riêng")
    return errors, warns


def side_by_side(novel, row, width=70):
    """In từng cặp đoạn raw / bản dịch (đã lọc như khi đếm), để tìm chỗ bỏ sót hay gộp đoạn."""
    raw_paras = raw_paragraphs(novel, row)
    vf = vi_file(novel, row["idx"])
    vi_paras = vi_paragraphs(read_text(vf)) if vf.exists() else []
    print(f"#{row['idx']}: raw {len(raw_paras)} đoạn, bản dịch {len(vi_paras)} đoạn")
    for k in range(max(len(raw_paras), len(vi_paras))):
        r = raw_paras[k][:width] if k < len(raw_paras) else "(hết)"
        v = vi_paras[k][:width] if k < len(vi_paras) else "(hết)"
        print(f"{k + 1:>4} RAW {r}\n     VI  {v}")


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("range")
    ap.add_argument("--side", action="store_true",
                    help="in từng cặp đoạn raw / bản dịch theo số thứ tự, không chạy QA")
    args = ap.parse_args()
    novel = load_novel(args.slug)
    rows = load_progress(novel)
    if args.side:
        for idx in parse_range(args.range):
            side_by_side(novel, get_row(rows, idx))
        return
    total_err = 0
    for idx in parse_range(args.range):
        row = get_row(rows, idx)
        if row["trạng thái"] == "skip":
            continue
        errors, warns = check(novel, row)
        total_err += len(errors)
        status = "LỖI" if errors else ("cảnh báo" if warns else "OK")
        print(f"#{idx}: {status}")
        for m in errors:
            print(f"  [LỖI] {m}")
        for m in warns:
            print(f"  [cảnh báo] {m}")
    sys.exit(1 if total_err else 0)


if __name__ == "__main__":
    main()
