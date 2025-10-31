# Document RAG Tools - LangChain Integration

## Overview

LangChain tool wrappers that make the Document RAG Tool accessible to LLMs as autonomous agents. The LLM can use these tools to manage documents, search, query, and analyze legal documents independently.

## Features

### 🤖 LLM-Accessible Tools

- **9 Complete Tools** - Full document management via LangChain
- **Autonomous Operation** - LLM decides when and how to use tools
- **Multi-Step Reasoning** - Agent can chain multiple tool calls
- **Context Aware** - Maintains conversation context
- **Type Safe** - Pydantic schemas for validation

### 📦 Available Tools

| Tool Name             | Description                 | Input Required           |
| --------------------- | --------------------------- | ------------------------ |
| `add_document`        | Add new document to RAG     | content, title, metadata |
| `search_documents`    | Semantic search across docs | query, top_k, doc_filter |
| `query_document`      | Ask questions about doc     | doc_id, question         |
| `list_documents`      | List all documents          | none                     |
| `get_document`        | Get full document content   | doc_id                   |
| `delete_document`     | Delete a document           | doc_id                   |
| `compare_documents`   | Compare two documents       | doc_id1, doc_id2         |
| `semantic_search_all` | Search with grouped results | query, top_k             |
| `get_statistics`      | Get system statistics       | none                     |

## Installation

Required packages:

```bash
pip install langchain langchain-google-genai pydantic
```

Already included in your `requirements.txt`!

## Quick Start

### 1. Create Tools

```python
from modules.document_rag_langchain import create_document_rag_tools

# Create all 9 tools
tools = create_document_rag_tools(storage_path="document_storage")

print(f"Created {len(tools)} tools")
for tool in tools:
    print(f"  - {tool.name}")
```

### 2. Create LangChain Agent

```python
from langchain.agents import AgentExecutor, create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    google_api_key="your_key",
    temperature=0.7
)

# Create agent with tools
agent = create_react_agent(llm, tools, prompt_template)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True
)
```

### 3. Let LLM Use Tools

```python
# LLM will autonomously decide which tools to use
result = agent_executor.invoke({
    "input": "Add this rental agreement to the system and then search for notice period clauses"
})

print(result["output"])
```

## Usage Examples

### Example 1: Document Management

```python
# LLM autonomously adds document
query = """
Add this employment contract:
'EMPLOYMENT AGREEMENT dated 2025-01-15.
Employee: John Doe. Salary: Rs. 12,00,000 per annum.
Notice Period: 60 days. Non-compete: 12 months.'

Title it 'John Doe Employment Contract' with metadata type='employment'
"""

result = agent_executor.invoke({"input": query})

# LLM Output:
# "I've added the employment contract successfully.
#  Document ID: abc123, Chunks created: 2"
```

### Example 2: Intelligent Search

```python
query = "Find all clauses related to termination across all documents"

result = agent_executor.invoke({"input": query})

# LLM will:
# 1. Use search_documents tool
# 2. Analyze results
# 3. Provide summary
```

### Example 3: Q&A Workflow

```python
query = """
First, list all available documents.
Then, for the employment contract, tell me:
1. What is the salary?
2. What is the notice period?
3. Is there a non-compete clause?
"""

result = agent_executor.invoke({"input": query})

# LLM will:
# 1. Call list_documents
# 2. Identify the employment contract doc_id
# 3. Call query_document multiple times
# 4. Synthesize answers
```

### Example 4: Document Comparison

```python
query = """
Compare the rental agreement and employment contract.
Focus on termination clauses and notice periods.
"""

result = agent_executor.invoke({"input": query})

# LLM will:
# 1. List documents to find IDs
# 2. Call compare_documents
# 3. Provide analysis
```

## Direct Tool Usage

You can also use tools directly without an agent:

```python
from modules.document_rag_langchain import create_document_rag_tools

tools = create_document_rag_tools()

# Use specific tool
add_tool = next(t for t in tools if t.name == "add_document")
result = add_tool._run(
    content="Document text...",
    title="My Document",
    metadata={"type": "contract"}
)
print(result)

# Search
search_tool = next(t for t in tools if t.name == "search_documents")
result = search_tool._run(query="notice period", top_k=5)
print(result)
```

## Tool Schemas

Each tool has a Pydantic schema for input validation:

### AddDocumentInput

```python
class AddDocumentInput(BaseModel):
    content: str  # Document text
    title: str    # Document title
    metadata: Optional[Dict[str, str]]  # Optional metadata
```

### SearchDocumentsInput

```python
class SearchDocumentsInput(BaseModel):
    query: str    # Search query
    top_k: int = 5  # Number of results
    doc_filter: Optional[str]  # Optional doc ID filter
```

### QueryDocumentInput

```python
class QueryDocumentInput(BaseModel):
    doc_id: str   # Document ID
    question: str # Question to ask
```

## Advanced Configuration

### Custom Prompt Template

```python
template = """You are a specialized legal AI assistant.

You have access to document management tools for storing, searching, and analyzing legal documents.

Available tools:
{tools}

Tool names: {tool_names}

Always:
- Think step by step
- Use tools when needed
- Cite sources for legal information
- Be precise with document IDs

Question: {input}
{agent_scratchpad}
"""

prompt = PromptTemplate.from_template(template)
agent = create_react_agent(llm, tools, prompt)
```

### Agent Configuration

```python
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,              # Show reasoning
    max_iterations=15,         # Maximum tool calls
    handle_parsing_errors=True, # Graceful error handling
    early_stopping_method="generate"  # Stop when answer found
)
```

### Custom Tool Subset

```python
# Use only specific tools
from modules.document_rag_langchain import (
    AddDocumentTool,
    SearchDocumentsTool,
    QueryDocumentTool
)
from modules.document_rag_tool import DocumentRAGTool

rag_tool = DocumentRAGTool()

custom_tools = [
    AddDocumentTool(rag_tool),
    SearchDocumentsTool(rag_tool),
    QueryDocumentTool(rag_tool)
]

agent = create_react_agent(llm, custom_tools, prompt)
```

## Testing

### Run Comprehensive Tests

```bash
# Test with LangChain agent
python test_document_rag_langchain.py --mode agent

# Test direct tool usage
python test_document_rag_langchain.py --mode direct

# Show tool catalog
python test_document_rag_langchain.py --mode catalog
```

### Test Scenarios Included

1. ✅ Add document via agent
2. ✅ List documents
3. ✅ Search documents
4. ✅ Query document
5. ✅ Get statistics
6. ✅ Document comparison
7. ✅ Multi-step workflows

## Integration with Existing App

### Add to Flask API

```python
# In app.py
from modules.document_rag_langchain import create_document_rag_tools
from langchain.agents import AgentExecutor, create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI

# Initialize once
tools = create_document_rag_tools()
llm = ChatGoogleGenerativeAI(model=Config.LLM_MODEL, google_api_key=Config.GOOGLE_API_KEY)
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools)

@app.route('/api/agent/query', methods=['POST'])
@auth_manager.token_required
def agent_query():
    """Let LLM agent handle document queries"""
    data = request.get_json()
    query = data.get('query')

    result = agent_executor.invoke({"input": query})

    return jsonify({
        'query': query,
        'response': result['output']
    })
```

## How It Works

### Agent Decision Process

```
User Query
    ↓
LLM Reasoning
    ↓
Tool Selection ─→ [add_document, search_documents, etc.]
    ↓
Tool Execution
    ↓
Observation
    ↓
More Reasoning? ──Yes──→ Select Next Tool
    ↓ No
Final Answer
```

### Example Agent Thinking

```
Query: "Add this contract and find termination clauses"

Thought: I need to first add the document, then search for termination clauses
Action: add_document
Action Input: {"content": "...", "title": "Contract", "metadata": {...}}
Observation: Document added with ID abc123

Thought: Now I can search for termination clauses
Action: search_documents
Action Input: {"query": "termination clauses", "top_k": 5}
Observation: Found 3 relevant chunks...

Thought: I now have the information needed
Final Answer: I've added the contract (ID: abc123) and found 3 termination clauses...
```

## Best Practices

### 1. Clear Instructions

```python
# Good ✓
"Add the rental agreement with title 'Mumbai Rental 2025' and metadata type='rental'"

# Vague ✗
"Add this document"
```

### 2. Provide Context

```python
# Good ✓
"Search for notice period clauses in employment contracts"

# Too broad ✗
"Search for clauses"
```

### 3. Multi-Step Queries

```python
# Good ✓
"First list all documents, then compare the two rental agreements"

# Better: Let agent figure out steps ✓
"Compare all rental agreements and tell me which has better terms"
```

### 4. Error Handling

```python
try:
    result = agent_executor.invoke({"input": query})
except Exception as e:
    # Agent failed - might be parsing error or tool error
    print(f"Agent error: {e}")
```

## Troubleshooting

### Issue: Agent Not Using Tools

**Cause**: Prompt doesn't clearly indicate tools
**Solution**: Use REACT format prompt with tools list

### Issue: Tool Parsing Errors

**Cause**: LLM output doesn't match expected format
**Solution**: Enable `handle_parsing_errors=True` in AgentExecutor

### Issue: Infinite Loop

**Cause**: Agent keeps calling same tool
**Solution**: Set `max_iterations` limit and improve prompt

### Issue: Wrong Tool Selected

**Cause**: Tool descriptions not clear
**Solution**: Improve tool descriptions to be more specific

## Performance

- **Tool Creation**: ~100ms (one-time)
- **Agent Invocation**: 2-5 seconds (depends on reasoning)
- **Tool Execution**: Same as direct RAG tool
- **Multi-Step**: +1-2 seconds per additional step

## Advantages

| Feature         | Traditional API   | LangChain Tools   |
| --------------- | ----------------- | ----------------- |
| Flexibility     | Fixed endpoints   | Dynamic workflows |
| Multi-step      | Manual chaining   | Autonomous        |
| Context         | Stateless         | Maintains context |
| Complexity      | Simple queries    | Complex reasoning |
| User Experience | Explicit commands | Natural language  |

## Use Cases

### 1. Intelligent Document Assistant

```python
"I have 5 contracts. Find which one has the shortest notice period
and then show me the exact clause."

# Agent will:
# - List documents
# - Search each for notice period
# - Compare results
# - Query specific document
# - Return answer
```

### 2. Automated Contract Analysis

```python
"Analyze all employment contracts and create a summary comparing
their termination clauses, salary structures, and non-compete terms."

# Agent handles entire workflow
```

### 3. Legal Research Assistant

```python
"Find all documents mentioning Section 420 IPC and summarize
the legal implications mentioned in each."

# Agent searches, extracts, and synthesizes
```

## Limitations

- **Token Limits**: Agent reasoning uses tokens
- **Cost**: More API calls than direct tool usage
- **Latency**: Slower than single tool call
- **Reliability**: Depends on LLM reasoning quality

## Future Enhancements

- [ ] Memory across sessions
- [ ] Tool result caching
- [ ] Batch operations
- [ ] Custom tool chains
- [ ] Async tool execution
- [ ] Tool usage analytics

## Conclusion

The LangChain integration transforms the Document RAG Tool from a library into an **intelligent agent** that can autonomously manage and analyze legal documents using natural language instructions.

Perfect for:

- ✅ Complex document workflows
- ✅ Natural language interfaces
- ✅ Intelligent document assistants
- ✅ Automated legal research
- ✅ Multi-step analysis tasks
