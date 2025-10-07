# Finance AI Dashboard - AI-First Architecture

## Philosophy

This application is built with an **AI-first** philosophy. Unlike traditional financial software that uses AI as an optional enhancement, Finance AI Dashboard is fundamentally powered by artificial intelligence at its core.

## Why AI-First?

### Traditional Approach (What We Don't Do)
```
Upload CSV → Parse with rigid rules → Manual categorization → Database
```
**Problems:**
- Only works with perfectly formatted files
- Breaks with new formats
- Requires manual data entry for PDFs
- Can't understand context
- Limited to predefined categories

### AI-First Approach (What We Do)
```
Upload ANY file → AI understands context → AI organizes intelligently → Self-adapting database
```
**Benefits:**
- ✅ Handles unstructured documents
- ✅ Understands context and intent
- ✅ Adapts to new formats automatically
- ✅ Extracts from text, images (OCR), tables
- ✅ Creates new categories and tables as needed

## Core AI Components

### 1. Local LLM (Mistral-7B)
- **Purpose**: Natural language understanding
- **Model**: Mistral-7B-Instruct-v0.1 (Q5_0 quantization)
- **Size**: ~4.2GB
- **Speed**: 5-10 tokens/second on CPU
- **Privacy**: 100% offline, no data leaves your machine

**Why Mistral?**
- Excellent instruction following
- Good balance of size vs capability
- Quantized for CPU efficiency
- Free and open source

### 2. Three Specialized AI Agents

Each agent has a specific role and uses the LLM differently:

#### Agent 1: Extraction Agent 🔍
**Role**: Universal document reader

**AI Tasks:**
- Understand document type (bank statement, invoice, budget, etc.)
- Extract relevant financial entities
- Identify date ranges, currencies, account info
- Handle both structured and unstructured data

**LLM Prompt Example:**
```
Analyze this financial document and extract key information.
Identify:
1. Document type (bank statement, credit card, invoice, budget, etc.)
2. Date range or relevant dates
3. Account information (if present)
4. Currency
5. Key financial entities (transactions, balances, totals)

Context: [document content]
```

**Intelligence Level**: High - Must understand diverse document formats

#### Agent 2: Organizer Agent 📊
**Role**: Intelligent data structuring

**AI Tasks:**
- Identify what types of data are present
- Extract structured records from unstructured text
- Normalize data to standard formats
- Determine appropriate categories and fields

**LLM Prompt Example:**
```
Extract all financial transactions from this text.
For each transaction, identify:
- date (in YYYY-MM-DD format if possible)
- amount (as a number, negative for expenses, positive for income)
- description (what the transaction was for)

Return as JSON array.

Context: [transaction data]
```

**Intelligence Level**: Very High - Must structure unstructured data

#### Agent 3: Database Agent 💾
**Role**: Schema evolution expert

**AI Tasks:**
- Analyze data structure
- Determine if new tables needed
- Identify missing columns
- Infer appropriate SQL types

**Intelligence Level**: Medium - Primarily rule-based with some inference

## AI Workflow Step-by-Step

### Step 1: Upload
```python
User uploads: "September_2025_Statement.pdf"
```

### Step 2: Agent 1 - Extraction
```python
# Agent 1 reads the file
raw_text = extract_text_from_pdf(content)

# Agent 1 asks LLM to understand it
llm_response = llm.generate_json(f"""
    Analyze this financial document:
    {raw_text[:3000]}
""")

# LLM Response:
{
    "document_type": "bank_statement",
    "date_range": "2025-09-01 to 2025-09-30",
    "account_info": "Checking Account ****1234",
    "currency": "USD",
    "entities": ["transactions", "balances"]
}

# Agent 1 saves this to output_1.json
```

### Step 3: Agent 2 - Organization
```python
# Agent 2 reads output_1.json
output_1 = load_json("output_1.json")

# Agent 2 identifies data types
data_types = ["transactions"]  # Could also be ["budgets"], ["invoices"], etc.

# Agent 2 asks LLM to extract transactions
llm_response = llm.generate_json(f"""
    Extract all transactions from this bank statement:
    {output_1['raw_data']['text']}
""")

# LLM Response:
{
    "transactions": [
        {
            "date": "2025-09-15",
            "amount": -45.67,
            "description": "WHOLE FOODS MARKET #123"
        },
        {
            "date": "2025-09-16",
            "amount": -12.50,
            "description": "COFFEE SHOP DOWNTOWN"
        }
        // ... more transactions
    ]
}

# Agent 2 normalizes and saves to organized_transactions.json
```

### Step 4: Agent 3 - Database Write
```python
# Agent 3 reads organized_transactions.json
organized_data = load_json("organized_transactions.json")

# Agent 3 checks if table exists and has all needed columns
check_schema(table="transactions", sample_record=organized_data['records'][0])

# If new fields exist, add them
if 'notes' in sample_record and 'notes' not in existing_columns:
    ALTER TABLE transactions ADD COLUMN notes TEXT

# Write all records
for record in organized_data['records']:
    INSERT INTO transactions (date, amount, description, category, ...)
    VALUES (?, ?, ?, ?, ...)

# Agent 3 done!
```

### Step 5: Cleanup
```python
# Delete temporary files
delete("output_1.json")
delete("organized_transactions.json")

# Show result to user
"✓ September_2025_Statement.pdf: 42 records processed 🤖"
```

## AI Decision Points

### When Agent 1 Uses LLM
- **Always** for document understanding
- **Always** for context extraction
- Even for CSV files (to understand column meanings)

### When Agent 2 Uses LLM
- **Primary**: Extracting from unstructured text
- **Secondary**: Understanding CSV column purposes
- **Fallback**: Pattern matching if LLM extraction returns nothing

### When Agent 3 Uses LLM
- **Never** - Schema evolution is rule-based for reliability
- Type inference uses Python types, not LLM

## Prompt Engineering

### Key Principles

1. **Clear Instructions**: Tell the LLM exactly what to extract
2. **JSON Output**: Always request structured JSON responses
3. **Context Limits**: Truncate input to ~3000 tokens
4. **Low Temperature**: Use 0.1 for deterministic financial data
5. **Examples**: Provide format examples in prompts

### Example Prompt Template
```python
prompt = f"""[INST] {instruction}

Context:
{context[:3000]}

Return valid JSON only. [/INST]"""
```

## Why This Works

### 1. Flexibility
LLMs can understand almost any document format. New bank? New layout? No problem.

### 2. Context Understanding
"WHOLE FOODS" → Groceries (not just keyword matching)
"SPOTIFY PREMIUM" → Subscription (understands it's recurring)

### 3. Future-Proof
As LLMs improve, so does the app. Just swap the model file.

### 4. Self-Improving
User corrections can be fed back to improve categorization over time.

## Performance Considerations

### Model Loading
- **First time**: 5-10 seconds to load 4.2GB model
- **Subsequent**: Instant (model stays in memory)

### Processing Speed
- **Small files** (<100 rows): 2-3 seconds
- **Medium files** (100-1000 rows): 5-10 seconds
- **Large files** (1000+ rows): 15-30 seconds

### Memory Usage
- **Model in RAM**: ~4-5GB
- **Processing**: +500MB during extraction
- **Total**: ~5-6GB RAM needed

### Optimization Tips
1. **Use quantized models**: Q5_0 is good balance
2. **Batch processing**: Group multiple uploads
3. **GPU acceleration**: If available (Metal, CUDA)
4. **Context pruning**: Limit text sent to LLM

## Fallback Strategy

Even though we're AI-first, we have fallbacks:

```python
if llm_available:
    # Primary: Use AI
    transactions = llm_extract_transactions(text)
    
    if not transactions:
        # Fallback 1: Pattern matching
        transactions = regex_extract_transactions(text)
        
        if not transactions:
            # Fallback 2: Manual entry prompt
            show_manual_entry_form()
else:
    # No LLM: Show clear error
    raise ImportError("LLM required for this app")
```

## Future AI Enhancements

### Phase 2 (Future)
- **Embeddings**: Use sentence transformers for semantic search
- **Vector DB**: FAISS for similar transaction matching
- **Multi-modal**: Direct image understanding (no OCR)
- **Conversational**: Chat with your finances

### Phase 3 (Future)
- **Predictive**: Forecast spending patterns
- **Anomaly Detection**: Flag unusual transactions
- **Budget Suggestions**: AI-recommended budgets
- **Financial Advice**: Personalized insights

## Model Alternatives

### Smaller Models (Faster, Less Capable)
- **TinyLlama-1.1B**: ~600MB, 3x faster
- **Phi-2-2.7B**: ~1.5GB, 2x faster

### Larger Models (Slower, More Capable)
- **Mistral-7B Q8**: ~7GB, more accurate
- **Llama-2-13B**: ~13GB, best quality

### How to Swap Models
```python
# In llm_handler.py
model_path = Path("your-model-name.gguf")
```

## Privacy & Security

### Why Local AI Matters
- ❌ **Cloud API**: Your data goes to OpenAI/Anthropic servers
- ✅ **Local AI**: Everything stays on your computer

### Data Flow
```
Your Files → Your RAM → Your Database
           ↑
    Never leaves your machine
```

### No Telemetry
- No usage tracking
- No crash reports
- No analytics
- Zero network calls

## Conclusion

This AI-first architecture makes the Finance Dashboard:
- More flexible than rule-based systems
- More private than cloud-based apps
- More capable than traditional software
- More future-proof as AI advances

**The AI is not a feature. The AI is the product.** 🤖
