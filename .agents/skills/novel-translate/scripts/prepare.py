"""Chuẩn bị trước khi dịch một chương: in mọi thứ agent cần biết.

    python prepare.py <slug> [idx]     # bỏ idx thì lấy chương todo kế tiếp

In ra: thông tin chương, góc nhìn ước lượng, nhân vật xuất hiện + xưng hô liên quan,
thuật ngữ mới chưa có trong glossary, tóm tắt 3 chương trước và file bản dịch liền trước.
"""
import argparse
import re

from common import (TRANSLATED, contains, raw_paragraphs, die, entries, get_row, load_novel, load_progress, raw_file,
                    read_text, table_with, utf8_stdout, vi_file)
from extract_terms import pov_hint, report


def characters_in(novel, text):
    found = []
    for e in entries(novel["context"] / "characters.md"):
        hits = sum(len(re.findall(r"(?<![\w’'])" + re.escape(t) + r"(?![\w’'])", text)) for t in [e["en"], *e["aliases"]])
        if hits:
            found.append((e, hits))
    return sorted(found, key=lambda x: -x[1])


def pronoun_rows(novel, names):
    names = {n.lower() for n in names}
    rows = []
    for r in table_with(novel["context"] / "pronouns.md", "a"):
        a, b = r.get("a", "").lower(), r.get("b", "").lower()
        if a in names and (b in names or b in {"*", "mọi người", "tất cả"}):
            rows.append(r)
    return rows


def narrator_rows(novel, names):
    names = {n.lower() for n in names}
    return [r for r in table_with(novel["context"] / "pronouns.md", "nhân vật") if r.get("nhân vật", "").lower() in names]


def summaries(novel, idxs):
    text = read_text(novel["context"] / "summaries.md") if (novel["context"] / "summaries.md").exists() else ""
    parts = re.split(r"(?m)^## +#?(\d+)\b", text)
    by_idx = {int(parts[i]): parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)}
    return [(i, by_idx.get(i)) for i in idxs]


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("idx", nargs="?", type=int)
    args = ap.parse_args()
    novel = load_novel(args.slug)
    rows = load_progress(novel)

    if args.idx is None:
        todo = [r for r in rows if r["trạng thái"] == "todo"]
        if not todo:
            die("hết chương todo")
        row = todo[0]
    else:
        row = get_row(rows, args.idx)
    idx = row["idx"]
    if row["trạng thái"] == "skip":
        print(f"CẢNH BÁO: chương #{idx} đang 'skip' ({row['ghi chú']}).")

    raw = raw_file(novel, row)
    paras = raw_paragraphs(novel, row)
    text = "\n".join(paras)
    words = len(text.split())

    print(f"# Chương #{idx}: {row['tiêu đề']}")
    print(f"Raw:      {raw.as_posix()}")
    print(f"Bản dịch: {vi_file(novel, idx).as_posix()}")
    print(f"Độ dài: {words} từ, {len(paras)} đoạn (đã bỏ tiêu đề, phân cách, T/N)")

    h = pov_hint(paras)
    print(f"\n## Góc nhìn (ước lượng)\n{h['pov']} — I/me/my ngoài thoại: {h['first']}, he/she ngoài thoại: {h['third']}; "
          f"{h['dialogue']} đoạn thoại, {h['system']} đoạn [ ].")

    chars = characters_in(novel, text)
    print("\n## Nhân vật đã biết xuất hiện")
    for e, n in chars:
        print(f"  {n:>3}× {e['en']} -> {e['vi'] or e['en']}  ({e['row'].get('vai trò', '')})")
    if not chars:
        print("  (chưa nhận ra nhân vật nào trong characters.md)")
    names = [e["en"] for e, _ in chars]
    nar = narrator_rows(novel, names)
    pr = pronoun_rows(novel, names)
    print("\n## Xưng hô liên quan (pronouns.md)")
    for r in nar:
        print(f"  Người kể gọi {r['nhân vật']}: {r.get('người kể gọi', '')}  (từ chương {r.get('từ chương', '')}) {r.get('ghi chú', '')}")
    for r in pr:
        print(f"  {r['a']} → {r['b']}: xưng '{r.get('a xưng', '')}', gọi '{r.get('a gọi b', '')}'  "
              f"(từ chương {r.get('từ chương', '')}) {r.get('ghi chú', '')}")
    if not nar and not pr:
        print("  (chưa có dòng nào khớp — tự xác định và bổ sung sau khi dịch)")

    print("\n## Thuật ngữ")
    report(novel, paras, show_all=True)

    print("\n## Mạch truyện")
    prev = [r["idx"] for r in rows if r["idx"] < idx and r["trạng thái"] in TRANSLATED][-3:]
    if not prev:
        print("  (chưa có chương nào đã dịch trước chương này)")
    for i, s in summaries(novel, prev):
        print(f"  #{i}: {s or '(THIẾU tóm tắt trong summaries.md)'}")
    if prev:
        print(f"  Bản dịch liền trước: {vi_file(novel, prev[-1]).as_posix()}")
    tn = sum(1 for l in read_text(raw).splitlines() if re.search(r"T/N|TL\s*note", l, re.I))
    if tn:
        print(f"\nGhi chú translator (T/N) trong raw: {tn} dòng — đã lọc khỏi số đoạn, KHÔNG dịch.")


if __name__ == "__main__":
    main()
