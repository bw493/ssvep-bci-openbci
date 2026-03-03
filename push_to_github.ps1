# PowerShell script to push project to GitHub
# Run this from the project root directory

Write-Host "=================================" -ForegroundColor Cyan
Write-Host "SSVEP BCI - GitHub Push Script" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is installed
try {
    git --version | Out-Null
} catch {
    Write-Host "Error: Git is not installed!" -ForegroundColor Red
    Write-Host "Install Git from: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

Write-Host "Git found: " -NoNewline
git --version

Write-Host ""

# Check if we're in a git repository
if (-not (Test-Path ".git")) {
    Write-Host "Initializing Git repository..." -ForegroundColor Yellow
    git init
    Write-Host "✓ Git initialized" -ForegroundColor Green
} else {
    Write-Host "✓ Git repository already exists" -ForegroundColor Green
}

Write-Host ""

# Add all files
Write-Host "Adding files to Git..." -ForegroundColor Yellow
git add .
Write-Host "✓ Files added" -ForegroundColor Green

Write-Host ""

# Create commit
Write-Host "Creating commit..." -ForegroundColor Yellow
$commitMessage = "Complete SSVEP BCI implementation with collected OpenBCI data"
git commit -m $commitMessage
Write-Host "✓ Commit created" -ForegroundColor Green

Write-Host ""

# Add remote (if not exists)
$remoteUrl = "https://github.com/bw493/ssvep-bci-openbci.git"
$remoteExists = git remote get-url origin 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "Remote 'origin' already exists" -ForegroundColor Yellow
    Write-Host "Current remote: $remoteExists"
    $response = Read-Host "Update remote URL? (y/n)"
    if ($response -eq 'y') {
        git remote set-url origin $remoteUrl
        Write-Host "✓ Remote URL updated" -ForegroundColor Green
    }
} else {
    Write-Host "Adding remote repository..." -ForegroundColor Yellow
    git remote add origin $remoteUrl
    Write-Host "✓ Remote added" -ForegroundColor Green
}

Write-Host ""

# Pull any existing content
Write-Host "Checking remote repository..." -ForegroundColor Yellow
try {
    git pull origin main --allow-unrelated-histories 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Pulled existing content" -ForegroundColor Green
    }
} catch {
    Write-Host "No existing content to pull" -ForegroundColor Yellow
}

Write-Host ""

# Push to GitHub
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
Write-Host ""

$pushed = $false
$tryForce = $false

# Try normal push first
git push -u origin main 2>&1 | Tee-Object -Variable pushOutput

if ($LASTEXITCODE -eq 0) {
    $pushed = $true
} else {
    # Check if it's a non-fast-forward error
    if ($pushOutput -match "non-fast-forward|rejected") {
        Write-Host ""
        Write-Host "Warning: Remote has different history" -ForegroundColor Yellow
        Write-Host "This usually happens when the remote repo already has commits" -ForegroundColor Yellow
        Write-Host ""
        $response = Read-Host "Force push? This will OVERWRITE remote content (y/n)"
        
        if ($response -eq 'y') {
            Write-Host "Force pushing..." -ForegroundColor Yellow
            git push -u origin main --force
            if ($LASTEXITCODE -eq 0) {
                $pushed = $true
                $tryForce = $true
            }
        }
    }
}

Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan

if ($pushed) {
    Write-Host "✓ SUCCESS!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your code is now on GitHub!" -ForegroundColor Green
    Write-Host "View it at: https://github.com/bw493/ssvep-bci-openbci" -ForegroundColor Cyan
    
    if ($tryForce) {
        Write-Host ""
        Write-Host "Note: Used force push - remote history was overwritten" -ForegroundColor Yellow
    }
} else {
    Write-Host "✗ Push failed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Make sure you're logged in to GitHub" -ForegroundColor White
    Write-Host "2. Check your internet connection" -ForegroundColor White
    Write-Host "3. Verify repository URL is correct" -ForegroundColor White
    Write-Host "4. See GITHUB_SETUP.md for detailed instructions" -ForegroundColor White
    Write-Host ""
    Write-Host "For authentication, you may need a Personal Access Token:" -ForegroundColor Yellow
    Write-Host "Create one at: https://github.com/settings/tokens" -ForegroundColor Cyan
}

Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Pause so user can read the output
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
