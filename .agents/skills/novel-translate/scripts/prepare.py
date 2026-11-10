"""Chuẩn bị trước khi dịch một chương: in mọi thứ agent cần biết.

    python prepare.py <slug> [idx]     # bỏ idx thì lấy chương todo kế tiếp

In ra: thông tin chương, góc nhìn ước lượng, nhân vật xuất hiện + xưng hô liên quan,
thuật ngữ mới chưa có trong glossary, mạch truyện và file bản dịch liền trước.
Mạch truyện: layout 1 in tóm tắt 3 chương trước; layout 2 in story-so-far, tóm tắt 2 arc trước
và tóm tắt các chương đã dịch của arc hiện tại.
"""
import argparse
import re

from common import (IMAGE_RE, TRANSLATED, all_summaries, arc_file, arc_label, arc_of, arc_summary_text, arcs, die,
                    entries, get_row, has_cjk, layout, load_novel, load_progress, raw_file, raw_lang, raw_paragraphs, read_text,
                    story_arc, story_path, table_with, term_regex, utf8_stdout, vi_file)
from extract_terms import pov_hint, report


def characters_in(novel, text):
    chars = entries(novel["context"] / "characters.md")
    # Tên tiếng Nhật: đếm tên dài trước rồi che lại, để "佐伯玲二" không bị đếm thêm một lần ở "玲二".
    masked = text
    cjk_hits = {}
    for t, e in sorted(((t, e) for e in chars for t in [e["en"], *e["aliases"]] if has_cjk(t)),
                       key=lambda x: -len(x[0])):
        rx = term_regex(t, True)
        n = len(rx.findall(masked))
        if n:
            cjk_hits[id(e)] = cjk_hits.get(id(e), 0) + n
            masked = rx.sub(lambda m: "　" * len(m.group(0)), masked)
    found = []
    for e in chars:
        hits = cjk_hits.get(id(e), 0) + sum(len(term_regex(t, True).findall(text))
                                            for t in [e["en"], *e["aliases"]] if not has_cjk(t))
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
    by_idx = all_summaries(novel)
    return [(i, by_idx.get(i)) for i in idxs]


def story_context(novel, rows, idx):
    """Layout 2: story-so-far + tóm tắt 2 arc trước + tóm tắt các chương đã dịch của arc hiện tại
    (luôn có ít nhất 3 chương gần nhất). Không in tóm tắt chương của các arc cũ."""
    arc_list = arcs(novel, rows)
    cur = arc_of(arc_list, idx)
    sp = story_path(novel)
    print(f"### Câu chuyện tới giờ ({sp.name}, cập nhật đến arc {story_arc(novel)})")
    print(read_text(sp).split("-->", 1)[-1].strip() if sp.exists() else "  (chưa có)")
    prev_arcs = [a for a in arc_list if a["no"] < cur["no"]][-2:]
    if prev_arcs:
        print("\n### Tóm tắt arc trước")
    for a in prev_arcs:
        p = arc_file(novel, a)
        text = arc_summary_text(read_text(p)) if p.exists() else ""
        print(f"{arc_label(a)}\n  {text or '(THIẾU tóm tắt arc — orchestrator chạy arc-summary)'}")
    status = {r["idx"]: r["trạng thái"] for r in rows}
    translated = [i for i in sorted(status) if i < idx and status[i] in TRANSLATED]
    prev = sorted({i for i in translated if i >= cur["first"]} | set(translated[-3:]))
    print(f"\n### Arc hiện tại: {arc_label(cur)}")
    if not prev:
        print("  (chưa có chương nào đã dịch trước chương này)")
    for i, s in summaries(novel, prev):
        print(f"  #{i}: {s or '(THIẾU tóm tắt chương)'}")
    return prev


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
    lang = raw_lang(novel, text)
    size = f"{len(''.join(text.split()))} ký tự" if lang == "ja" else f"{len(text.split())} từ"

    print(f"# Chương #{idx}: {row['tiêu đề']}")
    print(f"Raw:      {raw.as_posix()}")
    print(f"Bản dịch: {vi_file(novel, idx).as_posix()}")
    print(f"Độ dài: {size}, {len(paras)} đoạn (đã bỏ tiêu đề, phân cách, ảnh, T/N)")
    raw_imgs = [l.strip() for l in read_text(raw).splitlines() if IMAGE_RE.match(l.strip())]
    if raw_imgs:
        print(f"Ảnh trong raw ({len(raw_imgs)}): {', '.join(raw_imgs)} — giữ nguyên dòng ảnh ở đúng vị trí tương ứng.")

    h = pov_hint(paras, lang)
    print(f"\n## Góc nhìn (ước lượng)\n{h['pov']} — {h['first_label']} ngoài thoại: {h['first']}, "
          f"{h['third_label']} ngoài thoại: {h['third']}; {h['dialogue']} đoạn thoại, "
          f"{h['system']} đoạn {h['system_label']}.")

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
    report(novel, paras, show_all=True, lang=lang)

    print("\n## Mạch truyện")
    if layout(novel) >= 2:
        prev = story_context(novel, rows, idx)
    else:
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
