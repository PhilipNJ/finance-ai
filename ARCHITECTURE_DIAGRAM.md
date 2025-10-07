# Agent Workflow Visual Architecture

## Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERACTION                             │
│                    (Upload CSV, PDF, or Text)                        │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         app.py (Upload Handler)                      │
│  • Saves file to data/uploads/                                       │
│  • Checks if USE_AGENT_WORKFLOW=true                                │
│  • Checks if LLM available                                           │
└────────────────────────┬────────────────────────────────────────────┘
                         │
            ┌────────────┴────────────┐
            │                         │
            ▼ (Agent Mode)            ▼ (Fallback Mode)
┌─────────────────────┐      ┌──────────────────┐
│  AgentWorkflow      │      │  Classic Parsing │
│  Orchestrator       │      │  • parse_csv()   │
└──────────┬──────────┘      │  • parse_pdf()   │
           │                 │  • categorize()  │
           │                 └────────┬─────────┘
           │                          │
           ▼                          │
┌─────────────────────────────────────┤
│  SESSION CREATED                    │
│  session_id = timestamp_random      │
└──────────┬──────────────────────────┘
           │
           ▼
╔═══════════════════════════════════════════════════════════════════╗
║                    AGENT 1: ExtractionAgent                        ║
║  ┌──────────────────────────────────────────────────────────────┐ ║
║  │ Input: Raw file content (bytes) + file type                  │ ║
║  └──────────────────────────────────────────────────────────────┘ ║
║                              │                                     ║
║                              ▼                                     ║
║  ┌──────────────────────────────────────────────────────────────┐ ║
║  │ Step 1: Extract by file type                                 │ ║
║  │  • CSV  → parse_csv() → structured rows                      │ ║
║  │  • PDF  → extract_text_from_pdf() → raw text                 │ ║
║  │  • Text → decode() → raw text                                │ ║
║  └──────────────────────────────────────────────────────────────┘ ║
║                              │                                     ║
║                              ▼                                     ║
║  ┌──────────────────────────────────────────────────────────────┐ ║
║  │ Step 2: LLM Enhancement (if available)                       │ ║
║  │  • Load Mistral-7B model                                     │ ║
║  │  • Analyze document with prompt:                             │ ║
║  │    "What type of financial document is this?"                │ ║
║  │    "Extract: dates, amounts, account info, currency"         │ ║
║  │  • Generate JSON response with insights                      │ ║
║  └──────────────────────────────────────────────────────────────┘ ║
║                              │                                     ║
║                              ▼                                     ║
║  ┌──────────────────────────────────────────────────────────────┐ ║
║  │ Output: output_1_{session_id}.json                           │ ║
║  │  {                                                            │ ║
║  │    "filename": "statement.pdf",                              │ ║
║  │    "file_type": ".pdf",                                      │ ║
║  │    "raw_data": { ... },                                      │ ║
║  │    "enhanced_data": {                                        │ ║
║  │      "llm_analysis": {                                       │ ║
║  │        "document_type": "bank_statement",                    │ ║
║  │        "date_range": "2025-09-01 to 2025-09-30",            │ ║
║  │        "currency": "USD"                                     │ ║
║  │      }                                                        │ ║
║  │    }                                                          │ ║
║  │  }                                                            │ ║
║  └──────────────────────────────────────────────────────────────┘ ║
╚═══════════════════════════════════════════════════════════════════╝
           │
           ▼
╔═══════════════════════════════════════════════════════════════════╗
║                    AGENT 2: OrganizerAgent                         ║
║  ┌──────────────────────────────────────────────────────────────┐ ║
║  │ Input: output_1_{session_id}.json                            │ ║
║  └──────────────────────────────────────────────────────────────┘ ║
║                              │                                     ║
║                              ▼                                     ║
║  ┌──────────────────────────────────────────────────────────────┐ ║
║  │ Step 1: Identify data types present                          │ ║
║  │  • Check file structure and LLM analysis                     │ ║
║  │  • Possible types: transactions, budgets, accounts, invoices │ ║
║  │  • Default: transactions (most common)                       │ ║
║  └──────────────────────────────────────────────────────────────┘ ║
║                              │                                     ║
║                              ▼                                     ║
║  ┌──────────────────────────────────────────────────────────────┐ ║
║  │ Step 2: Organize by data type                                │ ║
║  │  FOR EACH data_type:                                         │ ║
║  │                                                               │ ║
║  │  IF type == "transactions":                                  │ ║
║  │    • Extract from CSV rows (if structured)                   │ ║
║  │    • OR use LLM to extract from text:                        │ ║
║  │      "Extract all transactions from this text.               │ ║
║  │       Return as JSON array with date, amount, description"   │ ║
║  │    • OR use regex patterns (fallback)                        │ ║
║  │    • Normalize to standard format                            │ ║
║  │                                                               │ ║
║  │  IF type == "budgets":                                       │ ║
║  │    • Similar extraction process                              │ ║
║  │    • Different schema                                        │ ║
║  └──────────────────────────────────────────────────────────────┘ ║
║                              │                                     ║
║                              ▼                                     ║
║  ┌──────────────────────────────────────────────────────────────┐ ║
║  │ Output: Multiple JSON files                                  │ ║
║  │                                                               │ ║
║  │ organized_transactions_{session_id}.json:                    │ ║
║  │  {                                                            │ ║
║  │    "data_type": "transactions",                              │ ║
║  │    "records": [                                              │ ║
║  │      {                                                        │ ║
║  │        "date": "2025-10-01",                                 │ ║
║  │        "amount": -45.67,                                     │ ║
║  │        "description": "Whole Foods Market",                  │ ║
║  │        "category": "Groceries"                               │ ║
║  │      },                                                       │ ║
║  │      ...                                                      │ ║
║  │    ],                                                         │ ║
║  │    "metadata": { ... }                                       │ ║
║  │  }                                                            │ ║
║  │                                                               │ ║
║  │ organized_budgets_{session_id}.json (if detected)            │ ║
║  │ organized_accounts_{session_id}.json (if detected)           │ ║
║  └──────────────────────────────────────────────────────────────┘ ║
╚═══════════════════════════════════════════════════════════════════╝
           │
           ▼
╔═══════════════════════════════════════════════════════════════════╗
║                    AGENT 3: DatabaseAgent                          ║
║  ┌──────────────────────────────────────────────────────────────┐ ║
║  │ Input: List of organized JSON files                          │ ║
║  └──────────────────────────────────────────────────────────────┘ ║
║                              │                                     ║
║           FOR EACH organized JSON file:                            ║
║                              │                                     ║
║                              ▼                                     ║
║  ┌──────────────────────────────────────────────────────────────┐ ║
║  │ Step 1: Check if table exists                                │ ║
║  │  SELECT name FROM sqlite_master WHERE name=?                 │ ║
║  └──────────────────────────────────────────────────────────────┘ ║
║                              │                                     ║
║             ┌────────────────┴────────────────┐                   ║
║             │                                 │                   ║
║             ▼ (Table exists)                  ▼ (Table missing)   ║
║  ┌──────────────────────┐        ┌────────────────────────────┐  ║
║  │ Check for new columns│        │ Create table dynamically    │  ║
║  │ PRAGMA table_info(?) │        │ • Infer column types from   │  ║
║  │                      │        │   sample record             │  ║
║  │ For each new field:  │        │ • Add metadata columns      │  ║
║  │  ALTER TABLE ADD     │        │   (source_file, created_at) │  ║
║  │  COLUMN name TYPE    │        │ • CREATE TABLE ...          │  ║
║  └──────────────────────┘        └────────────────────────────┘  ║
║             │                                 │                   ║
║             └────────────────┬────────────────┘                   ║
║                              ▼                                     ║
║  ┌──────────────────────────────────────────────────────────────┐ ║
║  │ Step 2: Write records                                        │ ║
║  │  FOR EACH record:                                            │ ║
║  │    • Add metadata (source_file, created_at)                 │ ║
║  │    • Build INSERT query with placeholders                    │ ║
║  │    • Execute: INSERT INTO table (cols...) VALUES (?, ?, ...) │ ║
║  │    • Handle errors gracefully                                │ ║
║  │  COMMIT transaction                                          │ ║
║  └──────────────────────────────────────────────────────────────┘ ║
║                              │                                     ║
║                              ▼                                     ║
║  ┌──────────────────────────────────────────────────────────────┐ ║
║  │ Output: Database updated                                     │ ║
║  │  • X records written to Y table(s)                           │ ║
║  │  • New tables created (if needed)                            │ ║
║  │  • New columns added (if needed)                             │ ║
║  └──────────────────────────────────────────────────────────────┘ ║
╚═══════════════════════════════════════════════════════════════════╝
           │
           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          CLEANUP PHASE                               │
│  • Delete output_1_{session_id}.json                                │
│  • Delete all organized_*_{session_id}.json files                   │
│  • Free temporary resources                                         │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      RETURN TO USER                                  │
│  ✓ Successfully processed filename.pdf: 42 records (with LLM)       │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Interaction Diagram

```
┌──────────────┐
│   app.py     │  Main application entry point
└──────┬───────┘
       │
       │ imports & initializes
       │
       ├───────────────────┬────────────────────┬──────────────────┐
       │                   │                    │                  │
       ▼                   ▼                    ▼                  ▼
┌──────────────┐   ┌──────────────┐    ┌──────────────┐   ┌──────────────┐
│  agents.py   │   │llm_handler.py│    │ finance_db.py│   │  parsers.py  │
│              │   │              │    │              │   │              │
│ • Workflow   │   │ • LLMHandler │    │ • init_db()  │   │ • parse_csv()│
│ • Agent1     │   │ • Mistral    │    │ • get_conn() │   │ • parse_pdf()│
│ • Agent2     │───┤ • Prompts    │    │ • insert_*() │   │ • categorize()│
│ • Agent3     │   │ • JSON gen   │    │              │   │              │
└──────────────┘   └──────────────┘    └──────────────┘   └──────────────┘
       │                   │                    │                  │
       │                   │                    │                  │
       └───────────────────┴────────────────────┴──────────────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │   File System        │
                        │                      │
                        │ • data/uploads/      │
                        │ • data/temp/         │
                        │ • data/finance.db    │
                        │ • mistral-*.gguf     │
                        └──────────────────────┘
```

## Database Schema Evolution Example

```
INITIAL STATE:
┌──────────────┐     ┌─────────────────┐     ┌──────────────┐
│  documents   │     │  transactions   │     │  mem_labels  │
├──────────────┤     ├─────────────────┤     ├──────────────┤
│ id           │     │ id              │     │ id           │
│ filename     │     │ document_id     │     │ keyword      │
│ uploaded_at  │     │ date            │     │ category     │
└──────────────┘     │ amount          │     └──────────────┘
                     │ description     │
                     │ category        │
                     └─────────────────┘

USER UPLOADS BUDGET FILE:
Agent 2 detects: "budgets" data type
Agent 3 executes: CREATE TABLE budgets

AFTER PROCESSING:
┌──────────────┐     ┌─────────────────┐     ┌──────────────┐
│  documents   │     │  transactions   │     │  mem_labels  │
├──────────────┤     ├─────────────────┤     ├──────────────┤
│ id           │     │ id              │     │ id           │
│ filename     │     │ document_id     │     │ keyword      │
│ uploaded_at  │     │ date            │     │ category     │
└──────────────┘     │ amount          │     └──────────────┘
                     │ description     │
                     │ category        │     ┌──────────────┐
                     └─────────────────┘     │   budgets    │◄─ NEW!
                                             ├──────────────┤
                                             │ id           │
                                             │ category     │
                                             │ amount       │
                                             │ period       │
                                             │ source_file  │
                                             │ created_at   │
                                             └──────────────┘

USER UPLOADS BUDGET WITH NOTES:
Agent 3 detects: "notes" field in data
Agent 3 executes: ALTER TABLE budgets ADD COLUMN notes TEXT

AFTER EVOLUTION:
                                             ┌──────────────┐
                                             │   budgets    │
                                             ├──────────────┤
                                             │ id           │
                                             │ category     │
                                             │ amount       │
                                             │ period       │
                                             │ source_file  │
                                             │ created_at   │
                                             │ notes        │◄─ NEW COLUMN!
                                             └──────────────┘
```

## LLM Prompt Examples

### Agent 1 Enhancement Prompt
```
[INST] Analyze this financial document and extract key information.
Identify:
1. Document type (bank statement, credit card, invoice, budget, etc.)
2. Date range or relevant dates
3. Account information (if present)
4. Currency
5. Key financial entities (transactions, balances, totals)

Return your analysis as JSON with these fields: document_type, date_range, 
account_info, currency, entities.

Context:
[CSV/PDF/Text content here...]
[/INST]
```

### Agent 2 Transaction Extraction Prompt
```
[INST] Extract all financial transactions from this text.
For each transaction, identify:
- date (in YYYY-MM-DD format if possible)
- amount (as a number, negative for expenses, positive for income)
- description (what the transaction was for)

Return as JSON array: [{"date": "...", "amount": 0.0, "description": "..."}]

Context:
[Text content here...]
[/INST]
```

## Error Handling & Fallbacks

```
┌─────────────────────┐
│  Upload File        │
└──────────┬──────────┘
           │
           ▼
    ┌──────────────┐
    │ LLM Available?│
    └──────┬───────┘
           │
    ┌──────┴──────┐
    │             │
    ▼ YES         ▼ NO
┌─────────┐   ┌────────────────┐
│ Agent   │   │ Pattern-based  │
│ Workflow│   │ Extraction     │
└────┬────┘   └────────┬───────┘
     │                 │
     │ ┌───────────────┘
     │ │
     ▼ ▼
 ┌─────────┐
 │ Success?│
 └────┬────┘
      │
  ┌───┴───┐
  │       │
  ▼ YES   ▼ NO
┌─────┐ ┌──────────┐
│Done │ │ Fallback │
│     │ │ to Classic│
└─────┘ │ Parser   │
        └─────┬────┘
              │
              ▼
        ┌─────────┐
        │  Done   │
        └─────────┘
```
