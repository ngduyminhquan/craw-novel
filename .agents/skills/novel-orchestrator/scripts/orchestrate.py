"""Trợ lý cho orchestrator dịch truyện. Trạng thái nằm hết trong progress.md nên chạy lại lúc nào cũng tiếp tục được.

    python orchestrate.py <slug> next [--until N] [--batch 3]
    python orchestrate.py <slug> brief <init|translate|review|fix> [--n N] [--range R]
                                       [--raw DIR --title T] [--review-report F] [--decisions F]
    python orchestrate.py <slug> verify <range> [--status done|reviewed]
    python orchestrate.py <slug> questions
    python orchestrate.py <slug> resolve "<đoạn chữ trong câu hỏi>" "<quyết định>"
"""
import argparse
import re
import sys
from pathlib import Path
from string import Template

SKILLS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SKILLS / "novel-translate" / "scripts"))

from common import (ROOT, TRANSLATIONS, die, entries, get_row, load_novel, load_progress, parse_range,  # noqa: E402
                    progress_path, read_text, utf8_stdout, vi_file)
from qa_check import check  # noqa: E402

BRIEFS = Path(__file__).resolve().parents[1] / "briefs"
TASKS = ROOT / ".herdr" / "tasks"
OPEN_HEADER = "## Cần user xác nhận"
DONE_HEADER = "## Đã quyết"


def fmt_range(idxs):
    """[1,2,3,5] -> '1-3,5'"""
    parts, start = [], None
    for i, v in enumerate(idxs):
        if start is None:
            start = v
        if i + 1 == len(idxs) or idxs[i + 1] != v + 1:
            parts.append(str(start) if start == v else f"{start}-{v}")
            start = None
    return ",".join(parts)


def initialized(slug):
    """Đã chạy init_novel.py VÀ đã dựng context (characters.md có ít nhất một nhân vật)."""
    d = TRANSLATIONS / slug
    return (d / "novel.json").exists() and bool(entries(d / "context" / "characters.md"))


# ---------- câu hỏi mở ----------

def _section(lines, header):
    start = next((i for i, l in enumerate(lines) if l.strip() == header), None)
    if start is None:
        return None, None
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return start, end


def open_questions(novel):
    lines = read_text(progress_path(novel)).splitlines()
    start, end = _section(lines, OPEN_HEADER)
    if start is None:
        return []
    return [l for l in lines[start + 1:end] if l.lstrip().startswith("- ")]


def resolve(novel, needle, decision):
    path = progress_path(novel)
    lines = read_text(path).splitlines()
    start, end = _section(lines, OPEN_HEADER)
    if start is None:
        die(f"progress.md không có mục '{OPEN_HEADER}'")
    hits = [i for i in range(start + 1, end) if lines[i].lstrip().startswith("- ") and needle in lines[i]]
    if len(hits) != 1:
        die(f"cần đúng 1 câu hỏi chứa '{needle}', thấy {len(hits)}")
    item = lines.pop(hits[0]).rstrip()
    item = re.sub(r"\s+—\s+đề xuất.*$", "", item)
    entry = f"{item} → {decision} (orchestrator)"
    d_start, d_end = _section(lines, DONE_HEADER)
    if d_start is None:
        lines += ["", DONE_HEADER, "", entry]
    else:
        lines.insert(d_end if lines[d_end - 1].strip() else d_end - 1, entry)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"đã chuyển sang '{DONE_HEADER}': {entry}")


# ---------- next ----------

def cmd_next(slug, until, batch):
    if not initialized(slug):
        print("action=init")
        return
    novel = load_novel(slug)
    rows = load_progress(novel)
    q = len(open_questions(novel))
    pending = [r["idx"] for r in rows if r["trạng thái"] == "done"]
    todo = [r["idx"] for r in rows if r["trạng thái"] == "todo" and (until is None or r["idx"] <= until)]
    if len(pending) >= batch:
        print(f"action=review range={fmt_range(pending[:batch])} open_questions={q}")
    elif todo:
        print(f"action=translate n={todo[0]} open_questions={q}")
    elif pending:
        print(f"action=review range={fmt_range(pending)} open_questions={q}")
    else:
        print(f"action=finished open_questions={q}")


# ---------- brief ----------

def cmd_brief(slug, args):
    values = {"slug": slug, "root": ROOT.as_posix()}
    if args.kind == "init":
        if not (args.raw and args.title):
            die("brief init cần --raw và --title")
        name = "tl-init"
        values.update(raw=args.raw, title=args.title)
    elif args.kind == "translate":
        if args.n is None:
            die("brief translate cần --n")
        novel = load_novel(slug)
        row = get_row(load_progress(novel), args.n)
        name = f"tl-{args.n:03d}"
        values.update(n=args.n, title=row["tiêu đề"], vi=vi_file(novel, args.n).relative_to(ROOT).as_posix())
    else:
        if not args.range:
            die(f"brief {args.kind} cần --range")
        idxs = parse_range(args.range)
        name = f"{'rv' if args.kind == 'review' else 'fx'}-{idxs[0]:03d}-{idxs[-1]:03d}"
        values.update(range=args.range)
        if args.kind == "fix":
            if not args.decisions:
                die("brief fix cần --decisions")
            values.update(decisions=args.decisions,
                          review_report=args.review_report or "(không có — chỉ sửa theo file quyết định)")
    text = Template(read_text(BRIEFS / f"{args.kind}.md")).substitute(values)
    TASKS.mkdir(parents=True, exist_ok=True)
    task = TASKS / f"{name}.md"
    task.write_text(text, encoding="utf-8")
    print(f"name={name} task={task.relative_to(ROOT).as_posix()} report=.herdr/reports/{name}.md")


# ---------- verify ----------

def cmd_verify(slug, spec, status):
    novel = load_novel(slug)
    rows = load_progress(novel)
    summaries = read_text(novel["context"] / "summaries.md")
    problems = 0
    for idx in parse_range(spec):
        row = get_row(rows, idx)
        if row["trạng thái"] == "skip":
            continue
        issues = []
        if not vi_file(novel, idx).exists():
            issues.append("thiếu file bản dịch")
        else:
            errors, _ = check(novel, row)
            issues += [f"QA: {e}" for e in errors]
        if row["trạng thái"] != status:
            issues.append(f"trạng thái là '{row['trạng thái']}', cần '{status}'")
        if not re.search(rf"(?m)^## +#?{idx}\b", summaries):
            issues.append("summaries.md thiếu mục tóm tắt")
        problems += len(issues)
        print(f"#{idx}: {'OK' if not issues else 'CHƯA ĐẠT'}")
        for i in issues:
            print(f"  - {i}")
    sys.exit(1 if problems else 0)


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("next")
    p.add_argument("--until", type=int, help="không dịch chương có # lớn hơn N")
    p.add_argument("--batch", type=int, default=3, help="số chương mỗi lần review")
    p = sub.add_parser("brief")
    p.add_argument("kind", choices=["init", "translate", "review", "fix"])
    p.add_argument("--n", type=int)
    p.add_argument("--range")
    p.add_argument("--raw")
    p.add_argument("--title")
    p.add_argument("--review-report")
    p.add_argument("--decisions")
    p = sub.add_parser("verify")
    p.add_argument("range")
    p.add_argument("--status", default="done", choices=["done", "reviewed"])
    sub.add_parser("questions")
    p = sub.add_parser("resolve")
    p.add_argument("needle")
    p.add_argument("decision")
    args = ap.parse_args()

    if args.cmd == "next":
        cmd_next(args.slug, args.until, args.batch)
    elif args.cmd == "brief":
        cmd_brief(args.slug, args)
    elif args.cmd == "verify":
        cmd_verify(args.slug, args.range, args.status)
    elif args.cmd == "questions":
        qs = open_questions(load_novel(args.slug))
        print("\n".join(qs) if qs else "(không có câu hỏi mở)")
    elif args.cmd == "resolve":
        resolve(load_novel(args.slug), args.needle, args.decision)


if __name__ == "__main__":
    main()
