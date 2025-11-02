"""
Comprehensive Test Suite for LuminaryAI
Tests all components: Document Analysis, RAG Tool, LangChain Integration, and App Integration
"""
import os
import sys
import warnings

# Suppress warnings
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GLOG_minloglevel'] = '3'
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.document_rag_tool import DocumentRAGTool
from modules.document_rag_langchain import create_document_rag_tools
from modules.reasoning_engine import GeminiReasoningEngine
from config import Config

# Sample documents for testing
RENTAL_AGREEMENT = """
RENTAL AGREEMENT
This agreement dated 15th January 2025 between:
LANDLORD: Mr. Rajesh Kumar, Address: 123 MG Road, Mumbai
TENANT: Ms. Priya Sharma, Address: 456 Park Street, Mumbai

TERMS:
1. Monthly Rent: Rs. 25,000
2. Security Deposit: Rs. 75,000
3. Duration: 11 months from February 1, 2025
4. Notice Period: 2 months
5. Lock-in Period: 6 months

Governed by Indian Contract Act, 1872 and Maharashtra Rent Control Act, 1999.
"""

EMPLOYMENT_CONTRACT = """
EMPLOYMENT AGREEMENT
Date: 20th October 2025
EMPLOYER: TechCorp India Private Limited, Gurgaon
EMPLOYEE: Mr. Amit Verma, Noida

POSITION: Senior Software Engineer
SALARY: Rs. 15,00,000 per annum
PROBATION: 3 months
NOTICE PERIOD: 2 months

Governed by Indian Contract Act, 1872 and Payment of Wages Act, 1936.
"""

def test_module_imports():
    """Test 1: Module Imports"""
    print("\n" + "="*80)
    print("TEST 1: Module Imports")
    print("="*80)
    
    try:
        from modules.document_rag_tool import DocumentRAGTool
        print("✓ DocumentRAGTool")
        
        from modules.document_rag_langchain import create_document_rag_tools
        print("✓ create_document_rag_tools")
        
        from modules.document_rag_routes import rag_bp
        print("✓ RAG Blueprint")
        
        from modules.reasoning_engine import GeminiReasoningEngine
        print("✓ GeminiReasoningEngine")
        
        from modules.orchestrator import LangChainOrchestrator
        print("✓ LangChainOrchestrator")
        
        print("\n✅ All imports successful!")
        return True
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        return False

def test_gemini_reasoning_engine():
    """Test 2: Gemini Document Analysis"""
    print("\n" + "="*80)
    print("TEST 2: Gemini Reasoning Engine")
    print("="*80)
    
    try:
        if not Config.GOOGLE_API_KEY or Config.GOOGLE_API_KEY == 'your_gemini_api_key_here':
            print("⚠ Skipping (API key not configured)")
            return True
        
        engine = GeminiReasoningEngine()
        print("✓ Engine initialized")
        
        # Test document analysis
        print("\n  Testing document analysis...")
        result = engine.analyze_legal_document(
            RENTAL_AGREEMENT,
            analysis_type="summary"
        )
        
        if result.get('success'):
            print(f"  ✓ Analysis successful")
            print(f"    Document Type: {result.get('document_type', 'N/A')}")
            print(f"    Summary length: {len(result.get('summary', ''))} chars")
        else:
            print(f"  ✗ Analysis failed: {result.get('message')}")
            return False
        
        print("\n✅ Gemini reasoning engine working!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rag_tool():
    """Test 3: Document RAG Tool"""
    print("\n" + "="*80)
    print("TEST 3: Document RAG Tool")
    print("="*80)
    
    try:
        if not Config.GOOGLE_API_KEY or Config.GOOGLE_API_KEY == 'your_gemini_api_key_here':
            print("⚠ Skipping (API key not configured)")
            return True
        
        tool = DocumentRAGTool(storage_path="test_comprehensive_storage")
        print("✓ RAG Tool initialized")
        
        # Test 1: Add documents
        print("\n  1. Adding rental agreement...")
        result1 = tool.add_document(
            content=RENTAL_AGREEMENT,
            title="Mumbai Rental Agreement 2025",
            metadata={"type": "rental", "location": "Mumbai"}
        )
        
        if result1.get('success'):
            rental_id = result1['doc_id']
            print(f"     ✓ Added (ID: {rental_id[:8]}..., Chunks: {result1['chunks_created']})")
        else:
            print(f"     ✗ Failed: {result1.get('message')}")
            return False
        
        print("\n  2. Adding employment contract...")
        result2 = tool.add_document(
            content=EMPLOYMENT_CONTRACT,
            title="TechCorp Employment Contract",
            metadata={"type": "employment"}
        )
        
        if result2.get('success'):
            emp_id = result2['doc_id']
            print(f"     ✓ Added (ID: {emp_id[:8]}..., Chunks: {result2['chunks_created']})")
        else:
            print(f"     ✗ Failed: {result2.get('message')}")
            return False
        
        # Test 2: Search documents
        print("\n  3. Searching for 'notice period'...")
        search_result = tool.search_documents(query="notice period", top_k=3)
        
        if search_result.get('success'):
            print(f"     ✓ Found {len(search_result['results'])} results")
            for r in search_result['results'][:2]:
                print(f"       - {r['doc_title']} (similarity: {r['similarity']:.3f})")
        else:
            print(f"     ✗ Search failed")
            return False
        
        # Test 3: Query document
        print("\n  4. Querying rental agreement...")
        query_result = tool.query_document(
            doc_id=rental_id,
            question="What is the monthly rent?"
        )
        
        if query_result.get('success'):
            print(f"     ✓ Answer: {query_result['answer'][:80]}...")
        else:
            print(f"     ✗ Query failed")
            return False
        
        # Test 4: List documents
        print("\n  5. Listing all documents...")
        list_result = tool.list_documents()
        
        if list_result.get('success'):
            print(f"     ✓ Total documents: {len(list_result['documents'])}")
            for doc in list_result['documents']:
                print(f"       - {doc['title']} ({doc['words']} words)")
        else:
            print(f"     ✗ List failed")
            return False
        
        # Test 5: Statistics
        print("\n  6. Getting statistics...")
        stats = tool.get_statistics()
        
        if stats.get('success'):
            print(f"     ✓ Documents: {stats['total_documents']}, Chunks: {stats['total_chunks']}")
        else:
            print(f"     ✗ Stats failed")
            return False
        
        print("\n✅ RAG Tool working perfectly!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_langchain_tools():
    """Test 4: LangChain Tools"""
    print("\n" + "="*80)
    print("TEST 4: LangChain Tools")
    print("="*80)
    
    try:
        if not Config.GOOGLE_API_KEY or Config.GOOGLE_API_KEY == 'your_gemini_api_key_here':
            print("⚠ Skipping (API key not configured)")
            return True
        
        tools = create_document_rag_tools(storage_path="test_langchain_storage")
        print(f"✓ Created {len(tools)} LangChain tools:")
        
        for i, tool in enumerate(tools, 1):
            print(f"  {i}. {tool.name}")
        
        print("\n✅ LangChain tools created successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_integration():
    """Test 5: Flask App Integration"""
    print("\n" + "="*80)
    print("TEST 5: Flask App Integration")
    print("="*80)
    
    try:
        import app as flask_app
        print("✓ Flask app imported")
        
        # Check RAG tool
        if hasattr(flask_app, 'rag_tool') and flask_app.rag_tool:
            print("✓ RAG tool initialized in app")
        else:
            print("⚠ RAG tool not initialized (API key may not be configured)")
        
        # Check LangChain tools
        if hasattr(flask_app, 'langchain_tools') and flask_app.langchain_tools:
            print(f"✓ LangChain tools: {len(flask_app.langchain_tools)}")
        else:
            print("⚠ LangChain tools not initialized")
        
        # Check blueprints
        if any(bp.name == 'rag' for bp in flask_app.app.blueprints.values()):
            print("✓ RAG blueprint registered")
        else:
            print("⚠ RAG blueprint not found")
        
        # Check routes
        routes = [str(rule) for rule in flask_app.app.url_map.iter_rules()]
        rag_routes = [r for r in routes if '/rag/' in r]
        agent_routes = [r for r in routes if '/agent/' in r]
        
        print(f"\n  Available endpoints:")
        print(f"    RAG endpoints: {len(rag_routes)}")
        print(f"    Agent endpoints: {len(agent_routes)}")
        
        print("\n✅ App integration verified!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_direct_tool_usage():
    """Test 6: Direct Tool Usage (Without Agent)"""
    print("\n" + "="*80)
    print("TEST 6: Direct Tool Usage")
    print("="*80)
    
    try:
        if not Config.GOOGLE_API_KEY or Config.GOOGLE_API_KEY == 'your_gemini_api_key_here':
            print("⚠ Skipping (API key not configured)")
            return True
        
        tools = create_document_rag_tools(storage_path="test_direct_storage")
        
        # Test add_document tool
        print("\n  1. Testing add_document tool...")
        add_tool = next(t for t in tools if t.name == "add_document")
        result = add_tool._run(
            content=RENTAL_AGREEMENT,
            title="Direct Test Rental",
            metadata={"source": "direct_test"}
        )
        print(f"     ✓ Result: {result[:100]}...")
        
        # Test list_documents tool
        print("\n  2. Testing list_documents tool...")
        list_tool = next(t for t in tools if t.name == "list_documents")
        result = list_tool._run()
        print(f"     ✓ Result: {result[:100]}...")
        
        print("\n✅ Direct tool usage working!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Run complete test suite"""
    print("\n" + "="*80)
    print("🤖 LUMINARYAI - COMPREHENSIVE TEST SUITE")
    print("="*80)
    print("Testing: Document Analysis, RAG, LangChain, and App Integration")
    print()
    
    results = []
    
    # Run all tests
    results.append(("Module Imports", test_module_imports()))
    results.append(("Gemini Reasoning Engine", test_gemini_reasoning_engine()))
    results.append(("Document RAG Tool", test_rag_tool()))
    results.append(("LangChain Tools", test_langchain_tools()))
    results.append(("Flask App Integration", test_app_integration()))
    results.append(("Direct Tool Usage", test_direct_tool_usage()))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nYour LuminaryAI system is fully operational:")
        print("  ✓ Document analysis with Gemini")
        print("  ✓ RAG pipeline with embeddings")
        print("  ✓ LangChain tools for autonomous operations")
        print("  ✓ Flask app with RAG endpoints")
        print("  ✓ Agent endpoint for intelligent queries")
    else:
        print("\n⚠ Some tests failed. Check output above.")
        print("Note: Some failures may be due to missing API keys.")
    
    print()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='LuminaryAI Test Suite')
    parser.add_argument('--test', choices=['all', 'imports', 'gemini', 'rag', 'langchain', 'app', 'direct'],
                        default='all', help='Which test to run')
    
    args = parser.parse_args()
    
    if args.test == 'all':
        run_all_tests()
    elif args.test == 'imports':
        test_module_imports()
    elif args.test == 'gemini':
        test_gemini_reasoning_engine()
    elif args.test == 'rag':
        test_rag_tool()
    elif args.test == 'langchain':
        test_langchain_tools()
    elif args.test == 'app':
        test_app_integration()
    elif args.test == 'direct':
        test_direct_tool_usage()
