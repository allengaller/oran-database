#!/usr/bin/env python3
"""
O-RAN Knowledge Base Structure Validator
=========================================
Validates the O-RAN knowledge base for structural integrity, link health,
bilingual pairing, numbering consistency, empty directories, and frontmatter.

Usage:
    python scripts/validate.py              # Run all checks
    python scripts/validate.py --check=links    # Links only
    python scripts/validate.py --check=dirs     # Empty dirs only
    python scripts/validate.py --check=bilingual # Bilingual pairing only

Exit codes:
    0 - All checks passed
    1 - Warnings found (non-critical)
    2 - Errors found (critical)
"""

import os
import re
import sys
import argparse
from pathlib import Path
from collections import defaultdict

# Configuration
REPO_ROOT = Path(__file__).parent.parent
SKIP_DIRS = {'.git', '.trae', '.qoder', '.claude', 'node_modules', '.github'}
MARKDOWN_EXT = {'.md'}
REQUIRED_FRONTMATTER_FIELDS = {'title', 'category', 'updated'}

class ValidationResult:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
    
    def error(self, msg):
        self.errors.append(f"  ❌ {msg}")
    
    def warning(self, msg):
        self.warnings.append(f"  ⚠️  {msg}")
    
    def ok(self, msg):
        self.info.append(f"  ✅ {msg}")
    
    def report(self, title):
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
        for i in self.info:
            print(i)
        for w in self.warnings:
            print(w)
        for e in self.errors:
            print(e)
        if not self.warnings and not self.errors:
            print("  ✅ All checks passed.")
        print()

def should_skip(path):
    parts = Path(path).parts
    return any(p in SKIP_DIRS for p in parts)

def collect_markdown_files(root):
    md_files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            if Path(f).suffix.lower() in MARKDOWN_EXT:
                md_files.append(Path(dirpath) / f)
    return md_files

# ─────────────────────────────────────────────────────────────
# Check 1: Link Validation
# ─────────────────────────────────────────────────────────────
def check_links(md_files, root):
    result = ValidationResult()
    rel_pattern = re.compile(r'\]\(([^)#\s]+\.md(?:#[^\)]*)?)\)')
    broken_links = []
    total_links = 0
    
    for md_file in md_files:
        try:
            content = md_file.read_text(encoding='utf-8')
        except Exception:
            continue
        
        md_dir = md_file.parent
        for match in rel_pattern.finditer(content):
            total_links += 1
            target = match.group(1).split('#')[0]  # Remove anchor
            resolved = (md_dir / target).resolve()
            if not resolved.exists():
                broken_links.append((str(md_file.relative_to(root)), match.group(1)))
    
    if broken_links:
        result.warning(f"Broken links found: {len(broken_links)}")
        for src, tgt in broken_links[:10]:
            result.warning(f"  {src} -> {tgt}")
        if len(broken_links) > 10:
            result.warning(f"  ... and {len(broken_links) - 10} more")
    else:
        result.ok(f"All {total_links} relative links valid")
    
    return result

# ─────────────────────────────────────────────────────────────
# Check 2: Bilingual Pairing
# ─────────────────────────────────────────────────────────────
def check_bilingual(md_files, root):
    result = ValidationResult()
    readme_pairs = {}
    
    for md_file in md_files:
        rel = md_file.relative_to(root)
        name = md_file.name.lower()
        parent = md_file.parent
        
        if name == 'readme.md':
            if parent not in readme_pairs:
                readme_pairs[parent] = {'en': None, 'zh': None}
            readme_pairs[parent]['en'] = rel
        elif name == 'readme-zh.md':
            if parent not in readme_pairs:
                readme_pairs[parent] = {'en': None, 'zh': None}
            readme_pairs[parent]['zh'] = rel
    
    missing_zh = [pair['en'] for pair in readme_pairs.values() if pair['en'] and not pair['zh']]
    missing_en = [pair['zh'] for pair in readme_pairs.values() if pair['zh'] and not pair['en']]
    
    if missing_zh:
        result.warning(f"readme.md without readme-zh.md: {len(missing_zh)}")
        for m in missing_zh[:5]:
            result.warning(f"  {m}")
    if missing_en:
        result.warning(f"readme-zh.md without readme.md: {len(missing_en)}")
        for m in missing_en[:5]:
            result.warning(f"  {m}")
    
    if not missing_zh and not missing_en:
        result.ok(f"All {len(readme_pairs)} readme pairs complete")
    
    return result

# ─────────────────────────────────────────────────────────────
# Check 3: Numbering Consistency
# ─────────────────────────────────────────────────────────────
def check_numbering(root):
    result = ValidationResult()
    numbered_dirs = []
    
    for item in root.iterdir():
        if item.is_dir() and item.name[0:2].isdigit():
            prefix = item.name.split('-')[0]
            numbered_dirs.append((prefix, item.name))
    
    prefixes = [p for p, _ in numbered_dirs]
    duplicates = [p for p in set(prefixes) if prefixes.count(p) > 1]
    
    if duplicates:
        result.error(f"Duplicate numbering: {duplicates}")
        for d in duplicates:
            dirs = [name for p, name in numbered_dirs if p == d]
            result.error(f"  {d}: {', '.join(dirs)}")
    else:
        result.ok(f"{len(numbered_dirs)} numbered directories, all unique")
    
    # Check for gaps
    nums = sorted([int(p) for p, _ in numbered_dirs])
    if nums:
        gaps = []
        for i in range(nums[0], nums[-1]):
            if i not in nums:
                gaps.append(i)
        if gaps:
            result.warning(f"Numbering gaps: {gaps}")
        else:
            result.ok(f"Numbering sequence continuous: {nums[0]:02d}-{nums[-1]:02d}")
    
    return result

# ─────────────────────────────────────────────────────────────
# Check 4: Empty Directories
# ─────────────────────────────────────────────────────────────
def check_empty_dirs(root):
    result = ValidationResult()
    empty_dirs = []
    
    for dirpath, dirnames, filenames in os.walk(root):
        rel = Path(dirpath).relative_to(root)
        if should_skip(rel):
            continue
        # Check if directory has no non-hidden files and no subdirectories with files
        has_content = False
        for f in filenames:
            if not f.startswith('.'):
                has_content = True
                break
        if not has_content and not dirnames:
            empty_dirs.append(str(rel))
    
    if empty_dirs:
        result.error(f"Empty directories found: {len(empty_dirs)}")
        for d in empty_dirs:
            result.error(f"  {d}")
    else:
        result.ok("No empty directories found")
    
    return result

# ─────────────────────────────────────────────────────────────
# Check 5: Frontmatter Validation
# ─────────────────────────────────────────────────────────────
def check_frontmatter(md_files, root):
    result = ValidationResult()
    missing_fm = []
    missing_fields = defaultdict(list)
    total = len(md_files)
    
    for md_file in md_files:
        try:
            content = md_file.read_text(encoding='utf-8')
        except Exception:
            continue
        
        # Check for YAML frontmatter
        if content.startswith('---'):
            end = content.find('---', 3)
            if end > 0:
                fm_content = content[3:end].strip()
                # Check required fields
                for field in REQUIRED_FRONTMATTER_FIELDS:
                    if f'{field}:' not in fm_content:
                        missing_fields[field].append(str(md_file.relative_to(root)))
            else:
                missing_fm.append(str(md_file.relative_to(root)))
        else:
            missing_fm.append(str(md_file.relative_to(root)))
    
    has_missing = bool(missing_fm) or bool(missing_fields)
    
    if missing_fm:
        result.warning(f"Files without frontmatter: {len(missing_fm)}")
        for f in missing_fm[:5]:
            result.warning(f"  {f}")
        if len(missing_fm) > 5:
            result.warning(f"  ... and {len(missing_fm) - 5} more")
    
    for field, files in missing_fields.items():
        result.warning(f"Missing '{field}' in frontmatter: {len(files)} files")
    
    if not has_missing:
        result.ok(f"All {total} markdown files have complete frontmatter")
    
    return result

# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description='Validate O-RAN Knowledge Base structure')
    parser.add_argument('--check', choices=['links', 'dirs', 'bilingual', 'numbering', 'frontmatter', 'all'],
                       default='all', help='Run specific check (default: all)')
    parser.add_argument('--json', action='store_true', help='Output JSON report')
    args = parser.parse_args()
    
    print("\n" + "🔍 " * 10)
    print("  O-RAN Knowledge Base Validator")
    print("🔍 " * 10)
    
    root = REPO_ROOT
    md_files = collect_markdown_files(root)
    print(f"\n  Repository: {root}")
    print(f"  Markdown files: {len(md_files)}")
    
    checks = {
        'links': lambda: check_links(md_files, root),
        'bilingual': lambda: check_bilingual(md_files, root),
        'numbering': lambda: check_numbering(root),
        'dirs': lambda: check_empty_dirs(root),
        'frontmatter': lambda: check_frontmatter(md_files, root),
    }
    
    results = []
    
    if args.check == 'all':
        for name, check_fn in checks.items():
            r = check_fn()
            r.report(f"Check: {name.upper()}")
            results.append(r)
    else:
        if args.check in checks:
            r = checks[args.check]()
            r.report(f"Check: {args.check.upper()}")
            results.append(r)
    
    # Summary
    total_errors = sum(len(r.errors) for r in results)
    total_warnings = sum(len(r.warnings) for r in results)
    
    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}")
    print(f"  Errors:   {total_errors}")
    print(f"  Warnings: {total_warnings}")
    
    if args.json:
        import json
        report = {
            'errors': total_errors,
            'warnings': total_warnings,
            'checks': {}
        }
        for r, name in zip(results, checks.keys()):
            report['checks'][name] = {
                'errors': r.errors,
                'warnings': r.warnings,
                'info': r.info
            }
        print("\n" + json.dumps(report, indent=2, ensure_ascii=False))
    
    if total_errors > 0:
        sys.exit(2)
    elif total_warnings > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == '__main__':
    main()
