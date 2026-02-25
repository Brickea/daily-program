#!/usr/bin/env python3
"""Unit tests for collect_daily_content.py"""

import unittest
import sys
from pathlib import Path
from datetime import datetime, timezone
import tempfile
import shutil
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

import collect_daily_content


class TestCollectDailyContent(unittest.TestCase):
    """Test cases for content collection."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

        # Create test config directory
        config_dir = Path(self.test_dir) / 'config'
        config_dir.mkdir(exist_ok=True)

        # Create docs directory structure
        docs_dir = Path(self.test_dir) / 'docs'
        for lang in ['java', 'python', 'go', 'ruby']:
            (docs_dir / lang / 'daily').mkdir(parents=True, exist_ok=True)

        # Create test config file
        config_content = """
output:
  max_items_per_source: 3
  max_total_items: 10
  max_items_display_per_source: 5

languages:
  java:
    sources:
      - name: "Test Source"
        type: rss
        url: "https://example.com/feed.rss"
        enabled: true
  python:
    sources:
      - name: "Test GitHub"
        type: github
        url: "https://github.com/test/repo"
        enabled: true
"""
        config_path = config_dir / 'sources.yaml'
        config_path.write_text(config_content)

    def tearDown(self):
        """Clean up test fixtures."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_get_language_title(self):
        """Test language title retrieval."""
        self.assertEqual(collect_daily_content.get_language_title('java'), 'Java')
        self.assertEqual(collect_daily_content.get_language_title('python'), 'Python')
        self.assertEqual(collect_daily_content.get_language_title('go'), 'Go')
        self.assertEqual(collect_daily_content.get_language_title('ruby'), 'Ruby')

    def test_clean_text(self):
        """Test text cleaning."""
        # Test empty text
        self.assertEqual(collect_daily_content.clean_text(''), '')
        self.assertEqual(collect_daily_content.clean_text(None), '')

        # Test HTML entity unescaping
        text = 'Test &amp; text'
        self.assertEqual(collect_daily_content.clean_text(text), 'Test & text')

        # Test HTML tag stripping
        html_text = '<p>Test <em>content</em> here</p>'
        self.assertEqual(collect_daily_content.clean_text(html_text), 'Test content here')

        # Test truncation
        long_text = 'a' * 300
        cleaned = collect_daily_content.clean_text(long_text)
        self.assertEqual(len(cleaned), 200)
        self.assertTrue(cleaned.endswith('...'))

    def test_load_config(self):
        """Test configuration loading."""
        config = collect_daily_content.load_config()
        self.assertIsNotNone(config)
        self.assertIn('languages', config)
        self.assertIn('output', config)
        self.assertEqual(config['output']['max_items_per_source'], 3)
        self.assertEqual(config['output']['max_total_items'], 10)

    def test_collect_github_repo(self):
        """Test GitHub repository collection."""
        source = {
            'name': 'Test Repo',
            'url': 'https://github.com/test/repo',
            'description': 'Test description'
        }
        items = collect_daily_content.collect_github_repo(source, 5)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['title'], 'Test Repo - Best Practices Repository')
        self.assertEqual(items[0]['link'], 'https://github.com/test/repo')
        self.assertEqual(items[0]['summary'], 'Test description')

    def test_generate_daily_doc(self):
        """Test daily document generation."""
        lang = 'java'
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        items = [
            {
                'title': 'Test Article',
                'link': 'https://example.com/article',
                'summary': 'Test summary',
                'published': '2026-02-25',
                'source': 'Test Source'
            }
        ]

        config = collect_daily_content.load_config()
        result = collect_daily_content.generate_daily_doc(lang, today, items, config)
        self.assertTrue(result)

        # Check file was created
        file_path = Path(self.test_dir) / 'docs' / lang / 'daily' / f'{today}.md'
        self.assertTrue(file_path.exists())

        # Check content
        content = file_path.read_text(encoding='utf-8')
        self.assertIn('Java 今日学习', content)
        self.assertIn('Test Article', content)
        self.assertIn('Test Source', content)
        self.assertIn('2026-02-25', content)
        self.assertIn('Test summary', content)
        self.assertIn('## 学习计划', content)
        self.assertIn('### 入门', content)

    def test_generate_daily_doc_no_items(self):
        """Test daily document generation with no items."""
        lang = 'python'
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        items = []

        config = collect_daily_content.load_config()
        result = collect_daily_content.generate_daily_doc(lang, today, items, config)
        self.assertTrue(result)

        # Check file was created
        file_path = Path(self.test_dir) / 'docs' / lang / 'daily' / f'{today}.md'
        self.assertTrue(file_path.exists())

        # Check content
        content = file_path.read_text(encoding='utf-8')
        self.assertIn('Python 今日学习', content)
        self.assertIn('暂无推荐内容', content)

    def test_generate_daily_doc_overwrite(self):
        """Test that existing files are overwritten."""
        lang = 'go'
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        items = []

        # Create initial file
        file_path = Path(self.test_dir) / 'docs' / lang / 'daily' / f'{today}.md'
        file_path.write_text('Old content', encoding='utf-8')
        self.assertTrue(file_path.exists())

        # Generate new content
        config = collect_daily_content.load_config()
        result = collect_daily_content.generate_daily_doc(lang, today, items, config)
        self.assertTrue(result)

        # Check file was overwritten
        content = file_path.read_text(encoding='utf-8')
        self.assertNotEqual(content, 'Old content')
        self.assertIn('Go 今日学习', content)


if __name__ == '__main__':
    unittest.main()
