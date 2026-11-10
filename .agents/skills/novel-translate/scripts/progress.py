"""Đọc/ghi progress.md.

    python progress.py <slug> next [-n N]            # N chương todo kế tiếp (mặc định 1)
    python progress.py <slug> set <range> <status> [--note "..."]
    python progress.py <slug> stats
    python progress.py <slug> ask N "<câu hỏi — đề xuất>" [--file F]   # chỉ layout 2: ghi câu hỏi vào questions.md
"""
import argparse

from common import (QUESTIONS_HEADER, ArgParser, STATUSES, die, get_row, layout, load_novel, load_progress, parse_range,
                    questions_path, read_text, save_progress, utf8_stdout)


def main():
    utf8_stdout()
    ap = ArgParser()
    ap.add_argument("slug")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_next = sub.add_parser("next")
    p_next.add_argument("-n", type=int, default=1)
    p_set = sub.add_parser("set")
    p_set.add_argument("range", help="vd 5 hoặc 1-10 hoặc 1,3,5-7")
    p_set.add_argument("status", choices=STATUSES)
    p_set.add_argument("--note")
    sub.add_parser("stats")
    p_ask = sub.add_parser("ask")
    p_ask.add_argument("idx", type=int)
    p_ask.add_argument("text", nargs="?")
    p_ask.add_argument("--file", help="file UTF-8 chứa câu hỏi (tránh lỗi dấu \" của PowerShell)")
    args = ap.parse_args()

    novel = load_novel(args.slug)
    rows = load_progress(novel)

    if args.cmd == "next":
        todo = [r for r in rows if r["trạng thái"] == "todo"][: args.n]
        if not todo:
            print("Hết chương todo.")
        for r in todo:
            print(f"#{r['idx']}\t{r['file raw']}")
    elif args.cmd == "set":
        for idx in parse_range(args.range):
            r = get_row(rows, idx)
            r["trạng thái"] = args.status
            if args.note is not None:
                r["ghi chú"] = args.note.replace("|", "/")
        save_progress(novel, rows)
        print(f"Đã đặt {args.range} -> {args.status}")
    elif args.cmd == "stats":
        counts = {s: sum(r["trạng thái"] == s for r in rows) for s in STATUSES}
        other = len(rows) - sum(counts.values())
        if other:
            die(f"{other} dòng có trạng thái lạ, sửa progress.md")
        total = len(rows) - counts["skip"]
        translated = counts["done"] + counts["reviewed"]
        pct = 100 * translated / total if total else 0
        print(f"đã dịch {translated}/{total} ({pct:.1f}%) · reviewed {counts['reviewed']} · chờ review {counts['done']} · "
              f"todo {counts['todo']} · skip {counts['skip']}")
    elif args.cmd == "ask":
        ask(novel, rows, args)


def ask(novel, rows, args):
    if layout(novel) < 2:
        die("lệnh ask chỉ dùng cho truyện layout 2; truyện layout 1 ghi vào '## Cần user xác nhận' trong progress.md")
    get_row(rows, args.idx)
    text = read_text(args.file) if args.file else (args.text or "")
    text = " ".join(text.split())
    if not text:
        die("thiếu nội dung câu hỏi")
    path = questions_path(novel)
    lines = read_text(path).rstrip("\n").splitlines() if path.exists() else QUESTIONS_HEADER.rstrip("\n").splitlines()
    item = f"- [#{args.idx}] {text}"
    if item in lines:
        die("câu hỏi này đã có trong questions.md")
    lines.append(item)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"questions.md + {item}")


if __name__ == "__main__":
    main()

