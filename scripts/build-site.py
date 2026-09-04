#!/usr/bin/env python3
"""
O-RAN Knowledge Base Static Site Builder
=========================================
Converts all markdown files in the repository to a static HTML site in dist/,
preserving the directory structure. Uses pandoc for markdown -> HTML.

Mapping rules:
    readme.md      -> index.html        (per directory; case-insensitive)
    readme-zh.md   -> readme-zh.html
    x.md           -> x.html
    README.md      -> dist/index.html   (site home)

Usage:
    python scripts/build-site.py            # full build into dist/
    python scripts/build-site.py --clean    # remove dist/ first

Exit codes:
    0 - Build succeeded
    1 - Build completed with warnings
    2 - Build failed
"""

import os
import re
import shutil
import subprocess
import sys
import argparse
from pathlib import Path

# Configuration
REPO_ROOT = Path(__file__).parent.parent
DIST_DIR = REPO_ROOT / 'dist'
SKIP_DIRS = {'.git', '.trae', '.qoder', '.claude', '.github', 'node_modules', 'dist'}
SKIP_FILES = {'.env'}
ASSET_EXTS = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.ico',
              '.pdf', '.css', '.js', '.woff', '.woff2', '.ttf', '.eot'}
PANDOC = shutil.which('pandoc') or '/opt/homebrew/bin/pandoc'

CSS = """
body { max-width: 860px; margin: 0 auto; padding: 2rem 1.2rem; color: #24292f;
       font-family: -apple-system, "Segoe UI", "PingFang SC", "Hiragino Sans GB",
                    "Microsoft YaHei", sans-serif; line-height: 1.7; }
h1, h2, h3, h4 { line-height: 1.3; margin-top: 1.6em; }
h1 { border-bottom: 2px solid #eaecef; padding-bottom: .3em; }
a { color: #0969da; text-decoration: none; }
a:hover { text-decoration: underline; }
code { background: #eff1f3; padding: .15em .4em; border-radius: 4px; font-size: .92em; }
pre { background: #f6f8fa; padding: 1em; border-radius: 6px; overflow-x: auto; }
pre code { background: none; padding: 0; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; }
th, td { border: 1px solid #d0d7de; padding: .45em .8em; text-align: left; }
th { background: #f6f8fa; }
tr:nth-child(even) { background: #fafbfc; }
blockquote { margin: 0; padding: 0 1em; color: #57606a; border-left: 4px solid #d0d7de; }
img { max-width: 100%; }
footer { margin-top: 3em; padding-top: 1em; border-top: 1px solid #eaecef;
         font-size: .9em; color: #57606a; }
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>{css}</style>
</head>
<body>
<article>
{body}
</article>
<footer><a href="{home}">&#8617; 返回首页 / Back to Home</a></footer>
</body>
</html>
"""


def is_readme(name):
    return name.lower() in ('readme.md', 'readme-zh.md')


def md_to_html_rel(md_rel):
    """Map a markdown path (relative to repo root) to its HTML output path."""
    name = md_rel.name.lower()
    parent = md_rel.parent
    if name == 'readme.md':
        return parent / 'index.html'
    if name == 'readme-zh.md':
        return parent / 'readme-zh.html'
    return parent / (md_rel.stem + '.html')


def strip_frontmatter(text):
    """Remove a leading YAML frontmatter block (--- ... ---)."""
    if text.startswith('---'):
        m = re.match(r'^---\s*\n.*?\n---\s*\n', text, re.DOTALL)
        if m:
            return text[m.end():]
    return text


def extract_title(body, fallback):
    m = re.search(r'^#\s+(.+)$', body, re.MULTILINE)
    if m:
        return re.sub(r'[#*`]', '', m.group(1)).strip()
    return fallback


def rewrite_href(href, md_rel):
    """Rewrite a single href value for the static site."""
    if re.match(r'^(?:https?:)?//', href) or href.startswith(('mailto:', 'tel:', 'javascript:')):
        return href
    # Split anchor / query
    anchor = ''
    m = re.match(r'^([^#?]*)([#?].*)?$', href)
    path_part, tail = m.group(1), m.group(2) or ''
    if not path_part:
        return href  # pure anchor
    if path_part.startswith('/'):
        return href  # absolute path, leave as-is

    target = (md_rel.parent / path_part).as_posix()
    # Normalize ../ segments
    parts = []
    for seg in target.split('/'):
        if seg == '..':
            if parts:
                parts.pop()
        elif seg not in ('', '.'):
            parts.append(seg)
    norm = '/'.join(parts)

    if path_part.lower().endswith('.md'):
        base = norm.rsplit('/', 1)[-1].lower()
        if base == 'readme.md':
            new = norm.rsplit('/', 1)[0] + '/index.html' if '/' in norm else 'index.html'
        elif base == 'readme-zh.md':
            new = norm.rsplit('/', 1)[0] + '/readme-zh.html' if '/' in norm else 'readme-zh.html'
        else:
            new = norm[:-3] + '.html'
        # Make relative to the current file's output directory
        cur_dir = md_to_html_rel(md_rel).parent.as_posix()
        rel = os.path.relpath(new, cur_dir if cur_dir != '.' else '.')
        return rel.replace(os.sep, '/') + tail

    # Directory link: if it resolves to an existing dir (or has a readme), append index.html
    if not os.path.splitext(norm)[1]:
        cand = REPO_ROOT / norm
        if cand.is_dir():
            new = norm + '/index.html'
            cur_dir = md_to_html_rel(md_rel).parent.as_posix()
            rel = os.path.relpath(new, cur_dir if cur_dir != '.' else '.')
            return rel.replace(os.sep, '/') + tail
    return href


def rewrite_links(html, md_rel):
    return re.sub(
        r'href="([^"]+)"',
        lambda m: 'href="%s"' % rewrite_href(m.group(1), md_rel),
        html,
    )


def pandoc_fragment(text):
    proc = subprocess.run(
        [PANDOC, '-f', 'gfm', '-t', 'html5', '--wrap=none'],
        input=text, capture_output=True, text=True, encoding='utf-8',
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip()[:300])
    return proc.stdout


def build(clean=False):
    if not Path(PANDOC).exists() and not shutil.which('pandoc'):
        print('  ❌ pandoc not found')
        sys.exit(2)
    if clean and DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(exist_ok=True)

    md_files, assets = [], []
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith('.git')]
        for f in filenames:
            if f in SKIP_FILES or f.startswith('.'):
                continue
            p = Path(dirpath) / f
            ext = p.suffix.lower()
            if ext == '.md':
                md_files.append(p)
            elif ext in ASSET_EXTS:
                assets.append(p)

    built, warnings = 0, []

    for md in sorted(md_files):
        rel = md.relative_to(REPO_ROOT)
        out_rel = md_to_html_rel(rel)
        out_path = DIST_DIR / out_rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            raw = md.read_text(encoding='utf-8')
            body_md = strip_frontmatter(raw)
            title = extract_title(body_md, md.stem)
            fragment = pandoc_fragment(body_md)
            fragment = rewrite_links(fragment, rel)
            home = os.path.relpath('index.html', out_rel.parent.as_posix() if out_rel.parent.as_posix() != '.' else '.')
            lang = 'zh-CN' if 'zh' in md.stem.lower() else 'en'
            html = HTML_TEMPLATE.format(title=title, css=CSS, body=fragment,
                                        home=home.replace(os.sep, '/'), lang=lang)
            out_path.write_text(html, encoding='utf-8')
            built += 1
        except Exception as e:
            warnings.append(f'{rel}: {e}')

    # Directory index pages for folders without a readme
    listing_count = 0
    for dirpath, dirnames, filenames in os.walk(DIST_DIR):
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        htmls = sorted(f for f in filenames if f.endswith('.html'))
        if htmls and 'index.html' not in htmls:
            rel_dir = Path(dirpath).relative_to(DIST_DIR)
            items = []
            for d in sorted(dirnames):
                items.append(f'<li>📁 <a href="{d}/index.html">{d}/</a></li>')
            for f in htmls:
                label = f[:-5]
                items.append(f'<li>📄 <a href="{f}">{label}</a></li>')
            home = os.path.relpath(DIST_DIR / 'index.html', dirpath).replace(os.sep, '/')
            body = f'<h1>{rel_dir}</h1>\n<ul>\n' + '\n'.join(items) + '\n</ul>'
            html = HTML_TEMPLATE.format(title=str(rel_dir), css=CSS, body=body,
                                        home=home, lang='en')
            (Path(dirpath) / 'index.html').write_text(html, encoding='utf-8')
            listing_count += 1

    # Copy assets
    copied = 0
    for a in assets:
        rel = a.relative_to(REPO_ROOT)
        dest = DIST_DIR / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(a, dest)
        copied += 1

    print(f"\n  ✅ Built {built} pages (+{listing_count} directory indexes)")
    print(f"  📎 Copied {copied} assets")
    print(f"  📂 Output: {DIST_DIR}")
    if (DIST_DIR / 'index.html').exists():
        print("  ✅ dist/index.html exists")
    else:
        print("  ❌ dist/index.html MISSING")
        sys.exit(2)
    if warnings:
        print(f"\n  ⚠️  {len(warnings)} warnings:")
        for w in warnings[:20]:
            print(f"    - {w}")
        sys.exit(1)
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description='Build O-RAN Knowledge Base static site')
    parser.add_argument('--clean', action='store_true', help='Remove dist/ before building')
    args = parser.parse_args()
    print("\n🏗️  O-RAN Knowledge Base Site Builder")
    build(clean=args.clean)


if __name__ == '__main__':
    main()
