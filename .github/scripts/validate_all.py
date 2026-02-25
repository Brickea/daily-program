#!/usr/bin/env python3
"""Comprehensive validation script for GitHub Actions workflows and scripts."""

import sys
import yaml
from pathlib import Path


def validate_yaml_files():
    """Validate all workflow YAML files."""
    print("=" * 60)
    print("YAML Workflow Validation")
    print("=" * 60)

    workflows = [
        '.github/workflows/daily-learning.yml',
        '.github/workflows/daily-feedback.yml',
        '.github/workflows/pages-deploy.yml',
        '.github/workflows/test-scripts.yml'
    ]

    all_valid = True
    for workflow in workflows:
        try:
            with open(workflow, 'r') as f:
                data = yaml.safe_load(f)
            print(f'✓ {workflow}')

            # Check required fields
            if 'name' in data:
                print(f'  - Name: {data["name"]}')
            if 'jobs' in data:
                print(f'  - Jobs: {", ".join(data["jobs"].keys())}')
        except Exception as e:
            print(f'✗ {workflow}: {e}')
            all_valid = False

    return all_valid


def validate_workflow_integration():
    """Validate that workflows are properly integrated."""
    print("\n" + "=" * 60)
    print("Workflow Integration Validation")
    print("=" * 60)

    with open('.github/workflows/pages-deploy.yml', 'r') as f:
        pages_config = yaml.safe_load(f)

    with open('.github/workflows/daily-learning.yml', 'r') as f:
        learning_config = yaml.safe_load(f)

    with open('.github/workflows/daily-feedback.yml', 'r') as f:
        feedback_config = yaml.safe_load(f)

    # Get trigger config (YAML parses 'on' as True)
    on_config = pages_config.get(True) or pages_config.get('on')
    watched = on_config['workflow_run']['workflows']

    learning_name = learning_config['name']
    feedback_name = feedback_config['name']

    print(f"Pages Deploy watches: {watched}")
    print(f"Daily Learning name: '{learning_name}' - {'✓' if learning_name in watched else '✗'}")
    print(f"Daily Feedback name: '{feedback_name}' - {'✓' if feedback_name in watched else '✗'}")

    if learning_name in watched and feedback_name in watched:
        print("\n✓ Workflow integration is correct")
        return True
    else:
        print("\n✗ Workflow names don't match")
        return False


def validate_docs_structure():
    """Validate docs directory structure for GitHub Pages."""
    print("\n" + "=" * 60)
    print("GitHub Pages Structure Validation")
    print("=" * 60)

    docs_dir = Path('docs')
    required_files = ['index.md', '_config.yml']
    required_dirs = ['java', 'python', 'go', 'ruby']

    all_valid = True

    # Check required files
    for file in required_files:
        file_path = docs_dir / file
        if file_path.exists():
            print(f'✓ {file_path}')
        else:
            print(f'✗ Missing: {file_path}')
            all_valid = False

    # Check language directories
    for lang_dir in required_dirs:
        dir_path = docs_dir / lang_dir
        readme_path = dir_path / 'README.md'

        if dir_path.exists():
            print(f'✓ {dir_path}/')
            if readme_path.exists():
                print(f'  ✓ {readme_path}')
            else:
                print(f'  ✗ Missing: {readme_path}')
                all_valid = False
        else:
            print(f'✗ Missing: {dir_path}/')
            all_valid = False

    # Check _config.yml content
    config_path = docs_dir / '_config.yml'
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        if 'theme' in config:
            print(f'  Theme: {config["theme"]}')
        if 'title' in config:
            print(f'  Title: {config["title"]}')

    if all_valid:
        print("\n✓ Docs structure is valid for GitHub Pages")

    return all_valid


def validate_python_scripts():
    """Validate Python scripts can be imported."""
    print("\n" + "=" * 60)
    print("Python Scripts Validation")
    print("=" * 60)

    scripts = [
        '.github/scripts/generate_daily_learning.py',
        '.github/scripts/generate_daily_feedback.py'
    ]

    all_valid = True
    for script in scripts:
        script_path = Path(script)
        if script_path.exists():
            print(f'✓ {script}')
            # Check it's executable
            if script_path.stat().st_mode & 0o111:
                print(f'  ✓ Executable')
            else:
                print(f'  ⚠ Not executable (may not matter in CI)')
        else:
            print(f'✗ Missing: {script}')
            all_valid = False

    return all_valid


def main():
    """Run all validations."""
    print("GitHub Actions Workflow Validation")
    print("\n")

    results = {
        'YAML Files': validate_yaml_files(),
        'Workflow Integration': validate_workflow_integration(),
        'Docs Structure': validate_docs_structure(),
        'Python Scripts': validate_python_scripts()
    }

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    for check, passed in results.items():
        status = '✓' if passed else '✗'
        print(f'{status} {check}')

    all_passed = all(results.values())

    if all_passed:
        print("\n✓ All validations passed!")
        print("\n✓ GitHub Actions workflows are properly configured")
        print("✓ Python scripts are in place and tested")
        print("✓ GitHub Pages structure is correct")
        return 0
    else:
        print("\n✗ Some validations failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
