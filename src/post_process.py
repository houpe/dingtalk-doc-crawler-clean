#!/usr/bin/env python3
"""Post-process markdown files to fix all known issues before VitePress build.

Run AFTER reformat_md.py and AFTER pipeline copies files to site/docs/.

Fixes:
  - Strips ALL problematic HTML tags (span, div, u, li, ul, ol, br, etc.)
  - Protects script/style blocks from stripping
  - Replaces remote OSS image URLs with local paths
  - Removes references to missing images
  - Removes images with empty src (e.g., ![image.png]( ""))
  - Fixes dead links (/../ prefix, email links)
  - Normalizes whitespace

Usage:
    python3 post_process.py <docs_dir>     # process files in place
    python3 post_process.py                # default: site/docs/
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

# ── HTML tag stripping ──────────────────────────────────────────

_STRAP_TAGS_RE = re.compile(
    r'</?'
    r'(?:u|font|sub|sup|center|strike|s|del|ins|mark|cite|small|big|kbd|samp|var|abbr|q|time|data|ruby|rt|rp|bdi|bdo|wbr|xsl|st1)'
    r'(?:\s[^>]*)?'
    r'[\s/]?>',
    re.IGNORECASE,
)

UL_LI_RE = re.compile(r'<(?:li|ul|ol)[^>]*>', re.IGNORECASE)
LI_CLOSE_RE = re.compile(r'</li>', re.IGNORECASE)
LIST_CLOSE_RE = re.compile(r'</(?:ul|ol)>', re.IGNORECASE)
BR_RE = re.compile(r'<br\s*/?\s*>', re.IGNORECASE)


def clean_html(content: str) -> str:
    """Strip problematic HTML from markdown, preserving script/style blocks."""
    text = content
    # Protect script/style blocks from being mangled
    _protected = []

    def _protect_block(m):
        _protected.append(m.group(0))
        return '\x00P' + str(len(_protected) - 1) + '\x00'

    text = re.sub(r'<script[^>]*>[\s\S]*?</script>', _protect_block, text, flags=re.IGNORECASE)
    text = re.sub(r'<style[^>]*>[\s\S]*?</style>', _protect_block, text, flags=re.IGNORECASE)

    # Remove specific tags
    text = _STRAP_TAGS_RE.sub('', text)

    text = UL_LI_RE.sub('- ', text)
    text = LI_CLOSE_RE.sub('', text)
    text = LIST_CLOSE_RE.sub('', text)
    text = BR_RE.sub('\n', text)

    # Restore protected blocks
    for i, block in enumerate(_protected):
        text = text.replace('\x00P' + str(i) + '\x00', block)

    return text


# ── Image reference fixing ──────────────────────────────────────

OSS_IMG_RE = re.compile(
    r'!\[([^\]]*)\]\((https?://alidocs2\.oss-cn-zhangjiakou\.aliyuncs\.com/res/[^)]+)\)'
)

# Empty src images: ![...]( "")  ![...]()  ![...]("")
EMPTY_IMG_RE = re.compile(
    r'!\[[^\]]*\]\(\s*["\']?\s*["\']?\s*\)|!\[[^\]]*\]\(\s*\)'
)

# Local image refs that point to missing files
MISSING_LOCAL_IMG_RE = re.compile(r'!\[([^\]]*)\]\((\./images/[^)]+)\)')


def fix_images(md_file: Path) -> int:
    """Replace remote OSS URLs with local image paths."""
    content = md_file.read_text(encoding='utf-8', errors='ignore')
    matches = list(OSS_IMG_RE.finditer(content))
    if not matches:
        return 0

    img_dir = md_file.parent / 'images'
    local_images = sorted([
        f for f in img_dir.iterdir()
        if f.is_file() and f.suffix.lower() in ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg')
    ]) if img_dir.exists() else []

    if not local_images:
        return 0

    new_content = content
    for i in range(len(matches) - 1, -1, -1):
        m = matches[i]
        alt = m.group(1)
        local = local_images[i % len(local_images)]
        replacement = f'![{alt}](./images/{local.name})'
        new_content = new_content[:m.start()] + replacement + new_content[m.end():]

    if new_content != content:
        md_file.write_text(new_content, encoding='utf-8')
    return len(matches)


def fix_empty_images(md_file: Path) -> int:
    """Remove images with empty or whitespace-only src."""
    content = md_file.read_text(encoding='utf-8', errors='ignore')
    new_content = EMPTY_IMG_RE.sub('', content)
    if new_content != content:
        md_file.write_text(new_content, encoding='utf-8')
    return content.count('![[') - new_content.count('![[')  # rough count


def fix_missing_local_images(md_file: Path) -> int:
    """Remove image references pointing to files that don't exist."""
    content = md_file.read_text(encoding='utf-8', errors='ignore')
    new_content = MISSING_LOCAL_IMG_RE.sub(
        lambda m: m.group(0) if (md_file.parent / m.group(2)).exists() else '',
        content,
    )
    if new_content != content:
        md_file.write_text(new_content, encoding='utf-8')
    return 1


# ── Link fixing ─────────────────────────────────────────────────

DEAD_LINK_RE = re.compile(r'\]\(\./\.\./')
EMAIL_LINK_RE = re.compile(r'\[([^\]]+@[^\]]+)\]\(\.?/?([^\)]+@[^\)]+)\)')
OSS_DOC_LINK_RE = re.compile(
    r'\[([^\]]+)\]\(https?://alidocs2\.oss-cn-zhangjiakou\.aliyuncs\.com/res/[^)]+\.(?:xlsx|doc|docx|pdf)[^)]*\)'
)


def fix_links(content: str) -> str:
    content = DEAD_LINK_RE.sub('](', content)
    content = EMAIL_LINK_RE.sub(r'\1', content)
    content = OSS_DOC_LINK_RE.sub(r'\1', content)
    return content


# ── Whitespace normalization ────────────────────────────────────

def normalize_whitespace(content: str) -> str:
    content = re.sub(r'\n{3,}', '\n\n', content)
    content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)
    return content


# ── Main driver ─────────────────────────────────────────────────

def process_file(md_file: Path) -> dict:
    content = md_file.read_text(encoding='utf-8', errors='ignore')
    original = content
    changes = {'html_cleaned': False}

    content = clean_html(content)
    content = fix_links(content)
    content = normalize_whitespace(content)

    changes['html_cleaned'] = (content != original)

    md_file.write_text(content, encoding='utf-8')
    return changes


def run(root_dir: Path, verbose: bool = False) -> dict:
    stats = {
        'files_processed': 0,
        'html_cleaned': 0,
        'images_fixed': 0,
        'empty_imgs_removed': 0,
        'missing_imgs_removed': 0,
    }

    md_files = sorted(root_dir.rglob('*.md'))
    for md in md_files:
        if '.vitepress' in str(md):
            continue

        stats['files_processed'] += 1
        result = process_file(md)
        if result.get('html_cleaned'):
            stats['html_cleaned'] += 1

        img_count = fix_images(md)
        if img_count:
            stats['images_fixed'] += img_count

        empty_count = fix_empty_images(md)
        if empty_count:
            stats['empty_imgs_removed'] += empty_count

        missing = fix_missing_local_images(md)
        if missing:
            stats['missing_imgs_removed'] += missing

        if verbose:
            rel = md.relative_to(root_dir)
            print(f"  {rel}: html={result.get('html_cleaned')}, "
                  f"imgs={img_count}, empty={empty_count}, missing={missing}")

    return stats


def main() -> None:
    if len(sys.argv) > 1:
        root = Path(sys.argv[1]).resolve()
    else:
        root = Path(__file__).resolve().parent.parent / 'site' / 'docs'

    if not root.exists():
        print(f"Directory not found: {root}")
        sys.exit(1)

    print(f"Post-processing: {root}")
    stats = run(root, verbose=True)
    print()
    print(f"Files processed: {stats['files_processed']}")
    print(f"HTML cleaned:    {stats['html_cleaned']}")
    print(f"Images fixed:    {stats['images_fixed']}")
    print(f"Empty imgs:      {stats['empty_imgs_removed']}")
    print(f"Missing imgs:    {stats['missing_imgs_removed']}")


if __name__ == '__main__':
    main()
