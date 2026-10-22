"""Soát bản dịch so với raw.

    python qa_check.py <slug> <range>

Kiểm tra: số đoạn lệch (dấu hiệu bỏ sót), số đoạn [ ], từ tiếng Anh sót lại, T/N còn sót,
thuật ngữ/tên trong glossary + characters có xuất hiện ở raw mà bản dịch không dùng đúng bản dịch,
lẫn lộn kiểu ngoặc kép. Exit 1 nếu có LỖI, 0 nếu chỉ có cảnh báo hoặc sạch.
"""
import argparse
import re
import sys

from common import (TN_RE, clean_raw, contains, entries, get_row, is_placeholder, load_novel, load_progress,
                    parse_range, raw_file, read_text, utf8_stdout, vi_file)

# Từ tiếng Anh không trùng với âm tiết tiếng Việt không dấu.
ENGLISH = set("""
the and was were with that this what have has his her you your they their them she
is are of for but not from would could should which there been will said
when where who why how into about because just only very then than these those
""".split())
ENGLISH_RE = re.compile(r"\b(" + "|".join(sorted(ENGLISH)) + r")\b", re.IGNORECASE)


def vi_paragraphs(text):
    return [l.strip() for l in text.splitlines() if l.strip() and not l.strip().startswith("#")]


def check(novel, row):
    idx = row["idx"]
    errors, warns = [], []
    vf = vi_file(novel, idx)
    if not vf.exists():
        return [f"không có file bản dịch {vf.as_posix()}"], []
    raw_paras = clean_raw(read_text(raw_file(novel, row)))
    raw_text = "\n".join(raw_paras)
    vi_text = read_text(vf)
    vi_paras = vi_paragraphs(vi_text)

    if not vi_text.lstrip().startswith("# "):
        warns.append("thiếu dòng tiêu đề '# Chương N: ...' ở đầu file")

    diff = len(vi_paras) - len(raw_paras)
    tol = max(3, round(len(raw_paras) * 0.05))
    if abs(diff) > tol:
        (errors if diff < 0 else warns).append(
            f"số đoạn lệch: raw {len(raw_paras)}, bản dịch {len(vi_paras)} ({diff:+d}) — "
            + ("nghi BỎ SÓT đoạn, đối chiếu lại" if diff < 0 else "có thể tách đoạn thừa"))

    rb = sum(p.startswith("[") for p in raw_paras)
    vb = sum(p.startswith("[") for p in vi_paras)
    if rb != vb:
        warns.append(f"số đoạn [ ]: raw {rb}, bản dịch {vb}")

    for n, line in enumerate(vi_paras, 1):
        hits = ENGLISH_RE.findall(line)
        if len(hits) >= 2:
            warns.append(f"đoạn {n} còn tiếng Anh ({', '.join(hits[:5])}): {line[:90]}")
        if TN_RE.search(line):
            errors.append(f"đoạn {n} còn ghi chú translator: {line[:90]}")

    if "\"" in vi_text and "“" in vi_text:
        warns.append("lẫn ngoặc kép thẳng \" và cong “ ” — thống nhất theo rules.md")

    ctx = novel["context"]
    for e in entries(ctx / "glossary.md") + entries(ctx / "characters.md"):
        terms = [e["en"], *e["aliases"]]
        if not any(contains(raw_text, t) for t in terms):
            continue
        if is_placeholder(e["vi"]):
            warns.append(f"'{e['en']}' có trong raw nhưng chưa có bản dịch trong context")
            continue
        variants = [v.strip() for v in e["vi"].split("/") if v.strip()]
        if not any(v.lower() in vi_text.lower() for v in variants):
            warns.append(f"'{e['en']}' có trong raw nhưng bản dịch không có '{e['vi']}'")
    return errors, warns


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("range")
    args = ap.parse_args()
    novel = load_novel(args.slug)
    rows = load_progress(novel)
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
