#!/usr/bin/env python3
"""Generate daily learning documentation files."""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def get_language_title(lang):
    """Get the display title for a language."""
    lang_titles = {
        'java': 'Java',
        'python': 'Python',
        'go': 'Go',
        'ruby': 'Ruby'
    }
    return lang_titles.get(lang, lang)


def generate_daily_doc(lang, today):
    """Generate a daily learning doc for a specific language."""
    lang_title = get_language_title(lang)

    # Create directory structure
    doc_dir = Path('docs') / lang / 'daily'
    doc_dir.mkdir(parents=True, exist_ok=True)

    # Create the file
    file_path = doc_dir / f'{today}.md'

    # Note: We no longer skip if file exists - allow overwrite when manually triggered
    file_existed = file_path.exists()

    content = f"""# {lang_title} 今日学习（{today}）

## 入门
- [ ] 今日目标：
- [ ] 笔记：

## 进阶
- [ ] 今日目标：
- [ ] 笔记：

## 高级
- [ ] 今日目标：
- [ ] 笔记：

## 参考资料
- 参见 [{lang_title} 权威信息源](../README.md#权威信息源)
"""

    file_path.write_text(content, encoding='utf-8')
    if file_existed:
        print(f"Overwritten: {file_path}")
    else:
        print(f"Generated: {file_path}")
    return True


def main():
    """Main function."""
    # Get today's date in UTC
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')

    # Languages to generate docs for
    languages = ['java', 'python', 'go', 'ruby']

    # Generate docs for each language
    for lang in languages:
        generate_daily_doc(lang, today)

    # Set output for GitHub Actions
    if 'GITHUB_OUTPUT' in os.environ:
        with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
            f.write(f'today={today}\n')

    print(f"Date: {today}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
