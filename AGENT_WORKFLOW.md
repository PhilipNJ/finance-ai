# Agent Workflow Setup Guide

## Overview

The Finance AI Dashboard now features an intelligent **multi-agent workflow** that processes uploaded files through three specialized AI agents:

1. **Agent 1 (ExtractionAgent)**: Extracts all information from files (PDF/CSV/text)
2. **Agent 2 (OrganizerAgent)**: Organizes extracted data into structured JSONs
3. **Agent 3 (DatabaseAgent)**: Dynamically manages database schema and writes data

This workflow uses a lightweight local LLM (Mistral-7B) for intelligent extraction and organization.

## Architecture

```
User Upload (PDF/CSV/Text)
    ↓
[Agent 1: ExtractionAgent]
    - Extracts raw data
    - Uses LLM for enhanced understanding
    - Outputs: output_1.json
    ↓
[Agent 2: OrganizerAgent]
    - Identifies data types (transactions, budgets, accounts, etc.)
    - Structures data into organized JSONs
    - Outputs: organized_*.json files
    ↓
[Agent 3: DatabaseAgent]
    - Analyzes data structure
    - Creates new tables/columns as needed
    - Writes to SQLite database
    ↓
Database Updated
    ↓
Temporary files deleted
```

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Important**: `llama-cpp-python` installation may require specific build flags depending on your system:

#### macOS (Apple Silicon)
```bash
CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python==0.2.90
```

#### macOS (Intel)
```bash
pip install llama-cpp-python==0.2.90
```

#### Linux (with CUDA support)
```bash
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python==0.2.90
```

#### Windows
```bash
pip install llama-cpp-python==0.2.90
```

### 2. Verify LLM Model

The project includes a Mistral-7B-Instruct GGUF model file:
- **File**: `mistral-7b-instruct-v0.1.Q5_0.gguf`
- **Location**: Project root directory

If the model file is missing, download it from Hugging Face:
```bash
# Using wget
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q5_0.gguf

# Or using curl
curl -L -o mistral-7b-instruct-v0.1.Q5_0.gguf https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q5_0.gguf
```

## Usage

### Running the Application

```bash
python app.py
```

The app will automatically use the agent workflow if `llama-cpp-python` is installed.

### Configuration

#### Enable/Disable Agent Workflow

Set the `USE_AGENT_WORKFLOW` environment variable:

```bash
# Enable (default)
export USE_AGENT_WORKFLOW=true
python app.py

# Disable (use classic parsing)
export USE_AGENT_WORKFLOW=false
python app.py
```

#### Fallback Behavior

If `llama-cpp-python` is not installed or the LLM fails to load, the system will automatically fall back to:
1. Pattern-based extraction for unstructured data
2. Classic CSV/PDF parsing for structured data

This ensures the app always works, even without LLM capabilities.

### Uploading Files

The agent workflow supports:
- **CSV files**: Bank statements, transaction exports
- **PDF files**: Bank statements, invoices (with OCR support)
- **Text files**: Any financial data in text format

Simply drag and drop files or click to upload. The agents will:
1. Extract all information intelligently
2. Identify data types (transactions, accounts, budgets, etc.)
3. Create database tables as needed
4. Write structured data to the database

## Agent Workflow Details

### Agent 1: ExtractionAgent

**Purpose**: Extract all information from uploaded files

**Features**:
- Multi-format support (CSV, PDF, text)
- LLM-enhanced extraction for unstructured data
- Identifies document type, dates, amounts, descriptions
- Saves raw and enhanced data to `output_1.json`

**Output Example**:
```json
{
  "filename": "statement.pdf",
  "file_type": ".pdf",
  "session_id": "20251007_143022_123456",
  "extracted_at": "2025-10-07T14:30:22.123456",
  "raw_data": {
    "type": "pdf",
    "text": "..."
  },
  "enhanced_data": {
    "llm_analysis": {
      "document_type": "bank_statement",
      "date_range": "2025-09-01 to 2025-09-30",
      "currency": "USD"
    }
  }
}
```

### Agent 2: OrganizerAgent

**Purpose**: Organize extracted data into structured JSONs

**Features**:
- Identifies data types (transactions, accounts, budgets, invoices)
- Normalizes data to standard formats
- LLM-powered extraction for unstructured text
- Pattern-based fallback for reliability
- Creates separate JSONs for each data type

**Output Example**:
```json
{
  "data_type": "transactions",
  "records": [
    {
      "date": "2025-09-15",
      "amount": -45.67,
      "description": "Whole Foods Market",
      "category": "Groceries"
    }
  ],
  "metadata": {
    "source_file": "statement.pdf",
    "record_count": 42
  }
}
```

### Agent 3: DatabaseAgent

**Purpose**: Manage database schema and write data

**Features**:
- **Dynamic schema evolution**: Creates new tables for new data types
- **Column auto-addition**: Adds missing columns to existing tables
- **Type inference**: Automatically infers SQL types from Python values
- **Metadata tracking**: Records source file and creation timestamp
- **Transactional safety**: Ensures data integrity

**Schema Evolution Example**:
```sql
-- If uploading budget data for the first time:
CREATE TABLE budgets (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  category TEXT,
  amount REAL,
  period TEXT,
  source_file TEXT,
  created_at TEXT
)

-- If new field appears in later upload:
ALTER TABLE budgets ADD COLUMN notes TEXT
```

## Temporary Files

The workflow uses temporary files stored in `data/temp/`:

- `output_1_{session_id}.json` - Raw extraction output
- `organized_{data_type}_{session_id}.json` - Organized data by type

**Cleanup**: All temporary files are automatically deleted after successful database write.

## Database Tables

### Existing Tables

- **documents**: Tracks uploaded files
- **transactions**: Financial transactions
- **mem_labels**: Categorization memory (keyword → category)

### Dynamic Tables

Agent 3 can create new tables based on data type:
- **budgets**: Budget planning data
- **accounts**: Account balances and info
- **invoices**: Invoice records
- **Any custom data type identified by Agent 2**

## Performance Considerations

### LLM Loading

The Mistral-7B model (~4.2GB) is loaded into memory on first use:
- **First upload**: ~5-10 seconds for model loading
- **Subsequent uploads**: Instant (model remains in memory)

### Memory Usage

- **Model in memory**: ~4-5GB RAM
- **Recommended**: 8GB+ RAM for comfortable operation
- **Low memory systems**: Use `USE_AGENT_WORKFLOW=false` to disable LLM

### Processing Speed

- **Small files** (<100 transactions): 2-5 seconds
- **Medium files** (100-1000 transactions): 5-15 seconds
- **Large files** (1000+ transactions): 15-30 seconds

Processing includes extraction, LLM analysis, organization, and database write.

## Troubleshooting

### LLM Installation Issues

**Problem**: `llama-cpp-python` fails to install

**Solutions**:
1. Install build tools:
   ```bash
   # macOS
   xcode-select --install
   
   # Ubuntu/Debian
   sudo apt-get install build-essential
   ```

2. Use pre-built wheels:
   ```bash
   pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
   ```

### Model Not Found

**Problem**: `Model file not found at mistral-7b-instruct-v0.1.Q5_0.gguf`

**Solution**: Download the model (see Installation section above)

### Out of Memory

**Problem**: System runs out of RAM when loading model

**Solutions**:
1. Use a smaller model:
   ```python
   # In llm_handler.py, modify:
   model_path = Path(__file__).parent / "mistral-7b-instruct-v0.1.Q4_0.gguf"  # Smaller quantization
   ```

2. Disable agent workflow:
   ```bash
   export USE_AGENT_WORKFLOW=false
   python app.py
   ```

### Agent Workflow Errors

**Problem**: Agent workflow fails but app continues working

**Reason**: Automatic fallback to classic parsing

**Check**: Look for "fallback method" in upload status messages

## Advanced Configuration

### Custom LLM Settings

Edit `llm_handler.py` to customize LLM parameters:

```python
llm_handler = LLMHandler(
    model_path=Path("path/to/your/model.gguf"),
    n_ctx=4096,        # Context window size
    n_threads=4        # CPU threads to use
)
```

### Custom Agent Behavior

Modify agent classes in `agents.py`:

- **ExtractionAgent**: Change extraction prompts or add new file type handlers
- **OrganizerAgent**: Add new data type categories or normalization rules
- **DatabaseAgent**: Customize schema creation or type inference

### Temperature and Creativity

For more creative LLM responses (less recommended for financial data):

```python
# In agents.py, modify generate() calls:
llm_response = llm.generate_json(prompt, temperature=0.3)  # Default: 0.1
```

Lower temperature (0.1) = more deterministic and accurate
Higher temperature (0.7+) = more creative but less reliable

## Testing the Agent Workflow

### Test with Sample Files

1. **CSV Test**:
   ```csv
   date,amount,description
   2025-10-01,-45.67,Whole Foods Market
   2025-10-02,2500.00,Salary Deposit
   ```

2. **PDF Test**: Upload any bank statement PDF

3. **Text Test**:
   ```
   Transaction History
   10/01/2025  -$45.67  Whole Foods Market
   10/02/2025  +$2500.00  Salary Deposit
   ```

### Verify Agent Execution

Check console output for agent messages:
```
[Agent 1] Extracting information from statement.csv...
Loading LLM from mistral-7b-instruct-v0.1.Q5_0.gguf...
LLM loaded successfully.
[Agent 2] Organizing extracted data...
[Agent 3] Writing to database...
Cleaned up temporary files for session 20251007_143022_123456
```

### Inspect Database

```bash
sqlite3 data/finance.db
```

```sql
-- Check for new tables
.tables

-- View transactions
SELECT * FROM transactions LIMIT 10;

-- Check if new columns were added
PRAGMA table_info(transactions);
```

## Future Enhancements

The agent system is designed for extensibility:

1. **More Data Types**: Add support for investment portfolios, loan schedules, etc.
2. **Better LLM Models**: Swap in newer/better models as they become available
3. **Agent Collaboration**: Agents could query each other for context
4. **User Feedback Loop**: Let users correct agent decisions to improve accuracy
5. **Embedding Search**: Use FAISS for semantic transaction matching

## Support

For issues or questions:
1. Check console output for error messages
2. Verify `data/temp/` directory is writable
3. Ensure model file exists and is readable
4. Try disabling agent workflow to isolate issues

## License

This agent workflow system is part of the Finance AI Dashboard project.
