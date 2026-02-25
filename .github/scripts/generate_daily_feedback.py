#!/usr/bin/env python3
"""Generate daily feedback summary and planning documentation files."""

import os
import sys
from datetime import datetime, timedelta, timezone
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


def generate_feedback_doc(lang, yesterday, tomorrow):
    """Generate a feedback and planning doc for a specific language."""
    lang_title = get_language_title(lang)

    # Create directory structure
    doc_dir = Path('docs') / lang / 'daily'
    doc_dir.mkdir(parents=True, exist_ok=True)

    # Check if files exist
    summary_file = doc_dir / f'{tomorrow}.md'
    yesterday_file = doc_dir / f'{yesterday}.md'

    # Note: We no longer skip if file exists - allow overwrite when manually triggered
    file_existed = summary_file.exists()

    # Create yesterday reference
    yesterday_basename = yesterday_file.name
    if yesterday_file.exists():
        yesterday_ref = f"- 昨日记录：[{yesterday}]({yesterday_basename})"
    else:
        yesterday_ref = "- 昨日记录：未找到"

    content = f"""---
layout: default
title: "{lang_title} 学习计划（{tomorrow}）"
---

# {lang_title} 学习计划（{tomorrow}）

## 昨日反馈
{yesterday_ref}
- 今日总结：请在此填写昨天的学习反馈、完成度与困难。

## 明日学习计划
- 学习目标（基于权威资料，如 {lang_title} 官方文档）：
- 预计投入时间：
- 学习量调整说明：

## 参考资料
- 参见 [{lang_title} 权威信息源](../README.md#权威信息源)
"""

    summary_file.write_text(content, encoding='utf-8')
    if file_existed:
        print(f"Overwritten: {summary_file}")
    else:
        print(f"Generated: {summary_file}")
    return True


def main():
    """Main function."""
    # Get dates in UTC
    now = datetime.now(timezone.utc)
    yesterday = (now - timedelta(days=1)).strftime('%Y-%m-%d')
    tomorrow = (now + timedelta(days=1)).strftime('%Y-%m-%d')

    # Languages to generate docs for
    languages = ['java', 'python', 'go', 'ruby']

    # Generate docs for each language
    for lang in languages:
        generate_feedback_doc(lang, yesterday, tomorrow)

    # Set output for GitHub Actions
    if 'GITHUB_OUTPUT' in os.environ:
        with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
            f.write(f'tomorrow={tomorrow}\n')

    print(f"Yesterday: {yesterday}, Tomorrow: {tomorrow}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
