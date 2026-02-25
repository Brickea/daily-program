#!/usr/bin/env python3
"""Unit tests for generate_daily_learning.py"""

import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

# Import the module to test
from generate_daily_learning import get_language_title, generate_daily_doc, main


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


class TestGenerateDailyDoc(unittest.TestCase):
    """Test generate_daily_doc function."""

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

    def test_generate_new_doc(self):
        """Test generating a new daily doc."""
        today = '2026-02-25'
        result = generate_daily_doc('java', today)

        self.assertTrue(result)

        # Check file was created
        file_path = Path('docs/java/daily/2026-02-25.md')
        self.assertTrue(file_path.exists())

        # Check content
        content = file_path.read_text(encoding='utf-8')
        self.assertIn('# Java 今日学习（2026-02-25）', content)
        self.assertIn('## 入门', content)
        self.assertIn('## 进阶', content)
        self.assertIn('## 高级', content)
        self.assertIn('## 参考资料', content)
        self.assertIn('[Java 权威信息源](../README.md#权威信息源)', content)

    def test_generate_existing_doc(self):
        """Test that existing docs are overwritten."""
        today = '2026-02-25'

        # Create the file first
        doc_dir = Path('docs/java/daily')
        doc_dir.mkdir(parents=True, exist_ok=True)
        file_path = doc_dir / f'{today}.md'
        file_path.write_text('Existing content', encoding='utf-8')

        # Try to generate again - should overwrite
        result = generate_daily_doc('java', today)

        self.assertTrue(result)

        # Check content was changed
        content = file_path.read_text(encoding='utf-8')
        self.assertIn('# Java 今日学习（2026-02-25）', content)
        self.assertNotEqual(content, 'Existing content')

    def test_chinese_characters_encoding(self):
        """Test that Chinese characters are properly encoded."""
        today = '2026-02-25'
        generate_daily_doc('python', today)

        file_path = Path('docs/python/daily/2026-02-25.md')
        content = file_path.read_text(encoding='utf-8')

        # Check for Chinese characters
        self.assertIn('今日学习', content)
        self.assertIn('入门', content)
        self.assertIn('进阶', content)
        self.assertIn('高级', content)
        self.assertIn('参考资料', content)
        self.assertIn('权威信息源', content)

    def test_all_languages(self):
        """Test generating docs for all supported languages."""
        today = '2026-02-25'
        languages = ['java', 'python', 'go', 'ruby']

        for lang in languages:
            result = generate_daily_doc(lang, today)
            self.assertTrue(result)

            file_path = Path(f'docs/{lang}/daily/{today}.md')
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
            today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
            for lang in ['java', 'python', 'go', 'ruby']:
                file_path = Path(f'docs/{lang}/daily/{today}.md')
                self.assertTrue(file_path.exists())

            # Check GITHUB_OUTPUT was written
            self.assertTrue(output_file.exists())
            output_content = output_file.read_text()
            self.assertIn(f'today={today}', output_content)
        finally:
            if 'GITHUB_OUTPUT' in os.environ:
                del os.environ['GITHUB_OUTPUT']

    def test_main_no_new_files(self):
        """Test that main returns 0 even when files already exist (overwriting)."""
        # Pre-create all files
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        for lang in ['java', 'python', 'go', 'ruby']:
            doc_dir = Path(f'docs/{lang}/daily')
            doc_dir.mkdir(parents=True, exist_ok=True)
            file_path = doc_dir / f'{today}.md'
            file_path.write_text('Existing', encoding='utf-8')

        exit_code = main()

        # Should return 0 (files are overwritten)
        self.assertEqual(exit_code, 0)

        # Check files were overwritten
        for lang in ['java', 'python', 'go', 'ruby']:
            file_path = Path(f'docs/{lang}/daily/{today}.md')
            content = file_path.read_text(encoding='utf-8')
            self.assertNotEqual(content, 'Existing')


if __name__ == '__main__':
    unittest.main()
