"""Trợ lý cho orchestrator dịch truyện. Trạng thái nằm hết trong progress.md (layout 2: thêm questions.md,
context/summaries/) nên chạy lại lúc nào cũng tiếp tục được.

    python orchestrate.py <slug> next [--until N] [--batch 3]
    python orchestrate.py <slug> brief <init|translate|review|fix|arc-summary> [--n N] [--range R] [--arc K]
                                       [--raw DIR --title T] [--review-report F] [--decisions F]
                                       [--keep-status]
    python orchestrate.py <slug> verify <range> [--status done|reviewed|translated]
    python orchestrate.py <slug> verify-arc <K>                                  # layout 2
    python orchestrate.py <slug> questions
    python orchestrate.py <slug> resolve "<đoạn chữ trong câu hỏi>" "<quyết định>" [--new]
    python orchestrate.py <slug> resolve --args-file <file> [--new]   # khi chuỗi có dấu "
"""
import argparse
import re
import sys
from pathlib import Path
from string import Template

SKILLS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SKILLS / "novel-translate" / "scripts"))

from common import (QUESTIONS_HEADER, ROOT, STORY_LIMIT, TRANSLATED, TRANSLATIONS, all_summaries, arc_file,  # noqa: E402
                    arc_label, arc_summary_text, arcs, decisions_path, die, entries, get_row, layout, load_novel,
                    load_progress, missing_arc_summaries, parse_range, progress_path, questions_path, read_text,
                    story_arc, utf8_stdout, vi_file)
from lint_context import lint  # noqa: E402
from qa_check import check  # noqa: E402

BRIEFS = Path(__file__).resolve().parents[1] / "briefs"
TASKS = ROOT / ".herdr" / "tasks"
OPEN_HEADER = "## Cần user xác nhận"
DONE_HEADER = "## Đã quyết"
# Dòng kết thúc bằng tên người quyết, vd "(orchestrator)", "(user)", là đã quyết dù không có "→"
DECIDER_RE = re.compile(r"\((orchestrator|user)[^)]*\)\s*$", re.IGNORECASE)


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


def _is_question(line):
    return line.lstrip().startswith("- ")


def _open_indices(lines):
    """Vị trí các câu hỏi mở: mọi dòng '- ' trong "Cần user xác nhận", cộng các dòng '- ' chưa có
    '→' trong "Đã quyết" (panel lỡ ghi câu hỏi mới xuống cuối file)."""
    out = []
    # Panel có thể lỡ tạo thêm một mục "Cần user xác nhận" ở cuối file: đọc mọi mục trùng tên.
    for start, line in enumerate(lines):
        if line.strip() != OPEN_HEADER:
            continue
        end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
        out += [i for i in range(start + 1, end) if _is_question(lines[i])]
    d_start, d_end = _section(lines, DONE_HEADER)
    if d_start is not None:
        out += [i for i in range(d_start + 1, d_end)
                if _is_question(lines[i]) and "→" not in lines[i] and not DECIDER_RE.search(lines[i])]
    return out


def _continuation(lines, i):
    """Các dòng thụt lề ngay sau câu hỏi ở dòng i (panel hay ghi câu hỏi kèm ý con '  1. ...')."""
    out = []
    j = i + 1
    while j < len(lines) and lines[j].strip() and lines[j][:1] in (" ", "\t"):
        out.append(j)
        j += 1
    return out


def _full_question(lines, i):
    return " ".join([lines[i].rstrip()] + [lines[j].strip() for j in _continuation(lines, i)])


def open_questions(novel):
    if layout(novel) >= 2:
        lines = _question_lines(novel)
        return [_full_question(lines, i) for i, l in enumerate(lines) if _is_question(l)]
    lines = read_text(progress_path(novel)).splitlines()
    return [_full_question(lines, i) for i in _open_indices(lines)]


def _question_lines(novel):
    p = questions_path(novel)
    return read_text(p).splitlines() if p.exists() else []


def resolve_v2(novel, needle, decision, new=False):
    """Layout 2: câu hỏi mở nằm trong questions.md, câu đã quyết ghi thêm vào decisions/<khoảng 100 chương>.md."""
    qpath = questions_path(novel)
    lines = _question_lines(novel)
    if new:
        item = needle if needle.lstrip().startswith("- ") else f"- {needle}"
    else:
        hits = [i for i, l in enumerate(lines) if _is_question(l) and needle in _full_question(lines, i)]
        if len(hits) != 1:
            listing = "".join(f"\n  {lines[i].strip()[:120]}" for i in hits)
            die(f"cần đúng 1 câu hỏi chứa '{needle}', thấy {len(hits)}. Dùng đoạn chữ dài hơn, chỉ có ở một câu."
                + (listing if hits else " Câu hỏi chỉ có trong báo cáo panel thì dùng --new"))
        item = _full_question(lines, hits[0])
        for j in reversed([hits[0], *_continuation(lines, hits[0])]):
            lines.pop(j)
        qpath.write_text("\n".join(lines or QUESTIONS_HEADER.splitlines()).rstrip("\n") + "\n", encoding="utf-8")
    item = re.sub(r"\s+—\s+đề xuất.*$", "", item)
    entry = f"{item} → {decision} (orchestrator)"
    dpath = decisions_path(novel, item)
    dpath.parent.mkdir(parents=True, exist_ok=True)
    old = read_text(dpath).rstrip("\n") if dpath.exists() else (
        f"# Đã quyết — {dpath.stem}\n\n<!-- Mỗi dòng: - [#chương] vấn đề → quyết định (người quyết). "
        f"Chỉ ghi thêm; tra bằng grep, không cần đọc trọn. -->\n")
    dpath.write_text(old + "\n" + entry + "\n", encoding="utf-8")
    print(f"đã chuyển sang decisions/{dpath.name}: {entry}")


def resolve(novel, needle, decision, new=False):
    """Chuyển câu hỏi mở có chứa `needle` sang "Đã quyết". new=True: `needle` là câu hỏi
    chỉ có trong báo cáo panel (không nằm trong "Cần user xác nhận"), ghi thẳng vào "Đã quyết"."""
    if layout(novel) >= 2:
        return resolve_v2(novel, needle, decision, new)
    path = progress_path(novel)
    lines = read_text(path).splitlines()
    if new:
        item = needle if needle.lstrip().startswith("- ") else f"- {needle}"
    else:
        hits = [i for i in _open_indices(lines) if needle in _full_question(lines, i)]
        if len(hits) != 1:
            listing = "".join(f"\n  {lines[i].strip()[:120]}" for i in hits)
            die(f"cần đúng 1 câu hỏi chứa '{needle}', thấy {len(hits)}. Dùng đoạn chữ dài hơn, chỉ có ở một câu."
                + (listing if hits else " Câu hỏi chỉ có trong báo cáo panel thì dùng --new"))
        item = _full_question(lines, hits[0])
        # xoá cả các dòng ý con đi kèm, từ dưới lên để không lệch chỉ số
        for j in reversed([hits[0], *_continuation(lines, hits[0])]):
            lines.pop(j)
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
        print("action=init open_questions=0")
        return
    novel = load_novel(slug)
    rows = load_progress(novel)
    q = len(open_questions(novel))
    # Chương đã dịch mà nay QA báo LỖI (vd sau khi sửa script QA) thì sửa trước khi làm tiếp.
    broken = [r["idx"] for r in rows if r["trạng thái"] in TRANSLATED and check(novel, r)[0]]
    if broken:
        print(f"action=repair range={fmt_range(broken)} open_questions={q}")
        return
    if lint(novel)[0]:
        print(f"action=fix-context open_questions={q}")
        return
    pending = [r["idx"] for r in rows if r["trạng thái"] == "done"]
    todo = [r["idx"] for r in rows if r["trạng thái"] == "todo" and (until is None or r["idx"] <= until)]
    # Layout 2: arc đã dịch xong mà thiếu tóm tắt arc / story-so-far thì viết trước khi sang arc mới.
    missing = missing_arc_summaries(novel, rows)
    if len(pending) >= batch:
        print(f"action=review range={fmt_range(pending[:batch])} open_questions={q}")
    elif missing:
        a = missing[0]
        print(f"action=arc-summary arc={a['no']} range={a['first']}-{a['last']} open_questions={q}")
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
    elif args.kind == "arc-summary":
        if args.arc is None:
            die("brief arc-summary cần --arc")
        novel = load_novel(slug)
        a = next((x for x in arcs(novel, load_progress(novel)) if x["no"] == args.arc), None)
        if a is None:
            die(f"không có arc {args.arc}")
        name = f"as-{args.arc:03d}"
        values.update(arc=args.arc, label=arc_label(a), range=f"{a['first']}-{a['last']}",
                      arc_file=arc_file(novel, a).relative_to(ROOT).as_posix(), story_limit=STORY_LIMIT)
    else:
        if not args.range:
            die(f"brief {args.kind} cần --range")
        idxs = parse_range(args.range)
        name = f"{'rv' if args.kind == 'review' else 'fx'}-{idxs[0]:03d}-{idxs[-1]:03d}"
        values.update(range=args.range)
        if args.kind == "fix":
            if not args.decisions:
                die("brief fix cần --decisions")
            # Layout 2: chép nguyên file quyết định vào brief, vì panel sửa hay bỏ qua bước đọc file này
            # và sửa thẳng theo báo cáo review (kể cả mục đã bị bác).
            dtext = ""
            dpath = Path(args.decisions) if Path(args.decisions).is_absolute() else ROOT / args.decisions
            if layout(load_novel(slug)) >= 2 and dpath.exists():
                dtext = ("\nNội dung file quyết định (chép nguyên văn, làm theo đúng file này):\n\n"
                         + read_text(dpath).strip() + "\n")
            values.update(decisions=args.decisions, decisions_text=dtext,
                          review_report=args.review_report or "(không có — chỉ sửa theo file quyết định)",
                          status_rule=("Giữ nguyên trạng thái các chương trong `progress.md`, không đặt `reviewed`."
                                       if args.keep_status else
                                       "Các chương $range trong `progress.md` là `reviewed`.".replace("$range", args.range)))
    text = Template(read_text(BRIEFS / f"{args.kind}.md")).substitute(values)
    TASKS.mkdir(parents=True, exist_ok=True)
    task = TASKS / f"{name}.md"
    task.write_text(text, encoding="utf-8")
    print(f"name={name} task={task.relative_to(ROOT).as_posix()} report=.herdr/reports/{name}.md")


# ---------- verify ----------

def cmd_verify(slug, spec, status):
    novel = load_novel(slug)
    rows = load_progress(novel)
    v2 = layout(novel) >= 2
    summaries = all_summaries(novel) if v2 else read_text(novel["context"] / "summaries.md")
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
        if row["trạng thái"] != status and not (status == "translated" and row["trạng thái"] in TRANSLATED):
            issues.append(f"trạng thái là '{row['trạng thái']}', cần '{status}'")
        if v2 and idx not in summaries:
            issues.append("thiếu tóm tắt chương trong context/summaries/ (ctx.py add-summary)")
        elif not v2 and not re.search(rf"(?m)^## +#?{idx}\b", summaries):
            issues.append("summaries.md thiếu mục tóm tắt")
        problems += len(issues)
        print(f"#{idx}: {'OK' if not issues else 'CHƯA ĐẠT'}")
        for i in issues:
            print(f"  - {i}")
    sys.exit(1 if problems else 0)


def cmd_verify_arc(slug, no):
    """Layout 2: arc `no` đã có tóm tắt arc, story-so-far.md đã cập nhật tới arc đó, và mọi chương đã dịch
    của arc có tóm tắt chương."""
    novel = load_novel(slug)
    rows = load_progress(novel)
    a = next((x for x in arcs(novel, rows) if x["no"] == no), None)
    if a is None:
        die(f"không có arc {no}")
    issues = []
    p = arc_file(novel, a)
    if not (p.exists() and arc_summary_text(read_text(p))):
        issues.append(f"{p.name} chưa có mục '## Tóm tắt arc' (ctx.py set-arc-summary {no})")
    if story_arc(novel) < no:
        issues.append(f"story-so-far.md mới cập nhật đến arc {story_arc(novel)} (ctx.py set-story {no})")
    have = all_summaries(novel)
    status = {r["idx"]: r["trạng thái"] for r in rows}
    lack = [i for i in a["idxs"] if status[i] in TRANSLATED and i not in have]
    if lack:
        issues.append(f"thiếu tóm tắt chương: {fmt_range(lack)}")
    print(f"{arc_label(a)}: {'OK' if not issues else 'CHƯA ĐẠT'}")
    for i in issues:
        print(f"  - {i}")
    sys.exit(1 if issues else 0)


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("next")
    p.add_argument("--until", type=int, help="không dịch chương có # lớn hơn N")
    p.add_argument("--batch", type=int, default=3, help="số chương mỗi lần review")
    p = sub.add_parser("brief")
    p.add_argument("kind", choices=["init", "translate", "review", "fix", "arc-summary"])
    p.add_argument("--n", type=int)
    p.add_argument("--arc", type=int)
    p.add_argument("--range")
    p.add_argument("--raw")
    p.add_argument("--title")
    p.add_argument("--review-report")
    p.add_argument("--decisions")
    p.add_argument("--keep-status", action="store_true",
                   help="fix chỉ để áp dụng quyết định cho chương cũ: không đổi trạng thái sang reviewed")
    p = sub.add_parser("verify")
    p.add_argument("range")
    p.add_argument("--status", default="done", choices=["done", "reviewed", "translated"],
                   help="translated = done hoặc reviewed")
    p = sub.add_parser("verify-arc")
    p.add_argument("arc", type=int)
    sub.add_parser("questions")
    p = sub.add_parser("resolve")
    p.add_argument("needle", nargs="?")
    p.add_argument("decision", nargs="?")
    p.add_argument("--args-file", help="file UTF-8: dòng 1 là câu hỏi, các dòng sau là quyết định")
    p.add_argument("--new", action="store_true", help="câu hỏi chỉ có trong báo cáo panel, ghi thẳng vào 'Đã quyết'")
    args = ap.parse_args()

    if args.cmd == "next":
        cmd_next(args.slug, args.until, args.batch)
    elif args.cmd == "brief":
        cmd_brief(args.slug, args)
    elif args.cmd == "verify":
        cmd_verify(args.slug, args.range, args.status)
    elif args.cmd == "verify-arc":
        cmd_verify_arc(args.slug, args.arc)
    elif args.cmd == "questions":
        qs = open_questions(load_novel(args.slug))
        print("\n".join(qs) if qs else "(không có câu hỏi mở)")
    elif args.cmd == "resolve":
        needle, decision = args.needle, args.decision
        if args.args_file:
            # PowerShell 5.1 làm hỏng dấu " trong tham số: đọc từ file (dòng 1 = câu hỏi, phần còn lại = quyết định)
            lines = read_text(args.args_file).strip().splitlines()
            if len(lines) < 2:
                die("--args-file cần ít nhất 2 dòng: câu hỏi, rồi quyết định")
            needle, decision = lines[0].strip(), " ".join(l.strip() for l in lines[1:])
        if not (needle and decision):
            die("resolve cần <câu hỏi> <quyết định> hoặc --args-file")
        resolve(load_novel(args.slug), needle, decision, args.new)


if __name__ == "__main__":
    main()
