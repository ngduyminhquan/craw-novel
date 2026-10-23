"""Soát các file context.

    python lint_context.py <slug>

LỖI (exit 1):
  - một tên/thuật ngữ EN (kể cả alias) khai báo ở nhiều dòng trong glossary.md + characters.md
  - tên trong pronouns.md không khớp cột EN của characters.md
  - chương đã dịch mà summaries.md thiếu mục tóm tắt
Cảnh báo:
  - kỹ năng/danh hiệu/chức nghiệp để nguyên tiếng Anh mà Ghi chú không nói "giữ nguyên"
  - VI có nhiều biến thể ngăn bằng '/' (chỉ chấp nhận khi Ghi chú nói rõ dùng biến thể nào trong ngữ cảnh nào)
"""
import argparse
import re
import sys
from collections import defaultdict

from common import TRANSLATED, entries, load_novel, load_progress, read_text, table_with, utf8_stdout

# Loại thuật ngữ mà rules.md yêu cầu dịch Hán Việt
MUST_TRANSLATE = ("kỹ năng", "danh hiệu", "chức nghiệp", "cấp bậc")
KINDS = {"kỹ năng", "danh hiệu", "chức nghiệp", "cấp bậc", "vật phẩm", "địa danh", "tổ chức",
         "chủng tộc", "quái vật", "hệ thống", "khác"}


def lint(novel):
    ctx = novel["context"]
    errors, warns = [], []

    seen = defaultdict(list)
    for fname in ("glossary.md", "characters.md"):
        for e in entries(ctx / fname):
            for t in {e["en"].lower(), *(a.lower() for a in e["aliases"])}:
                seen[t].append(f"{fname}:{e['en']}")
    for term, where in sorted(seen.items()):
        if len(where) > 1:
            errors.append(f"'{term}' khai báo ở {len(where)} dòng: {', '.join(where)} — gộp về một dòng")

    names = {e["en"].lower() for e in entries(ctx / "characters.md")}
    for r in table_with(ctx / "pronouns.md", "a"):
        for k in ("a", "b"):
            v = r.get(k, "").strip()
            if v and v != "*" and v.lower() not in names:
                errors.append(f"pronouns.md: '{v}' không có trong cột EN của characters.md")
    for r in table_with(ctx / "pronouns.md", "nhân vật"):
        v = r.get("nhân vật", "").strip()
        if v and v.lower() not in names:
            errors.append(f"pronouns.md (người kể): '{v}' không có trong cột EN của characters.md")

    summaries = read_text(ctx / "summaries.md")
    for row in load_progress(novel):
        if row["trạng thái"] in TRANSLATED and not re.search(rf"(?m)^## +#?{row['idx']}\b", summaries):
            errors.append(f"summaries.md thiếu mục '## {row['idx']}'")

    for e in entries(ctx / "glossary.md"):
        note = e["row"].get("ghi chú", "").strip()
        if "/" in e["vi"] and not note:
            warns.append(f"glossary: '{e['en']}' có nhiều bản dịch '{e['vi']}' mà không ghi khi nào dùng bản nào")
        kind = e["row"].get("loại", "").strip().lower()
        if kind not in KINDS:
            warns.append(f"glossary: '{e['en']}' có Loại '{kind}' không hợp lệ — dùng một trong: "
                         f"{', '.join(sorted(KINDS))}")
        if (e["vi"].lower() == e["en"].lower() and any(k in kind for k in MUST_TRANSLATE)
                and "giữ nguyên" not in note.lower()):
            warns.append(f"glossary: '{e['en']}' ({kind}) để nguyên tiếng Anh — rules.md yêu cầu dịch Hán Việt, "
                         "hoặc ghi 'giữ nguyên' kèm lý do vào Ghi chú")
    return errors, warns


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    args = ap.parse_args()
    errors, warns = lint(load_novel(args.slug))
    for m in errors:
        print(f"[LỖI] {m}")
    for m in warns:
        print(f"[cảnh báo] {m}")
    if not errors and not warns:
        print("OK")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
