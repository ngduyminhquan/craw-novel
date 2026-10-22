"""Đọc/ghi progress.md.

    python progress.py <slug> next [-n N]            # N chương todo kế tiếp (mặc định 1)
    python progress.py <slug> set <range> <status> [--note "..."]
    python progress.py <slug> stats
"""
import argparse

from common import STATUSES, die, get_row, load_novel, load_progress, parse_range, save_progress, utf8_stdout


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_next = sub.add_parser("next")
    p_next.add_argument("-n", type=int, default=1)
    p_set = sub.add_parser("set")
    p_set.add_argument("range", help="vd 5 hoặc 1-10 hoặc 1,3,5-7")
    p_set.add_argument("status", choices=STATUSES)
    p_set.add_argument("--note")
    sub.add_parser("stats")
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


if __name__ == "__main__":
    main()
