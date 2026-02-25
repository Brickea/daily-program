#!/usr/bin/env python3
"""Unit tests for validate_all.py"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
import yaml

# Import the module to test
from validate_all import (
    validate_yaml_files,
    validate_workflow_integration,
    validate_docs_structure,
    validate_python_scripts,
    validate_github_pages_links,
    main
)


class TestValidateYamlFiles(unittest.TestCase):
    """Test validate_yaml_files function."""

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

    def test_valid_yaml_files(self):
        """Test validation of valid YAML files."""
        # Create workflow directory
        workflows_dir = Path('.github/workflows')
        workflows_dir.mkdir(parents=True, exist_ok=True)

        # Create valid workflow files
        workflows = {
            'daily-learning.yml': {'name': 'Daily Learning', 'jobs': {'test': {}}},
            'daily-feedback.yml': {'name': 'Daily Feedback', 'jobs': {'test': {}}},
            'pages-deploy.yml': {'name': 'Pages Deploy', 'jobs': {'deploy': {}}},
            'test-scripts.yml': {'name': 'Test Scripts', 'jobs': {'test': {}}}
        }

        for filename, content in workflows.items():
            with open(workflows_dir / filename, 'w') as f:
                yaml.dump(content, f)

        result = validate_yaml_files()
        self.assertTrue(result)

    def test_invalid_yaml_file(self):
        """Test validation fails on invalid YAML."""
        workflows_dir = Path('.github/workflows')
        workflows_dir.mkdir(parents=True, exist_ok=True)

        # Create three valid files
        valid_workflows = {
            'daily-learning.yml': {'name': 'Daily Learning', 'jobs': {'test': {}}},
            'daily-feedback.yml': {'name': 'Daily Feedback', 'jobs': {'test': {}}},
            'pages-deploy.yml': {'name': 'Pages Deploy', 'jobs': {'deploy': {}}}
        }

        for filename, content in valid_workflows.items():
            with open(workflows_dir / filename, 'w') as f:
                yaml.dump(content, f)

        # Create one invalid YAML file
        with open(workflows_dir / 'test-scripts.yml', 'w') as f:
            f.write('invalid: yaml: syntax:')

        result = validate_yaml_files()
        self.assertFalse(result)


class TestValidateWorkflowIntegration(unittest.TestCase):
    """Test validate_workflow_integration function."""

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

    def test_correct_integration(self):
        """Test validation succeeds when workflow names match."""
        workflows_dir = Path('.github/workflows')
        workflows_dir.mkdir(parents=True, exist_ok=True)

        # Create workflows with matching names
        pages_config = {
            'name': 'Pages Deploy',
            'on': {
                'workflow_run': {
                    'workflows': ['Daily Learning Docs', 'Daily Feedback Summary']
                }
            }
        }

        learning_config = {
            'name': 'Daily Learning Docs',
            'jobs': {'test': {}}
        }

        feedback_config = {
            'name': 'Daily Feedback Summary',
            'jobs': {'test': {}}
        }

        with open(workflows_dir / 'pages-deploy.yml', 'w') as f:
            yaml.dump(pages_config, f)

        with open(workflows_dir / 'daily-learning.yml', 'w') as f:
            yaml.dump(learning_config, f)

        with open(workflows_dir / 'daily-feedback.yml', 'w') as f:
            yaml.dump(feedback_config, f)

        result = validate_workflow_integration()
        self.assertTrue(result)

    def test_incorrect_integration(self):
        """Test validation fails when workflow names don't match."""
        workflows_dir = Path('.github/workflows')
        workflows_dir.mkdir(parents=True, exist_ok=True)

        # Create workflows with mismatched names
        pages_config = {
            'name': 'Pages Deploy',
            'on': {
                'workflow_run': {
                    'workflows': ['Wrong Name', 'Daily Feedback Summary']
                }
            }
        }

        learning_config = {
            'name': 'Daily Learning Docs',
            'jobs': {'test': {}}
        }

        feedback_config = {
            'name': 'Daily Feedback Summary',
            'jobs': {'test': {}}
        }

        with open(workflows_dir / 'pages-deploy.yml', 'w') as f:
            yaml.dump(pages_config, f)

        with open(workflows_dir / 'daily-learning.yml', 'w') as f:
            yaml.dump(learning_config, f)

        with open(workflows_dir / 'daily-feedback.yml', 'w') as f:
            yaml.dump(feedback_config, f)

        result = validate_workflow_integration()
        self.assertFalse(result)


class TestValidateDocsStructure(unittest.TestCase):
    """Test validate_docs_structure function."""

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

    def test_valid_docs_structure(self):
        """Test validation succeeds with correct docs structure."""
        docs_dir = Path('docs')
        docs_dir.mkdir(exist_ok=True)

        # Create required files
        (docs_dir / 'index.md').write_text('# Index')
        (docs_dir / '_config.yml').write_text(yaml.dump({
            'theme': 'jekyll-theme-minimal',
            'title': 'Daily Program',
            'baseurl': '/daily-program',
            'url': 'https://brickea.github.io'
        }))

        # Create language directories with READMEs
        for lang in ['java', 'python', 'go', 'ruby']:
            lang_dir = docs_dir / lang
            lang_dir.mkdir(exist_ok=True)
            (lang_dir / 'README.md').write_text(f'# {lang.title()}')

        result = validate_docs_structure()
        self.assertTrue(result)

    def test_missing_required_files(self):
        """Test validation fails when required files are missing."""
        docs_dir = Path('docs')
        docs_dir.mkdir(exist_ok=True)

        # Only create index.md, missing _config.yml
        (docs_dir / 'index.md').write_text('# Index')

        result = validate_docs_structure()
        self.assertFalse(result)

    def test_missing_language_directories(self):
        """Test validation fails when language directories are missing."""
        docs_dir = Path('docs')
        docs_dir.mkdir(exist_ok=True)

        # Create required files
        (docs_dir / 'index.md').write_text('# Index')
        (docs_dir / '_config.yml').write_text(yaml.dump({
            'theme': 'minimal',
            'baseurl': '/daily-program',
            'url': 'https://brickea.github.io'
        }))

        # Create only java directory
        java_dir = docs_dir / 'java'
        java_dir.mkdir(exist_ok=True)
        (java_dir / 'README.md').write_text('# Java')

        result = validate_docs_structure()
        self.assertFalse(result)

    def test_missing_baseurl_in_config(self):
        """Test validation fails when baseurl is missing from _config.yml."""
        docs_dir = Path('docs')
        docs_dir.mkdir(exist_ok=True)

        # Create required files but without baseurl
        (docs_dir / 'index.md').write_text('# Index')
        (docs_dir / '_config.yml').write_text(yaml.dump({
            'theme': 'jekyll-theme-minimal',
            'title': 'Daily Program'
        }))

        # Create language directories with READMEs
        for lang in ['java', 'python', 'go', 'ruby']:
            lang_dir = docs_dir / lang
            lang_dir.mkdir(exist_ok=True)
            (lang_dir / 'README.md').write_text(f'# {lang.title()}')

        result = validate_docs_structure()
        self.assertFalse(result)


class TestValidatePythonScripts(unittest.TestCase):
    """Test validate_python_scripts function."""

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

    def test_scripts_exist(self):
        """Test validation succeeds when scripts exist."""
        scripts_dir = Path('.github/scripts')
        scripts_dir.mkdir(parents=True, exist_ok=True)

        # Create script files
        (scripts_dir / 'generate_daily_learning.py').write_text('#!/usr/bin/env python3\nprint("test")')
        (scripts_dir / 'generate_daily_feedback.py').write_text('#!/usr/bin/env python3\nprint("test")')

        result = validate_python_scripts()
        self.assertTrue(result)

    def test_missing_scripts(self):
        """Test validation fails when scripts are missing."""
        scripts_dir = Path('.github/scripts')
        scripts_dir.mkdir(parents=True, exist_ok=True)

        # Only create one script
        (scripts_dir / 'generate_daily_learning.py').write_text('#!/usr/bin/env python3\nprint("test")')

        result = validate_python_scripts()
        self.assertFalse(result)


class TestValidateGitHubPagesLinks(unittest.TestCase):
    """Test validate_github_pages_links function."""

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

    def test_valid_links_with_baseurl(self):
        """Test validation succeeds when all internal links use {{ site.baseurl }}."""
        docs_dir = Path('docs')
        docs_dir.mkdir(exist_ok=True)

        # Create index.md with proper baseurl usage
        index_content = """
# Daily Programming
<a href="{{ site.baseurl }}/java/README.html">Java</a>
<a href="{{ site.baseurl }}/python/README.html">Python</a>
<a href="{{ site.baseurl }}/go/daily/2026-02-25.html">Go Daily</a>
<a href="https://github.com/Brickea/daily-program">GitHub</a>
"""
        (docs_dir / 'index.md').write_text(index_content)

        result = validate_github_pages_links()
        self.assertTrue(result)

    def test_invalid_links_without_baseurl(self):
        """Test validation fails when internal links don't use {{ site.baseurl }}."""
        docs_dir = Path('docs')
        docs_dir.mkdir(exist_ok=True)

        # Create index.md with improper relative links
        index_content = """
# Daily Programming
<a href="java/README.html">Java</a>
<a href="python/README.html">Python</a>
<a href="{{ site.baseurl }}/go/daily/2026-02-25.html">Go Daily</a>
"""
        (docs_dir / 'index.md').write_text(index_content)

        result = validate_github_pages_links()
        self.assertFalse(result)

    def test_external_links_ignored(self):
        """Test that external links are not validated."""
        docs_dir = Path('docs')
        docs_dir.mkdir(exist_ok=True)

        # Create index.md with external links only
        index_content = """
# Daily Programming
<a href="https://github.com/Brickea/daily-program">GitHub</a>
<a href="http://example.com">Example</a>
<a href="#anchor">Anchor</a>
"""
        (docs_dir / 'index.md').write_text(index_content)

        result = validate_github_pages_links()
        self.assertTrue(result)

    def test_missing_index_file(self):
        """Test validation fails when index.md doesn't exist."""
        result = validate_github_pages_links()
        self.assertFalse(result)


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

    def test_main_all_pass(self):
        """Test main returns 0 when all validations pass."""
        # Create complete valid structure
        workflows_dir = Path('.github/workflows')
        workflows_dir.mkdir(parents=True, exist_ok=True)
        scripts_dir = Path('.github/scripts')
        scripts_dir.mkdir(parents=True, exist_ok=True)
        docs_dir = Path('docs')
        docs_dir.mkdir(exist_ok=True)

        # Create workflow files
        workflows = {
            'daily-learning.yml': {'name': 'Daily Learning Docs', 'jobs': {'test': {}}},
            'daily-feedback.yml': {'name': 'Daily Feedback Summary', 'jobs': {'test': {}}},
            'pages-deploy.yml': {
                'name': 'Pages Deploy',
                'on': {
                    'workflow_run': {
                        'workflows': ['Daily Learning Docs', 'Daily Feedback Summary']
                    }
                },
                'jobs': {'deploy': {}}
            },
            'test-scripts.yml': {'name': 'Test Scripts', 'jobs': {'test': {}}}
        }

        for filename, content in workflows.items():
            with open(workflows_dir / filename, 'w') as f:
                yaml.dump(content, f)

        # Create script files
        (scripts_dir / 'generate_daily_learning.py').write_text('#!/usr/bin/env python3\nprint("test")')
        (scripts_dir / 'generate_daily_feedback.py').write_text('#!/usr/bin/env python3\nprint("test")')

        # Create docs structure with proper baseurl links
        index_content = """
# Daily Programming
<a href="{{ site.baseurl }}/java/README.html">Java</a>
<a href="{{ site.baseurl }}/python/README.html">Python</a>
"""
        (docs_dir / 'index.md').write_text(index_content)
        (docs_dir / '_config.yml').write_text(yaml.dump({
            'theme': 'minimal',
            'baseurl': '/daily-program',
            'url': 'https://brickea.github.io'
        }))

        for lang in ['java', 'python', 'go', 'ruby']:
            lang_dir = docs_dir / lang
            lang_dir.mkdir(exist_ok=True)
            (lang_dir / 'README.md').write_text(f'# {lang.title()}')

        result = main()
        self.assertEqual(result, 0)

    def test_main_some_fail(self):
        """Test main returns 1 when some validations fail."""
        # Create incomplete structure (missing docs)
        workflows_dir = Path('.github/workflows')
        workflows_dir.mkdir(parents=True, exist_ok=True)

        workflows = {
            'daily-learning.yml': {'name': 'Daily Learning Docs', 'jobs': {'test': {}}},
            'daily-feedback.yml': {'name': 'Daily Feedback Summary', 'jobs': {'test': {}}},
            'pages-deploy.yml': {
                'name': 'Pages Deploy',
                'on': {
                    'workflow_run': {
                        'workflows': ['Daily Learning Docs', 'Daily Feedback Summary']
                    }
                },
                'jobs': {'deploy': {}}
            },
            'test-scripts.yml': {'name': 'Test Scripts', 'jobs': {'test': {}}}
        }

        for filename, content in workflows.items():
            with open(workflows_dir / filename, 'w') as f:
                yaml.dump(content, f)

        result = main()
        self.assertEqual(result, 1)


if __name__ == '__main__':
    unittest.main()
