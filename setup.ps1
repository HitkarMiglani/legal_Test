# LuminaryAI Setup Script (PowerShell)
# Run this script to set up the application

Write-Host "Setting up LuminaryAI..." -ForegroundColor Cyan

# Check Python version
Write-Host "`nChecking Python version..." -ForegroundColor Yellow
python --version

# Create virtual environment
Write-Host "`nCreating virtual environment..." -ForegroundColor Yellow
python -m venv env

# Activate virtual environment
Write-Host "`nActivating virtual environment..." -ForegroundColor Yellow
& ".\env\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "`nUpgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install requirements
Write-Host "`nInstalling dependencies (this may take a few minutes)..." -ForegroundColor Yellow
pip install -r requirements.txt

# Create .env file
Write-Host "`nSetting up environment file..." -ForegroundColor Yellow
if (-Not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env file. Please edit it with your API keys." -ForegroundColor Green
} else {
    Write-Host ".env file already exists. Skipping..." -ForegroundColor Yellow
}

# Generate Fernet key
Write-Host "`nGenerating encryption key..." -ForegroundColor Yellow
$fernetCmd = "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
$fernetKey = python -c $fernetCmd
Write-Host "Your Fernet Key: $fernetKey" -ForegroundColor Cyan
Write-Host "Add this to your .env file as FERNET_KEY=$fernetKey" -ForegroundColor Cyan

# Create uploads directory
Write-Host "`nCreating uploads directory..." -ForegroundColor Yellow
if (-Not (Test-Path "uploads")) {
    New-Item -ItemType Directory -Path "uploads" | Out-Null
    Write-Host "Created uploads directory" -ForegroundColor Green
}

# Initialize database
Write-Host "`nInitializing database..." -ForegroundColor Yellow
$dbCmd = "from models import init_db; init_db(); print('Database initialized successfully!')"
python -c $dbCmd

Write-Host "`nSetup complete!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env file with your API keys (especially GOOGLE_API_KEY)" -ForegroundColor White
Write-Host "2. Run Flask backend: python app.py" -ForegroundColor White
Write-Host "3. Run Streamlit frontend: streamlit run main.py" -ForegroundColor White
Write-Host "`nSee SETUP.md for detailed instructions" -ForegroundColor Cyan
