#!/usr/bin/env python3
"""Collect daily learning content from configured sources."""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path
import yaml
import feedparser
import html
from urllib.parse import urlparse


def load_config():
    """Load sources configuration."""
    config_path = Path('config/sources.yaml')
    if not config_path.exists():
        print(f"Error: Configuration file {config_path} not found", file=sys.stderr)
        sys.exit(1)

    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_language_title(lang):
    """Get the display title for a language."""
    lang_titles = {
        'java': 'Java',
        'python': 'Python',
        'go': 'Go',
        'ruby': 'Ruby'
    }
    return lang_titles.get(lang, lang)


def clean_text(text):
    """Clean and truncate text content."""
    if not text:
        return ""
    # Unescape HTML entities
    text = html.unescape(text)
    # Strip HTML tags
    text = text.replace('<', '&lt;').replace('>', '&gt;')
    # Remove extra whitespace
    text = ' '.join(text.split())
    # Truncate
    if len(text) > 200:
        text = text[:197] + '...'
    return text


def collect_rss_feed(source, max_items):
    """Collect items from an RSS feed."""
    items = []
    try:
        feed = feedparser.parse(source['url'])

        count = 0
        for entry in feed.entries:
            if count >= max_items:
                break

            # Extract item data
            title = entry.get('title', 'No title')
            link = entry.get('link', '')
            summary = clean_text(entry.get('summary', entry.get('description', '')))

            # Parse date
            published = entry.get('published', entry.get('updated', ''))
            if published:
                try:
                    from email.utils import parsedate_to_datetime
                    pub_date = parsedate_to_datetime(published)
                    published = pub_date.strftime('%Y-%m-%d')
                except:
                    published = ''

            items.append({
                'title': title,
                'link': link,
                'summary': summary,
                'published': published
            })
            count += 1

    except Exception as e:
        print(f"Warning: Failed to fetch {source['name']}: {e}", file=sys.stderr)

    return items


def collect_github_repo(source, max_items):
    """Collect information from a GitHub repository."""
    # For GitHub repos, we'll just link to them as a reference
    # In a full implementation, you could use GitHub API to get recent commits, issues, etc.
    items = []
    try:
        repo_url = source['url']
        items.append({
            'title': f"{source['name']} - Best Practices Repository",
            'link': repo_url,
            'summary': source.get('description', 'Curated collection of best practices'),
            'published': ''
        })
    except Exception as e:
        print(f"Warning: Failed to process {source['name']}: {e}", file=sys.stderr)

    return items


def collect_content_for_language(lang, config):
    """Collect content for a specific language."""
    lang_config = config['languages'].get(lang, {})
    sources = lang_config.get('sources', [])
    max_items = config['output'].get('max_items_per_source', 5)
    max_total = config['output'].get('max_total_items', 15)

    all_items = []

    for source in sources:
        if not source.get('enabled', True):
            continue

        source_type = source.get('type', 'rss')

        if source_type == 'rss':
            items = collect_rss_feed(source, max_items)
        elif source_type == 'github':
            items = collect_github_repo(source, max_items)
        else:
            print(f"Warning: Unknown source type '{source_type}' for {source['name']}", file=sys.stderr)
            continue

        # Add source name to each item
        for item in items:
            item['source'] = source['name']

        all_items.extend(items)

    # Limit total items
    if len(all_items) > max_total:
        all_items = all_items[:max_total]

    return all_items


def generate_daily_doc(lang, today, items):
    """Generate a daily learning doc with collected content."""
    lang_title = get_language_title(lang)

    # Create directory structure
    doc_dir = Path('docs') / lang / 'daily'
    doc_dir.mkdir(parents=True, exist_ok=True)

    # Create the file
    file_path = doc_dir / f'{today}.md'
    file_existed = file_path.exists()

    # Build content
    content_parts = [
        f"---",
        f"layout: default",
        f'title: "{lang_title} 今日学习（{today}）"',
        f"---",
        f"",
        f"# {lang_title} 今日学习（{today}）",
        f"",
        f"## 今日推荐内容",
        f""
    ]

    if items:
        for i, item in enumerate(items, 1):
            content_parts.append(f"### {i}. {item['title']}")
            content_parts.append(f"")
            content_parts.append(f"**来源**: {item['source']}")
            if item['published']:
                content_parts.append(f"**发布时间**: {item['published']}")
            content_parts.append(f"")
            if item['summary']:
                content_parts.append(f"{item['summary']}")
                content_parts.append(f"")
            content_parts.append(f"[查看详情]({item['link']})")
            content_parts.append(f"")
            content_parts.append(f"---")
            content_parts.append(f"")
    else:
        content_parts.append("暂无推荐内容。")
        content_parts.append("")

    content_parts.extend([
        f"## 学习计划",
        f"",
        f"### 入门",
        f"- [ ] 今日目标：",
        f"- [ ] 笔记：",
        f"",
        f"### 进阶",
        f"- [ ] 今日目标：",
        f"- [ ] 笔记：",
        f"",
        f"### 高级",
        f"- [ ] 今日目标：",
        f"- [ ] 笔记：",
        f"",
        f"## 参考资料",
        f"- 参见 [{lang_title} 权威信息源](../README.md#权威信息源)",
        f""
    ])

    content = '\n'.join(content_parts)
    file_path.write_text(content, encoding='utf-8')

    if file_existed:
        print(f"Overwritten: {file_path}")
    else:
        print(f"Generated: {file_path}")

    return True


def main():
    """Main function."""
    # Load configuration
    config = load_config()

    # Get today's date in UTC
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')

    # Languages to generate docs for
    languages = ['java', 'python', 'go', 'ruby']

    # Collect and generate docs for each language
    for lang in languages:
        print(f"\n=== Processing {lang} ===")
        items = collect_content_for_language(lang, config)
        print(f"Collected {len(items)} items for {lang}")
        generate_daily_doc(lang, today, items)

    # Set output for GitHub Actions
    if 'GITHUB_OUTPUT' in os.environ:
        with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
            f.write(f'today={today}\n')

    print(f"\nDate: {today}")
    print("Content collection completed successfully!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
