# Troubleshooting Guide

Common issues and their solutions when using Finance AI Dashboard.

## Installation Issues

### ❌ "LLM model not found"

**Error Message:**
```
FileNotFoundError: LLM model not found at: mistral-7b-instruct-v0.1.Q5_0.gguf
```

**Cause:** The AI model file is missing from the project directory.

**Solution:**

=== "Option 1: Download from Hugging Face"
    ```bash
    wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q5_0.gguf
    ```

=== "Option 2: Manual Download"
    1. Visit: https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF
    2. Download `mistral-7b-instruct-v0.1.Q5_0.gguf` (4.7 GB)
    3. Place in project root directory

=== "Option 3: Use Different Model"
    Edit `llm_handler.py`:
    ```python
    model_path = Path("your-model-name.gguf")
    ```

---

### ❌ "Module 'llama_cpp' not found"

**Error Message:**
```
ModuleNotFoundError: No module named 'llama_cpp'
```

**Cause:** `llama-cpp-python` package not installed or installation failed.

**Solution:**

=== "macOS (Metal GPU)"
    ```bash
    # Activate virtual environment first
    source .venv/bin/activate
    
    # Install with Metal support
    CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python
    ```

=== "Linux (CPU)"
    ```bash
    source .venv/bin/activate
    pip install llama-cpp-python
    ```

=== "Linux (CUDA GPU)"
    ```bash
    source .venv/bin/activate
    CMAKE_ARGS="-DLLAMA_CUDA=on" pip install llama-cpp-python
    ```

=== "Windows (CPU)"
    ```cmd
    .venv\Scripts\activate
    pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
    ```

**If still failing:**
```bash
# Install build dependencies
pip install --upgrade pip setuptools wheel cmake

# Try again
pip install llama-cpp-python
```

---

### ❌ "CMake not found"

**Error during llama-cpp-python installation:**
```
CMake must be installed to build llama-cpp-python
```

**Solution:**

=== "macOS"
    ```bash
    brew install cmake
    ```

=== "Linux (Ubuntu/Debian)"
    ```bash
    sudo apt-get update
    sudo apt-get install cmake build-essential
    ```

=== "Linux (Fedora/RHEL)"
    ```bash
    sudo dnf install cmake gcc-c++
    ```

=== "Windows"
    Download from: https://cmake.org/download/

---

### ❌ Virtual Environment Issues

**Error:**
```
command not found: python3
# or
The virtual environment was not created successfully
```

**Solution:**

=== "macOS"
    ```bash
    # Install Python 3 via Homebrew
    brew install python@3.11
    
    # Create virtual environment
    python3 -m venv .venv
    ```

=== "Linux"
    ```bash
    # Install Python 3 and venv
    sudo apt-get install python3 python3-venv python3-dev
    
    # Create virtual environment
    python3 -m venv .venv
    ```

=== "Windows"
    ```cmd
    # Download Python from python.org
    # Then create virtual environment
    python -m venv .venv
    ```

---

## Runtime Issues

### ❌ "Port 8050 already in use"

**Error:**
```
OSError: [Errno 48] Address already in use
```

**Cause:** Another process is using port 8050.

**Solution:**

=== "Option 1: Kill existing process"
    ```bash
    # Find process using port 8050
    lsof -ti:8050 | xargs kill -9
    
    # Then restart
    python app.py
    ```

=== "Option 2: Use different port"
    Edit `app.py`:
    ```python
    if __name__ == '__main__':
        app.run_server(debug=True, port=8051)  # Changed from 8050
    ```

---

### ❌ "Processing failed" on Upload

**Error Message in UI:**
```
❌ filename.pdf: Processing failed - [error details]
```

**Possible Causes & Solutions:**

#### 1. LLM Not Loaded

**Check startup logs:**
```
python app.py
# Look for: ✓ LLM loaded successfully!
```

**If not loaded, see** [LLM model not found](#llm-model-not-found)

#### 2. Corrupted File

**Try:**
- Re-download the file from your bank
- Open file to verify it's not corrupted
- Try converting to CSV

#### 3. Empty or Invalid File

**Check:**
- File has actual content
- File contains financial data
- File is not password-protected (for PDFs)

#### 4. Memory Issues

**If processing large files:**
```bash
# Check available memory
free -h  # Linux
vm_stat  # macOS

# If low, close other applications
```

---

### ❌ Slow Processing

**Symptoms:**
- First upload takes >30 seconds
- Subsequent uploads take >10 seconds

**Solutions:**

#### 1. Model Loading Slow (First Time)

**Expected:**
- First upload: 7-15 seconds (model loads once)
- Subsequent: 2-5 seconds

**If slower:**
```python
# Check model size
ls -lh mistral-7b-instruct-v0.1.Q5_0.gguf
# Should be ~4.7GB

# If much larger, consider quantized version
```

#### 2. Large Files

**For files >10MB:**
- Split into monthly chunks
- Export smaller date ranges from bank

#### 3. CPU Usage

**Optimize threads** in `llm_handler.py`:
```python
self.llm = Llama(
    model_path=str(self.model_path),
    n_ctx=4096,
    n_threads=4,  # Adjust based on your CPU
    verbose=False
)
```

**CPU count guide:**
- 4 cores or less: `n_threads=2`
- 6-8 cores: `n_threads=4`
- 10+ cores: `n_threads=6`

---

### ❌ Database Locked

**Error:**
```
sqlite3.OperationalError: database is locked
```

**Cause:** Multiple processes accessing database simultaneously.

**Solution:**

```python
# In finance_db.py, increase timeout
conn = sqlite3.connect('data/finance.db', timeout=20.0)
```

**Or:**
```bash
# Close other instances of the app
pkill -f "python app.py"

# Restart
python app.py
```

---

### ❌ Memory Error

**Error:**
```
MemoryError: Not enough memory to load model
```

**Requirements:**
- Minimum 6GB RAM
- 4GB available for model
- 2GB for processing

**Solutions:**

=== "Option 1: Close applications"
    Free up RAM by closing:
    - Web browsers (especially Chrome)
    - Other Python processes
    - Large applications (IDEs, etc.)

=== "Option 2: Use smaller model"
    Replace with TinyLlama (only 600MB):
    ```python
    # In llm_handler.py
    model_path = Path("tinyllama-1.1b-chat-v1.0.Q5_K_M.gguf")
    ```
    
    Download from: https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF

=== "Option 3: Add swap space (Linux)"
    ```bash
    # Create 4GB swap file
    sudo fallocate -l 4G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    ```

---

## Data Issues

### ❌ Transactions Not Appearing

**Symptoms:**
- Upload succeeds but dashboard shows no data
- Transaction count shows 0

**Solutions:**

#### 1. Check Date Filter

**The date range filter might be excluding your data:**
- Expand date range to "All Time"
- Check actual transaction dates in the file

#### 2. Query Database Directly

```bash
sqlite3 data/finance.db

# Check if transactions exist
SELECT COUNT(*) FROM transactions;

# View recent transactions
SELECT * FROM transactions ORDER BY created_at DESC LIMIT 5;
```

#### 3. Check Category Filter

**Ensure categories are enabled:**
- Check all category checkboxes in the dashboard
- Some categories might be unchecked

---

### ❌ Wrong Categorization

**Symptoms:**
- "Whole Foods" categorized as "Dining" instead of "Groceries"
- Categories don't make sense

**Solutions:**

#### 1. Manually Fix & Train

**In the dashboard:**
1. Click on the transaction
2. Change category to correct one
3. System learns for future uploads

#### 2. Check Learned Mappings

```bash
sqlite3 data/finance.db
SELECT * FROM mem_labels;
```

**Remove incorrect mappings:**
```sql
DELETE FROM mem_labels WHERE keyword = 'whole foods';
```

#### 3. Improve Descriptions

**More context = better categorization:**

**Better:**
```
Whole Foods Market #123 - Seattle
```

**vs:**
```
Purchase
```

---

### ❌ Duplicate Transactions

**Symptoms:**
- Same transaction appears multiple times
- Upload shows doubled record count

**Cause:** Uploading the same file multiple times.

**Solutions:**

#### 1. Manual Deduplication

```sql
-- Find duplicates
SELECT date, description, amount, COUNT(*) 
FROM transactions 
GROUP BY date, description, amount 
HAVING COUNT(*) > 1;

-- Delete duplicates (keeps one copy)
DELETE FROM transactions 
WHERE id NOT IN (
    SELECT MIN(id) 
    FROM transactions 
    GROUP BY date, description, amount
);
```

#### 2. Prevent Future Duplicates

**Track uploaded files** in `app.py`:
```python
# Store file hash in database
import hashlib

def get_file_hash(file_path):
    with open(file_path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

# Check before processing
file_hash = get_file_hash(file_path)
# ... check if hash exists in documents_metadata table
```

---

## UI Issues

### ❌ Dashboard Not Loading

**Symptoms:**
- Browser shows "This site can't be reached"
- Page doesn't load

**Solutions:**

#### 1. Check if App is Running

```bash
# Look for this in terminal:
🌐 Dashboard running at: http://127.0.0.1:8050
```

**If not running:**
```bash
python app.py
```

#### 2. Try Different URL

```
# Try these:
http://127.0.0.1:8050
http://localhost:8050
http://0.0.0.0:8050
```

#### 3. Check Firewall

**macOS:**
```
System Preferences → Security & Privacy → Firewall
→ Allow Python to accept incoming connections
```

**Windows:**
```
Windows Defender Firewall → Allow an app
→ Add Python
```

---

### ❌ Upload Button Not Working

**Symptoms:**
- Click upload area, nothing happens
- Drag & drop doesn't work

**Solutions:**

#### 1. Check Browser Console

**Open developer tools:**
- Chrome/Edge: `F12` or `Cmd+Opt+I` (Mac) / `Ctrl+Shift+I` (Windows)
- Look for JavaScript errors

#### 2. Try Different Browser

Test in:
- Chrome
- Firefox
- Edge
- Safari

#### 3. Clear Browser Cache

```
Chrome: Cmd+Shift+Delete (Mac) / Ctrl+Shift+Delete (Windows)
Select "Cached images and files" → Clear
```

---

## PDF Issues

### ❌ "Could not extract text from PDF"

**Symptoms:**
- PDF upload succeeds but no transactions found
- "0 records processed"

**Causes & Solutions:**

#### 1. Scanned/Image PDF

**Enable OCR:**

=== "macOS"
    ```bash
    brew install tesseract
    ```

=== "Linux"
    ```bash
    sudo apt-get install tesseract-ocr
    ```

=== "Windows"
    Download from: https://github.com/UB-Mannheim/tesseract/wiki

**Then re-upload the PDF.**

#### 2. Password-Protected PDF

**Remove password first:**
```bash
# Using qpdf (install: brew install qpdf)
qpdf --password=PASSWORD --decrypt input.pdf output.pdf
```

#### 3. Corrupted PDF

**Try:**
- Re-download from bank
- Open in PDF reader to verify
- Convert to CSV instead

---

## Performance Issues

### ❌ High CPU Usage

**Symptoms:**
- Computer fans spinning loudly
- System becomes slow
- CPU usage at 100%

**Solutions:**

#### 1. Reduce Thread Count

```python
# In llm_handler.py
n_threads=2  # Lower from 4 to 2
```

#### 2. Process Files Sequentially

**Don't upload many files at once:**
- Upload 1-2 files at a time
- Wait for processing to complete

#### 3. Close Background Apps

Free up CPU by closing:
- Web browsers
- Other Python processes
- Development tools

---

### ❌ High Memory Usage

**Symptoms:**
- System memory full
- Computer becomes sluggish
- Swap usage high

**Solutions:**

#### 1. Check Memory Usage

=== "macOS"
    ```bash
    # Check memory
    vm_stat
    
    # Check process memory
    ps aux | grep python
    ```

=== "Linux"
    ```bash
    # Check memory
    free -h
    
    # Check process memory
    top -p $(pgrep -f "python app.py")
    ```

#### 2. Restart App Periodically

```bash
# If processing many files
pkill -f "python app.py"
python app.py
```

#### 3. Use Smaller Model

See [Memory Error](#memory-error) section above.

---

## Getting Help

If your issue isn't listed here:

### 1. Check Logs

```bash
# Run with verbose output
python app.py

# Check for errors in terminal output
```

### 2. Enable Debug Mode

```python
# In app.py
if __name__ == '__main__':
    app.run_server(debug=True)  # Enables detailed error messages
```

### 3. Check Database

```bash
# Verify database integrity
sqlite3 data/finance.db "PRAGMA integrity_check;"
```

### 4. Test Installation

```bash
python test_installation.py
```

### 5. Community Support

- 📖 Read the [FAQ](faq.md)
- 🐛 Open an issue on GitHub
- 💬 Ask in discussions

---

## Reset & Recovery

### Clean Reset

**⚠️ WARNING: This deletes all data!**

```bash
# Backup first
cp data/finance.db data/finance_backup.db

# Remove database
rm data/finance.db

# Remove temp files
rm -rf data/temp/*

# Restart app (will recreate database)
python app.py
```

### Restore from Backup

```bash
# Copy backup
cp data/finance_backup.db data/finance.db

# Restart app
python app.py
```

---

!!! tip "Prevention Tips"
    - Keep backups of your database
    - Update dependencies regularly: `pip install --upgrade -r requirements.txt`
    - Monitor disk space and memory
    - Test with small files first

!!! info "Still Stuck?"
    If you can't solve your issue, please:
    1. Check the [FAQ](faq.md)
    2. Search existing GitHub issues
    3. Open a new issue with details (error messages, logs, steps to reproduce)
