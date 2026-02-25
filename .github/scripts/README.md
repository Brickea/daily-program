# GitHub Actions Scripts

This directory contains Python scripts used by GitHub Actions workflows to generate daily learning documentation.

## Scripts

### `generate_daily_learning.py`
Generates daily learning documentation files for Java, Python, Go, and Ruby.

**Usage:**
```bash
python generate_daily_learning.py
```

**Output:**
- Creates `docs/{language}/daily/{YYYY-MM-DD}.md` files for each language
- Sets `today` output variable for GitHub Actions

**Features:**
- Handles Chinese characters properly with UTF-8 encoding
- Skips files that already exist (no overwrites)
- Creates directory structure automatically

### `generate_daily_feedback.py`
Generates daily feedback and planning documentation files.

**Usage:**
```bash
python generate_daily_feedback.py
```

**Output:**
- Creates `docs/{language}/daily/{YYYY-MM-DD}.md` files for tomorrow's date
- Links to yesterday's file if it exists
- Sets `tomorrow` output variable for GitHub Actions

**Features:**
- Handles Chinese characters properly with UTF-8 encoding
- References yesterday's documentation when available
- Skips files that already exist (no overwrites)

### `validate_all.py`
Comprehensive validation script for all workflows and configurations.

**Usage:**
```bash
python validate_all.py
```

**Checks:**
- YAML syntax validation for all workflow files
- Workflow integration (Pages Deploy triggers correctly)
- GitHub Pages directory structure
- Python scripts existence and permissions

## Testing

### Unit Tests

Run all unit tests:
```bash
# Test generate_daily_learning.py
python -m unittest test_generate_daily_learning.py -v

# Test generate_daily_feedback.py
python -m unittest test_generate_daily_feedback.py -v
```

### Test Coverage

**`test_generate_daily_learning.py`** (8 tests):
- Language title mapping (known and unknown languages)
- New document generation
- Existing document handling (no overwrites)
- Chinese character encoding
- All languages support
- Main function with GITHUB_OUTPUT
- Main function with no new files

**`test_generate_daily_feedback.py`** (10 tests):
- Language title mapping (known and unknown languages)
- New feedback document generation
- Feedback with existing yesterday file
- Feedback without yesterday file
- Existing document handling (no overwrites)
- Chinese character encoding
- All languages support
- Main function with GITHUB_OUTPUT
- Main function with no new files

### CI/CD Testing

The `.github/workflows/test-scripts.yml` workflow automatically runs:
- All unit tests on push/pull request
- YAML syntax validation for all workflows

## Why Python Scripts?

Previously, these operations were done using bash heredocs in YAML files, which caused issues:

1. **YAML Syntax Errors**: Heredocs with list-like content (lines starting with `-`) can cause YAML parsing errors
2. **Character Encoding**: Complex Chinese characters are harder to manage in bash heredocs
3. **Maintainability**: Python scripts are easier to read, test, and modify
4. **Testing**: Python code can be unit tested, bash heredocs cannot

## Workflow Integration

### Daily Learning Workflow
- **File**: `.github/workflows/daily-learning.yml`
- **Schedule**: 07:00 UTC daily
- **Trigger**: Cron schedule or manual dispatch
- **Steps**:
  1. Checkout repository
  2. Setup Python
  3. Run `generate_daily_learning.py`
  4. Commit and push if files were created

### Daily Feedback Workflow
- **File**: `.github/workflows/daily-feedback.yml`
- **Schedule**: 00:00 UTC daily
- **Trigger**: Cron schedule or manual dispatch
- **Steps**:
  1. Checkout repository
  2. Setup Python
  3. Run `generate_daily_feedback.py`
  4. Commit and push if files were created

### Pages Deploy Workflow
- **File**: `.github/workflows/pages-deploy.yml`
- **Trigger**: On completion of Daily Learning or Daily Feedback workflows
- **Condition**: Only runs if triggering workflow succeeded
- **Steps**:
  1. Checkout repository at the triggering commit
  2. Setup GitHub Pages
  3. Upload `docs/` directory as artifact
  4. Deploy to GitHub Pages

## Adding a New Language

To add support for a new language:

1. Update both `generate_daily_learning.py` and `generate_daily_feedback.py`:
   ```python
   # In get_language_title()
   lang_titles = {
       'java': 'Java',
       'python': 'Python',
       'go': 'Go',
       'ruby': 'Ruby',
       'rust': 'Rust',  # Add new language
   }

   # In main()
   languages = ['java', 'python', 'go', 'ruby', 'rust']  # Add to list
   ```

2. Create the documentation structure:
   ```bash
   mkdir -p docs/rust
   ```

3. Add a README.md for the language in `docs/rust/README.md`

4. Update tests to include the new language

5. Run validation:
   ```bash
   python validate_all.py
   python -m unittest test_generate_daily_learning.py
   python -m unittest test_generate_daily_feedback.py
   ```

## Troubleshooting

### Scripts not executing in CI
Ensure scripts are executable:
```bash
chmod +x .github/scripts/*.py
```

### YAML syntax errors
Run validation:
```bash
python validate_all.py
```

### Tests failing locally
Ensure you're in the scripts directory:
```bash
cd .github/scripts
python -m unittest test_generate_daily_learning.py -v
```

### Files not being committed
Check that:
1. Scripts successfully generated files (check script output)
2. Git config is set in the workflow
3. There are actual changes to commit (`git status --porcelain` returns results)

## Best Practices

1. **Never use heredocs for complex strings** - Use Python scripts instead
2. **Always test changes** - Run unit tests before committing
3. **Validate YAML** - Run `validate_all.py` after modifying workflows
4. **UTF-8 encoding** - Always specify `encoding='utf-8'` when writing files
5. **Check file existence** - Don't overwrite existing documentation
