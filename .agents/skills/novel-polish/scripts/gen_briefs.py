#!/usr/bin/env python3
"""Sinh brief cho một phase trau chuốt văn phong.

usage: gen_briefs.py <slug> <start> [--count 9] [--cycle 3]
       [--polish-model M] [--review-model M]

Ghi vào .herdr/tasks/: pl-NNN.md cho từng chương, plr-AAA-BBB.md cho từng vòng
(còn chừa __BASE__ để orchestrator điền), và orch-pl-AAA-BBB.md cho orchestrator.
In ra đường dẫn brief orchestrator.
"""
import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SKILL = Path(__file__).resolve().parents[1]

ap = argparse.ArgumentParser()
ap.add_argument('slug')
ap.add_argument('start', type=int)
ap.add_argument('--count', type=int, default=9)
ap.add_argument('--cycle', type=int, default=3)
ap.add_argument('--polish-model', default='gemini-3.8-flash-high')
ap.add_argument('--review-model', default='gemini-4-argon-medium')
a = ap.parse_args()

tdir = ROOT / 'translations' / a.slug
novel = json.loads((tdir / 'novel.json').read_text(encoding='utf-8'))
raw = novel['raw_dir']
existing = sorted(int(p.stem.split('_')[1]) for p in (tdir / 'vi').glob('Chapter_*.md'))
chapters = [n for n in range(a.start, a.start + a.count) if n in existing]
if not chapters:
    sys.exit(f'không có chương đã dịch nào trong khoảng {a.start}..{a.start + a.count - 1}')

root = ROOT.as_posix()
common = {'__ROOT__': root, '__SLUG__': a.slug, '__RAW__': raw}

def fill(tmpl, extra):
    s = (SKILL / 'briefs' / tmpl).read_text(encoding='utf-8')
    for k, v in {**common, **extra}.items():
        s = s.replace(k, str(v))
    return s

out = ROOT / '.herdr' / 'tasks'
out.mkdir(parents=True, exist_ok=True)
cycles = [chapters[i:i + a.cycle] for i in range(0, len(chapters), a.cycle)]
for n in chapters:
    (out / f'pl-{n:03d}.md').write_text(fill('polish.md', {'__NNN__': f'{n:03d}', '__N__': n}), encoding='utf-8')
for c in cycles:
    (out / f'plr-{c[0]:03d}-{c[-1]:03d}.md').write_text(
        fill('review.md', {'__A__': c[0], '__B__': c[-1]}), encoding='utf-8')

A, B = chapters[0], chapters[-1]
cyc = ', '.join(f'{c[0]}–{c[-1]}' for c in cycles)
orch = fill('orchestrator.md', {'__A__': A, '__B__': B, '__CYCLES__': cyc,
                                '__POLISH_MODEL__': a.polish_model, '__REVIEW_MODEL__': a.review_model})
f = out / f'orch-pl-{A:03d}-{B:03d}.md'
f.write_text(orch, encoding='utf-8')
print(f.relative_to(ROOT).as_posix())
