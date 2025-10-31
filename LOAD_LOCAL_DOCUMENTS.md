# 📂 Loading Local Documents into RAG

## 🎯 How to Access Your Local Documents

You now have **3 ways** to add your local documents to the RAG system:

---

## ✨ Method 1: Batch Load Script (Easiest!)

### Load All Documents from a Folder

```powershell
# Load all PDF, DOCX, TXT files from a folder (recursive)
python load_local_documents.py "C:\Users\Admin\Documents\Legal"

# Load from current folder
python load_local_documents.py ".\my_documents"

# Load without searching subfolders
python load_local_documents.py "C:\Documents" --no-recursive
```

### What It Does:
- 🔍 Scans folder for PDF, DOCX, TXT files
- 📄 Extracts text from each document
- 🤖 Generates embeddings (locally, no API!)
- 💾 Stores in ChromaDB
- ✅ Makes documents searchable via API

### Example Output:
```
🔍 Scanning folder: C:\Documents\Legal
📦 ChromaDB storage: chromadb_storage
============================================================

✅ Found 5 documents

[1/5] Processing: Contract_Agreement.pdf
  📄 Extracting text...
  ✓ Extracted 2,456 words, 14,523 characters
  🔄 Adding to ChromaDB...
  ✅ Success! Doc ID: a1b2c3d4e5f6g7h8
      - Chunks created: 8

[2/5] Processing: IPC_Section_420.docx
  📄 Extracting text...
  ✓ Extracted 1,234 words, 7,890 characters
  🔄 Adding to ChromaDB...
  ✅ Success! Doc ID: h8g7f6e5d4c3b2a1
      - Chunks created: 5

============================================================
📊 SUMMARY
============================================================
✅ Successfully loaded: 5
❌ Errors: 0
📚 Total documents in RAG: 5

📈 RAG STATISTICS:
  - Total documents: 5
  - Total chunks: 27
  - Total words: 8,945
```

---

## 📋 Method 2: List & Search (Check What's Loaded)

### List All Loaded Documents
```powershell
python load_local_documents.py --list
```

Output:
```
📚 LOADED DOCUMENTS
============================================================

📄 Contract_Agreement
   ID: a1b2c3d4e5f6g7h8
   Words: 2,456 | Chunks: 8
   Added: 2025-10-30T23:15:00
   File: Contract_Agreement.pdf
   Type: pdf

📄 IPC_Section_420
   ID: h8g7f6e5d4c3b2a1
   Words: 1,234 | Chunks: 5
   Added: 2025-10-30T23:15:30
   File: IPC_Section_420.docx
   Type: docx
```

### Search Loaded Documents
```powershell
python load_local_documents.py --search "contract law"
```

Output:
```
🔍 SEARCH RESULTS for: 'contract law'
============================================================

1. Contract_Agreement
   Similarity: 0.8765
   Preview: This contract agreement is entered into between Party A and Party B...

2. Legal_Framework
   Similarity: 0.7543
   Preview: Under contract law in India, agreements must satisfy certain conditions...
```

---

## 🌐 Method 3: Via API (Programmatic)

### Add Single Document via API
```powershell
# Get auth token first
$token = "YOUR_JWT_TOKEN"

# Add document via API
curl -X POST http://localhost:5000/api/rag/documents `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d '{
    "content": "Your document text here...",
    "title": "My Document Title",
    "metadata": {
      "type": "contract",
      "date": "2025-10-30"
    }
  }'
```

### Upload File via API
```powershell
# Upload document file
curl -X POST http://localhost:5000/api/documents/upload `
  -H "Authorization: Bearer $token" `
  -F "file=@C:\Documents\contract.pdf"
```

---

## 🔍 After Loading: How to Use

### 1. Search via API
```powershell
curl -X POST http://localhost:5000/api/rag/search `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d '{
    "query": "What is breach of contract?",
    "top_k": 5
  }'
```

### 2. Query Specific Document
```powershell
curl -X POST http://localhost:5000/api/rag/documents/a1b2c3d4e5f6g7h8/query `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d '{
    "question": "What are the payment terms?"
  }'
```

### 3. Regular Chat (Auto-Searches Documents!)
```powershell
curl -X POST http://localhost:5000/api/query `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d '{
    "query": "What does my contract say about termination?"
  }'
```
**The chat automatically searches your loaded documents!**

### 4. Autonomous Agent (Advanced)
```powershell
curl -X POST http://localhost:5000/api/agent/query `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d '{
    "query": "Compare all my contracts and find common clauses",
    "verbose": true
  }'
```
**The agent autonomously searches, compares, and analyzes your documents!**

---

## 📁 Supported File Types

| Format | Extension | Support |
|--------|-----------|---------|
| PDF | `.pdf` | ✅ Full |
| Word | `.docx` | ✅ Full |
| Text | `.txt` | ✅ Full |

---

## 🎯 Quick Start Examples

### Example 1: Load Your Legal Documents
```powershell
# Navigate to your project
cd C:\Users\Admin\Music\PBLV\LegalAI3\Agentic_Law_AI

# Load all documents from your folder
python load_local_documents.py "C:\Users\Admin\Documents\Legal"

# Check what was loaded
python load_local_documents.py --list

# Test search
python load_local_documents.py --search "contract"
```

### Example 2: Load and Query via Chat
```powershell
# 1. Load documents
python load_local_documents.py ".\my_legal_docs"

# 2. Start server
python app.py

# 3. Register/login to get token
# 4. Query via chat - it automatically searches your docs!
curl -X POST http://localhost:5000/api/query `
  -H "Authorization: Bearer $token" `
  -d '{"query": "What are the terms in my contracts?"}'
```

---

## 💡 Pro Tips

### 1. **Organize Your Documents**
```
Legal_Documents/
├── Contracts/
│   ├── Service_Agreement.pdf
│   └── Employment_Contract.docx
├── Cases/
│   ├── Supreme_Court_Cases.pdf
│   └── High_Court_Judgments.pdf
└── Reference/
    └── IPC_Sections.txt
```

### 2. **Incremental Loading**
```powershell
# Load one folder at a time
python load_local_documents.py ".\Legal_Documents\Contracts"
python load_local_documents.py ".\Legal_Documents\Cases"

# Check progress
python load_local_documents.py --list
```

### 3. **Re-running is Safe**
- Already loaded documents are skipped
- No duplicates created
- Safe to re-run the script

### 4. **Metadata is Preserved**
Each loaded document stores:
- Original filename
- File type
- File path
- Word count
- Character count

---

## 🗄️ Storage Location

Your documents are stored in:
```
chromadb_storage/
├── chroma.sqlite3          # ChromaDB database
├── xxxxxxxx-xxxx-xxxx/     # Vector data
├── documents/              # Original text files
└── index.json              # Document index
```

**Backup this folder to preserve your RAG database!**

---

## ⚡ Performance

### Loading Speed
- Small doc (1-2 pages): ~1-2 seconds
- Medium doc (10-20 pages): ~3-5 seconds
- Large doc (50+ pages): ~10-15 seconds

### Search Speed
- Search query: ~0.1-0.3 seconds (local!)
- No API delays
- No quota limits

---

## 🎉 Summary

**Before:**
- ❌ Documents on local drive
- ❌ Not searchable
- ❌ Can't be queried by AI

**After:**
```powershell
python load_local_documents.py "C:\My\Documents"
```

- ✅ All documents loaded into RAG
- ✅ Semantically searchable
- ✅ AI can query and analyze them
- ✅ Works offline
- ✅ No API costs
- ✅ Unlimited usage

**Your local documents are now AI-powered!** 🚀

---

*Need help? Check CHROMADB_MIGRATION.md for technical details.*
