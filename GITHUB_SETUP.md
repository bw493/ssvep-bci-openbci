# GitHub Repository Setup Guide

This guide will help you push the SSVEP BCI project to GitHub.

## Prerequisites

1. Git installed on your system
2. GitHub account
3. Repository already created at: https://github.com/bw493/ssvep-bci-openbci

## Step-by-Step Instructions

### 1. Navigate to Project Directory

```bash
cd /path/to/ssvep_bci
```

On Windows (PowerShell):
```powershell
cd C:\Users\minen\Documents\code\ssvep_bci
```

### 2. Initialize Git Repository (if not already done)

```bash
git init
```

### 3. Add All Files

```bash
git add .
```

### 4. Create Initial Commit

```bash
git commit -m "Initial commit: Complete SSVEP BCI implementation with OpenBCI data"
```

### 5. Add Remote Repository

```bash
git remote add origin https://github.com/bw493/ssvep-bci-openbci.git
```

If remote already exists, update it:
```bash
git remote set-url origin https://github.com/bw493/ssvep-bci-openbci.git
```

### 6. Pull Any Existing Content (if repository not empty)

```bash
git pull origin main --allow-unrelated-histories
```

If there's a merge conflict or editor opens:
- Save and close the editor (default merge message is fine)

### 7. Push to GitHub

```bash
git push -u origin main
```

If this fails with "non-fast-forward" error:
```bash
git push -u origin main --force
```

⚠️ **Warning**: `--force` will overwrite any existing content on GitHub. Only use if you're sure.

## Verifying the Upload

After pushing, visit:
https://github.com/bw493/ssvep-bci-openbci

You should see:
- ✓ All Python modules (preprocessing, features, classification, control)
- ✓ Configuration files
- ✓ Scripts (run_pipeline.py, convert_openbci_data.py, etc.)
- ✓ README.md
- ✓ requirements.txt
- ✓ Raw data files in data/raw/

## Troubleshooting

### Authentication Issues

If prompted for credentials:
1. Use your GitHub username
2. For password, use a Personal Access Token (not your account password)
   - Create token at: https://github.com/settings/tokens
   - Select scopes: `repo` (full control of private repositories)

### Large File Warnings

If you get warnings about large files (>50MB):
```bash
# Add data directory to .gitignore
echo "data/*.fif" >> .gitignore
echo "data/raw/*" >> .gitignore
git add .gitignore
git commit -m "Update .gitignore to exclude large data files"
```

Then push again:
```bash
git push -u origin main
```

### Repository Already Has Content

If the GitHub repo already has files:

**Option A: Merge histories (keeps both)**
```bash
git pull origin main --allow-unrelated-histories
git push -u origin main
```

**Option B: Replace everything (clean slate)**
```bash
git push -u origin main --force
```

## After Successful Push

### Add a Description to Your Repository

1. Go to https://github.com/bw493/ssvep-bci-openbci
2. Click "About" settings (gear icon)
3. Add description: "SSVEP-based Brain-Computer Interface for bionic hand control using OpenBCI and Arduino"
4. Add topics: `bci`, `eeg`, `openbci`, `ssvep`, `brain-computer-interface`, `arduino`, `python`

### Create a Release Tag

```bash
git tag -a v1.0.0 -m "Version 1.0.0: Initial release"
git push origin v1.0.0
```

### Enable GitHub Pages (Optional)

For documentation hosting:
1. Go to repository Settings
2. Scroll to "Pages" section
3. Select source: main branch, /docs folder or root
4. Save

## Keeping Repository Updated

### After making changes:

```bash
# See what changed
git status

# Add changes
git add .

# Commit with message
git commit -m "Describe your changes here"

# Push to GitHub
git push
```

### Quick update command:
```bash
git add . && git commit -m "Update" && git push
```

## File Size Considerations

GitHub has limits:
- Files > 50MB: Warning
- Files > 100MB: Rejected

Your data files:
- OpenBCI-RAW-2026-02-26_19-22-57.txt: 8.6MB ✓
- OpenBCI-RAW-2026-02-26_19-35-13.txt: 7.5MB ✓
- OpenBCI-RAW-2026-02-23_19-06-24.txt: 8.2MB ✓
- BrainFlow-RAW_2026-02-23_19-05-38_0.csv: 7.4MB ✓

All files are within limits!

## Next Steps

1. Add collaborators (if working with team)
   - Settings → Collaborators → Add people

2. Set up Issues and Projects
   - Use Issues tab for bug tracking
   - Use Projects for task management

3. Add CI/CD (optional)
   - GitHub Actions for automated testing
   - See `.github/workflows/` for examples

## Getting Help

- GitHub Docs: https://docs.github.com
- Git Basics: https://git-scm.com/book/en/v2
- If stuck: Check `git status` to see what state you're in
