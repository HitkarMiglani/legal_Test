#!/bin/bash
# LuminaryAI Setup Script (Bash)
# Run this script to set up the application

echo "🚀 Setting up LuminaryAI..."

# Check Python version
echo ""
echo "📌 Checking Python version..."
python3 --version

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
python -m pip install --upgrade pip

# Install requirements
echo ""
echo "📚 Installing dependencies (this may take a few minutes)..."
pip install -r requirements.txt

# Create .env file
echo ""
echo "⚙️  Setting up environment file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file. Please edit it with your API keys."
else
    echo "⚠️  .env file already exists. Skipping..."
fi

# Generate Fernet key
echo ""
echo "🔐 Generating encryption key..."
FERNET_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
echo "Your Fernet Key: $FERNET_KEY"
echo "Add this to your .env file as FERNET_KEY=$FERNET_KEY"

# Create uploads directory
echo ""
echo "📁 Creating uploads directory..."
mkdir -p uploads
echo "✅ Created uploads directory"

# Initialize database
echo ""
echo "🗄️  Initializing database..."
python -c "from models import init_db; init_db(); print('Database initialized successfully!')"

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Edit .env file with your API keys (especially GOOGLE_API_KEY)"
echo "2. Run Flask backend: python app.py"
echo "3. Run Streamlit frontend: streamlit run main.py"
echo ""
echo "📖 See SETUP.md for detailed instructions"
