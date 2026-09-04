#!/usr/bin/env python3
"""Fix frontmatter language/last_updated across the knowledge base."""
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SKIP_DIRS = {'.git', '.trae', '.qoder', '.claude', 'node_modules', '.github'}
TODAY = '2026-09-03'

FM_RE = re.compile(r'\A---\n(.*?)\n---\n', re.DOTALL)
CJK_RE = re.compile(r'[一-鿿]')


def git_last_date(path):
    try:
        out = subprocess.run(
            ['git', 'log', '-1', '--format=%ad', '--date=short', '--', str(path)],
            cwd=REPO_ROOT, capture_output=True, text=True).stdout.strip()
        return out or None
    except Exception:
        return None


changed = 0
for md in sorted(REPO_ROOT.rglob('*.md')):
    rel = md.relative_to(REPO_ROOT)
    if any(part in SKIP_DIRS for part in rel.parts):
        continue
    text = md.read_text(encoding='utf-8')
    m = FM_RE.match(text)
    if not m:
        continue
    fm, body = m.group(1), text[m.end():]
    orig_fm = fm

    # a) language vs body CJK ratio
    cjk = len(CJK_RE.findall(body))
    alpha = len(re.findall(r'[A-Za-z]', body))
    is_zh = cjk > 0 and cjk / max(cjk + alpha, 1) > 0.2
    want = 'zh-CN' if is_zh else 'en-US'
    fm = re.sub(r'^(language:\s*)"[^"]*"',
                lambda mm: f'{mm.group(1)}"{want}"' if want in ('zh-CN', 'en-US') else mm.group(0),
                fm, flags=re.M)

    # b) last_updated from git
    date = git_last_date(rel) or TODAY
    if re.search(r'^last_updated:', fm, flags=re.M):
        fm = re.sub(r'^last_updated:.*$', f'last_updated: "{date}"', fm, flags=re.M)

    if fm != orig_fm:
        md.write_text(text[:m.start(1)] + fm + text[m.end(1):], encoding='utf-8')
        changed += 1

print(f'updated {changed} files')
