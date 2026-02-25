#!/usr/bin/env python3
"""Unit tests for generate_daily_feedback.py"""

import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Import the module to test
from generate_daily_feedback import get_language_title, generate_feedback_doc, main


class TestGetLanguageTitle(unittest.TestCase):
    """Test get_language_title function."""

    def test_known_languages(self):
        """Test that known languages return correct titles."""
        self.assertEqual(get_language_title('java'), 'Java')
        self.assertEqual(get_language_title('python'), 'Python')
        self.assertEqual(get_language_title('go'), 'Go')
        self.assertEqual(get_language_title('ruby'), 'Ruby')

    def test_unknown_language(self):
        """Test that unknown languages return the input as-is."""
        self.assertEqual(get_language_title('rust'), 'rust')
        self.assertEqual(get_language_title('javascript'), 'javascript')


class TestGenerateFeedbackDoc(unittest.TestCase):
    """Test generate_feedback_doc function."""

    def setUp(self):
        """Set up temporary directory for tests."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        """Clean up temporary directory."""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.test_dir)

    def test_generate_new_feedback_doc(self):
        """Test generating a new feedback doc."""
        yesterday = '2026-02-24'
        tomorrow = '2026-02-26'

        result = generate_feedback_doc('java', yesterday, tomorrow)

        self.assertTrue(result)

        # Check file was created
        file_path = Path('docs/java/daily/2026-02-26.md')
        self.assertTrue(file_path.exists())

        # Check content
        content = file_path.read_text(encoding='utf-8')
        self.assertTrue(content.startswith('---\nlayout: default'))
        self.assertIn('title: "Java 学习计划（2026-02-26）"', content)
        self.assertIn('# Java 学习计划（2026-02-26）', content)
        self.assertIn('## 昨日反馈', content)
        self.assertIn('## 明日学习计划', content)
        self.assertIn('## 参考资料', content)
        self.assertIn('[Java 权威信息源](../README.md#权威信息源)', content)

    def test_feedback_doc_with_yesterday_file(self):
        """Test that yesterday file reference is included when it exists."""
        yesterday = '2026-02-24'
        tomorrow = '2026-02-26'

        # Create yesterday's file
        doc_dir = Path('docs/java/daily')
        doc_dir.mkdir(parents=True, exist_ok=True)
        yesterday_file = doc_dir / f'{yesterday}.md'
        yesterday_file.write_text('Yesterday content', encoding='utf-8')

        result = generate_feedback_doc('java', yesterday, tomorrow)

        self.assertTrue(result)

        # Check content includes yesterday link
        file_path = Path('docs/java/daily/2026-02-26.md')
        content = file_path.read_text(encoding='utf-8')
        self.assertIn(f'[{yesterday}]({yesterday}.md)', content)

    def test_feedback_doc_without_yesterday_file(self):
        """Test that missing yesterday file is noted."""
        yesterday = '2026-02-24'
        tomorrow = '2026-02-26'

        result = generate_feedback_doc('java', yesterday, tomorrow)

        self.assertTrue(result)

        # Check content notes missing file
        file_path = Path('docs/java/daily/2026-02-26.md')
        content = file_path.read_text(encoding='utf-8')
        self.assertIn('未找到', content)

    def test_generate_existing_feedback_doc(self):
        """Test that existing feedback docs are overwritten."""
        yesterday = '2026-02-24'
        tomorrow = '2026-02-26'

        # Create the file first
        doc_dir = Path('docs/java/daily')
        doc_dir.mkdir(parents=True, exist_ok=True)
        file_path = doc_dir / f'{tomorrow}.md'
        file_path.write_text('Existing plan', encoding='utf-8')

        # Try to generate again - should overwrite
        result = generate_feedback_doc('java', yesterday, tomorrow)

        self.assertTrue(result)

        # Check content was changed
        content = file_path.read_text(encoding='utf-8')
        self.assertIn('# Java 学习计划（2026-02-26）', content)
        self.assertNotEqual(content, 'Existing plan')

    def test_chinese_characters_encoding(self):
        """Test that Chinese characters are properly encoded."""
        yesterday = '2026-02-24'
        tomorrow = '2026-02-26'

        generate_feedback_doc('python', yesterday, tomorrow)

        file_path = Path('docs/python/daily/2026-02-26.md')
        content = file_path.read_text(encoding='utf-8')

        # Check for Chinese characters
        self.assertIn('学习计划', content)
        self.assertIn('昨日反馈', content)
        self.assertIn('明日学习计划', content)
        self.assertIn('参考资料', content)
        self.assertIn('权威信息源', content)

    def test_all_languages(self):
        """Test generating feedback docs for all supported languages."""
        yesterday = '2026-02-24'
        tomorrow = '2026-02-26'
        languages = ['java', 'python', 'go', 'ruby']

        for lang in languages:
            result = generate_feedback_doc(lang, yesterday, tomorrow)
            self.assertTrue(result)

            file_path = Path(f'docs/{lang}/daily/{tomorrow}.md')
            self.assertTrue(file_path.exists())


class TestMain(unittest.TestCase):
    """Test main function."""

    def setUp(self):
        """Set up temporary directory for tests."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        """Clean up temporary directory."""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.test_dir)

    def test_main_creates_files(self):
        """Test that main creates files for all languages."""
        # Mock GITHUB_OUTPUT
        output_file = Path(self.test_dir) / 'github_output.txt'
        os.environ['GITHUB_OUTPUT'] = str(output_file)

        try:
            exit_code = main()

            # Should return 0 (success with files generated)
            self.assertEqual(exit_code, 0)

            # Check files were created
            now = datetime.now(timezone.utc)
            tomorrow = (now + timedelta(days=1)).strftime('%Y-%m-%d')
            for lang in ['java', 'python', 'go', 'ruby']:
                file_path = Path(f'docs/{lang}/daily/{tomorrow}.md')
                self.assertTrue(file_path.exists())

            # Check GITHUB_OUTPUT was written
            self.assertTrue(output_file.exists())
            output_content = output_file.read_text()
            self.assertIn(f'tomorrow={tomorrow}', output_content)
        finally:
            if 'GITHUB_OUTPUT' in os.environ:
                del os.environ['GITHUB_OUTPUT']

    def test_main_no_new_files(self):
        """Test that main returns 0 even when files already exist (overwriting)."""
        # Pre-create all files
        now = datetime.now(timezone.utc)
        tomorrow = (now + timedelta(days=1)).strftime('%Y-%m-%d')
        for lang in ['java', 'python', 'go', 'ruby']:
            doc_dir = Path(f'docs/{lang}/daily')
            doc_dir.mkdir(parents=True, exist_ok=True)
            file_path = doc_dir / f'{tomorrow}.md'
            file_path.write_text('Existing', encoding='utf-8')

        exit_code = main()

        # Should return 0 (files are overwritten)
        self.assertEqual(exit_code, 0)

        # Check files were overwritten
        for lang in ['java', 'python', 'go', 'ruby']:
            file_path = Path(f'docs/{lang}/daily/{tomorrow}.md')
            content = file_path.read_text(encoding='utf-8')
            self.assertNotEqual(content, 'Existing')


if __name__ == '__main__':
    unittest.main()
