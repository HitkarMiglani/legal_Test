"""
Utility script to load local documents into ChromaDB RAG system
Supports PDF, DOCX, and TXT files from a folder
"""
import os
from modules.document_rag_chromadb import ChromaDBRAGTool
from modules.document_processor import DocumentProcessor

def load_local_documents(
    folder_path: str,
    rag_storage_path: str = "chromadb_storage",
    recursive: bool = True
):
    """
    Load all documents from a local folder into ChromaDB
    
    Args:
        folder_path: Path to folder containing documents
        rag_storage_path: Path for ChromaDB storage
        recursive: Whether to search subfolders
    """
    
    print(f"🔍 Scanning folder: {folder_path}")
    print(f"📦 ChromaDB storage: {rag_storage_path}")
    print("=" * 60)
    
    # Initialize tools
    rag_tool = ChromaDBRAGTool(storage_path=rag_storage_path)
    doc_processor = DocumentProcessor(upload_folder="uploads")
    
    # Supported extensions
    supported_extensions = ['.pdf', '.docx', '.txt']
    
    # Find all documents
    documents_found = []
    
    if recursive:
        # Walk through all subdirectories
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if any(file.lower().endswith(ext) for ext in supported_extensions):
                    documents_found.append(os.path.join(root, file))
    else:
        # Only top-level directory
        for file in os.listdir(folder_path):
            if any(file.lower().endswith(ext) for ext in supported_extensions):
                documents_found.append(os.path.join(folder_path, file))
    
    print(f"\n✅ Found {len(documents_found)} documents\n")
    
    if not documents_found:
        print("❌ No documents found. Make sure your folder contains PDF, DOCX, or TXT files.")
        return
    
    # Process each document
    success_count = 0
    error_count = 0
    
    for i, file_path in enumerate(documents_found, 1):
        filename = os.path.basename(file_path)
        file_ext = os.path.splitext(filename)[1].lower().replace('.', '')
        
        print(f"\n[{i}/{len(documents_found)}] Processing: {filename}")
        
        try:
            # Extract text from document
            print(f"  📄 Extracting text...")
            result = doc_processor.process_document(file_path, file_ext)
            
            text = result['text']
            metadata = result['metadata']
            
            print(f"  ✓ Extracted {metadata['word_count']} words, {metadata['char_count']} characters")
            
            # Add to RAG system
            print(f"  🔄 Adding to ChromaDB...")
            
            # Use filename without extension as title
            title = os.path.splitext(filename)[0]
            
            # Add metadata
            doc_metadata = {
                'filename': filename,
                'file_type': file_ext,
                'file_path': file_path,
                'word_count': str(metadata['word_count']),
                'char_count': str(metadata['char_count'])
            }
            
            rag_result = rag_tool.add_document(
                content=text,
                title=title,
                metadata=doc_metadata
            )
            
            if rag_result['success']:
                print(f"  ✅ Success! Doc ID: {rag_result['doc_id']}")
                print(f"      - Chunks created: {rag_result['chunks_created']}")
                success_count += 1
            else:
                print(f"  ⚠️  {rag_result['message']}")
                if rag_result.get('existing'):
                    success_count += 1  # Count as success if already exists
                else:
                    error_count += 1
                    
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            error_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 SUMMARY")
    print("=" * 60)
    print(f"✅ Successfully loaded: {success_count}")
    print(f"❌ Errors: {error_count}")
    print(f"📚 Total documents in RAG: {len(rag_tool.index['documents'])}")
    
    # Show statistics
    stats = rag_tool.get_statistics()
    print(f"\n📈 RAG STATISTICS:")
    print(f"  - Total documents: {stats['total_documents']}")
    print(f"  - Total chunks: {stats['total_chunks']}")
    print(f"  - Total words: {stats['total_words']:,}")
    
    print("\n✨ Done! Your documents are now searchable via the API.")
    print("\nTest with:")
    print("  curl -X POST http://localhost:5000/api/rag/search \\")
    print('    -H "Authorization: Bearer YOUR_TOKEN" \\')
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"query": "your search query", "top_k": 5}\'')


def list_loaded_documents(rag_storage_path: str = "chromadb_storage"):
    """List all documents currently in ChromaDB"""
    
    rag_tool = ChromaDBRAGTool(storage_path=rag_storage_path)
    result = rag_tool.list_documents()
    
    print("\n📚 LOADED DOCUMENTS")
    print("=" * 60)
    
    if result['count'] == 0:
        print("No documents loaded yet.")
        return
    
    for doc in result['documents']:
        print(f"\n📄 {doc['title']}")
        print(f"   ID: {doc['doc_id']}")
        print(f"   Words: {doc['words']:,} | Chunks: {doc['chunks']}")
        print(f"   Added: {doc['added_at']}")
        if doc.get('metadata'):
            print(f"   File: {doc['metadata'].get('filename', 'N/A')}")
            print(f"   Type: {doc['metadata'].get('file_type', 'N/A')}")


def search_documents(query: str, top_k: int = 5, rag_storage_path: str = "chromadb_storage"):
    """Search loaded documents"""
    
    rag_tool = ChromaDBRAGTool(storage_path=rag_storage_path)
    result = rag_tool.search_documents(query, top_k)
    
    print(f"\n🔍 SEARCH RESULTS for: '{query}'")
    print("=" * 60)
    
    if not result['results']:
        print("No results found.")
        return
    
    for i, r in enumerate(result['results'], 1):
        print(f"\n{i}. {r['doc_title']}")
        print(f"   Similarity: {r['similarity']:.4f}")
        print(f"   Preview: {r['text'][:200]}...")


if __name__ == "__main__":
    import sys
    
    print("\n" + "=" * 60)
    print("📂 LOCAL DOCUMENT LOADER FOR CHROMADB RAG")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python load_local_documents.py <folder_path> [--list] [--search 'query']")
        print("\nExamples:")
        print("  # Load all documents from a folder")
        print('  python load_local_documents.py "C:\\Documents\\Legal"')
        print("\n  # Load documents (non-recursive)")
        print('  python load_local_documents.py "C:\\Documents\\Legal" --no-recursive')
        print("\n  # List loaded documents")
        print("  python load_local_documents.py --list")
        print("\n  # Search documents")
        print('  python load_local_documents.py --search "contract law"')
        print("\nSupported formats: PDF, DOCX, TXT")
        sys.exit(1)
    
    # Handle special commands
    if sys.argv[1] == "--list":
        list_loaded_documents()
    elif sys.argv[1] == "--search":
        if len(sys.argv) < 3:
            print("❌ Please provide a search query")
            sys.exit(1)
        search_documents(sys.argv[2])
    else:
        # Load documents
        folder_path = sys.argv[1]
        recursive = "--no-recursive" not in sys.argv
        
        if not os.path.exists(folder_path):
            print(f"❌ Folder not found: {folder_path}")
            sys.exit(1)
        
        if not os.path.isdir(folder_path):
            print(f"❌ Not a folder: {folder_path}")
            sys.exit(1)
        
        load_local_documents(folder_path, recursive=recursive)
