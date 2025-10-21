# LuminaryAI - Setup and Installation Guide

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.9 or higher
- pip package manager
- Virtual environment (recommended)

### 2. Installation Steps

#### Clone the repository (if from Git)

```bash
git clone https://github.com/yourusername/LuminaryAI.git
cd LuminaryAI
```

#### Create virtual environment

```powershell
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configuration

#### Copy environment file

```powershell
Copy-Item .env.example .env
```

#### Edit `.env` file and add your API keys:

- `GOOGLE_API_KEY` - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- `INDIAN_KANOON_API_KEY` - Optional, for legal case search
- `FLASK_SECRET_KEY` - Generate a random string
- `JWT_SECRET_KEY` - Generate a random string
- `FERNET_KEY` - Run: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`

### 4. Initialize Database

```powershell
python -c "from models import init_db; init_db()"
```

### 5. Run the Application

#### Terminal 1 - Start Flask Backend

```powershell
python app.py
```

#### Terminal 2 - Start Streamlit Frontend

```powershell
streamlit run main.py
```

### 6. Access the Application

- **Frontend (Streamlit):** http://localhost:8501
- **Backend API:** http://localhost:5000
- **API Documentation:** http://localhost:5000/

## 🔑 Getting API Keys

### Google Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and add to `.env` file

### Indian Kanoon API (Optional)

Contact Indian Kanoon for API access or use the default mock implementation.

## 📁 Project Structure

```
LuminaryAI/
├── app.py                  # Flask backend
├── main.py                 # Streamlit frontend
├── config.py               # Configuration management
├── models.py               # Database models
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
├── modules/               # Core modules
│   ├── auth.py           # Authentication
│   ├── document_processor.py
│   ├── embeddings.py
│   ├── legal_retriever.py
│   ├── memory_manager.py
│   ├── orchestrator.py
│   └── reasoning_engine.py
└── uploads/               # Uploaded documents (auto-created)
```

## 🎯 Usage Examples

### Register a New User

1. Open http://localhost:8501
2. Click "Register" tab
3. Fill in details and select role (Public/Student/Lawyer)
4. Click "Register"

### Upload and Analyze Document

1. Login to the application
2. Go to "Document Analysis"
3. Upload PDF/DOCX/TXT file
4. Enter analysis query
5. Click "Analyze Document"

### Ask Legal Questions

1. Go to "Legal Assistant"
2. Type your legal question
3. Get AI-powered response with relevant case law

### Search Legal Cases

1. Go to "Legal Research"
2. Enter search terms
3. Browse results

## 🔧 Troubleshooting

### Import Errors

```powershell
pip install --upgrade -r requirements.txt
```

### Database Errors

```powershell
# Delete existing database and reinitialize
Remove-Item luminary.db
python -c "from models import init_db; init_db()"
```

### API Connection Errors

- Verify Flask backend is running on port 5000
- Check firewall settings
- Ensure correct API_BASE_URL in environment

### Module Not Found

```powershell
# Ensure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

## 🔒 Security Notes

- Never commit `.env` file to version control
- Use strong secrets for production
- Change default database in production
- Enable HTTPS for production deployment
- Regularly update dependencies

## 📊 Production Deployment

### Using Gunicorn (Backend)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Docker

See `Dockerfile` for containerization (create if needed)

### Environment Variables for Production

- Set `FLASK_ENV=production`
- Use PostgreSQL instead of SQLite
- Configure proper CORS settings
- Set up proper logging
- Use environment-specific secrets

## 🆘 Support

For issues and questions:

- Email: support@luminaryai.in
- GitHub Issues: github.com/yourusername/LuminaryAI/issues

## ⚖️ Legal Disclaimer

This application provides AI-generated legal information for educational purposes only.
Always consult a qualified legal professional for legal advice.
