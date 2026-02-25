#!/usr/bin/env python3
"""Generate archive index pages for historical daily learning content."""

import os
import sys
from pathlib import Path
from datetime import datetime
import re


def get_language_title(lang):
    """Get the display title for a language."""
    lang_titles = {
        'java': 'Java',
        'python': 'Python',
        'go': 'Go',
        'ruby': 'Ruby'
    }
    return lang_titles.get(lang, lang)


def parse_date_from_filename(filename):
    """Extract date from filename like 2026-02-25.md"""
    match = re.match(r'(\d{4}-\d{2}-\d{2})\.md$', filename)
    if match:
        return match.group(1)
    return None


def generate_archive_index(lang):
    """Generate archive index for a specific language."""
    lang_title = get_language_title(lang)

    # Get all daily files
    daily_dir = Path('docs') / lang / 'daily'
    if not daily_dir.exists():
        print(f"Warning: Daily directory not found for {lang}")
        return False

    # Collect all daily files
    daily_files = []
    for file_path in sorted(daily_dir.glob('*.md'), reverse=True):
        date_str = parse_date_from_filename(file_path.name)
        if date_str:
            daily_files.append({
                'date': date_str,
                'filename': file_path.name,
                'path': f'daily/{file_path.name}'
            })

    if not daily_files:
        print(f"No daily files found for {lang}")
        return False

    # Group by year and month
    grouped = {}
    for item in daily_files:
        year_month = item['date'][:7]  # YYYY-MM
        if year_month not in grouped:
            grouped[year_month] = []
        grouped[year_month].append(item)

    # Generate archive index
    archive_path = Path('docs') / lang / 'archive.md'

    content_parts = [
        f"---",
        f"layout: default",
        f'title: "{lang_title} 学习归档"',
        f"---",
        f"",
        f"# {lang_title} 学习归档",
        f"",
        f"[返回 {lang_title} 首页](README.md)",
        f"",
        f"## 📚 历史学习记录",
        f"",
        f"本页面归档了所有历史学习内容，按月份组织。",
        f"",
    ]

    # Add content by month
    for year_month in sorted(grouped.keys(), reverse=True):
        # Parse year and month for display
        year, month = year_month.split('-')
        month_name = f"{year}年{int(month)}月"

        content_parts.append(f"### {month_name}")
        content_parts.append(f"")

        for item in grouped[year_month]:
            content_parts.append(f"- [{item['date']}]({item['path']}) - 学习记录")

        content_parts.append(f"")

    content_parts.extend([
        f"---",
        f"",
        f"[返回 {lang_title} 首页](README.md) | [返回网站首页](../index.md)",
        f""
    ])

    content = '\n'.join(content_parts)
    archive_path.write_text(content, encoding='utf-8')

    print(f"Generated: {archive_path}")
    return True


def main():
    """Main function."""
    # Languages to generate archives for
    languages = ['java', 'python', 'go', 'ruby']

    # Generate archive index for each language
    for lang in languages:
        print(f"\n=== Generating archive for {lang} ===")
        generate_archive_index(lang)

    print("\nArchive generation completed successfully!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
