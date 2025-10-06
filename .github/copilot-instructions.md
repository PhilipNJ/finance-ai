# Finance AI Dashboard - Copilot Instructions

## Project Overview
This is an offline personal finance dashboard built with Python and Dash. It allows users to upload bank/credit card statements (CSV or PDF), automatically parse and categorize transactions, and visualize spending patterns.

## Tech Stack
- **Framework**: Dash (Plotly)
- **Database**: SQLite3
- **Data Processing**: pandas
- **PDF Parsing**: pdfplumber, pytesseract (optional OCR)
- **Python Version**: 3.10+

## Project Structure
- `app.py` - Main Dash application and UI components
- `finance_db.py` - Database operations and schema
- `parsers.py` - CSV/PDF parsing and transaction categorization
- `utils.py` - Utility functions (filename sanitization, etc.)
- `data/` - SQLite database and uploaded files
- `assets/` - Static assets (CSS)

## Development Guidelines

### Code Style
- Follow PEP 8 conventions
- Use type hints for function parameters and returns
- Add docstrings to all functions and modules
- Use parameterized SQL queries (never string concatenation)

### Database Operations
- Always use `try/finally` blocks to close connections
- Use parameterized queries to prevent SQL injection
- Transactions are stored with: date, amount, description, category
- Memory labels store keyword-category mappings for learning

### File Handling
- Uploaded files are stored in `data/uploads/` with sanitized, hashed filenames
- Support both CSV and PDF formats
- PDF parsing includes optional OCR fallback with tesseract

### Security Considerations
- No external network calls (fully offline)
- File uploads use content hashing for uniqueness
- All file paths are sanitized
- SQL injection protection via parameterized queries

### Testing
- Manual testing via the web interface at http://127.0.0.1:8050
- Test CSV/PDF uploads with various bank statement formats
- Verify categorization rules work correctly

## Common Tasks

### Adding a New Category
Update the `categories` list in `app.py` and optionally add rules to `DEFAULT_RULES` in `parsers.py`.

### Improving Categorization
Add patterns to `DEFAULT_RULES` in `parsers.py` or let the memory system learn from manual categorization in the UI.

### Supporting New File Formats
Add parsing logic to `parsers.py` following the pattern of `parse_csv()` or `parse_pdf_to_rows()`.

## Future Enhancements
- Local LLM integration for smarter categorization (noted in comments)
- Embedding-based transaction matching with FAISS
- Budget tracking and alerts
- Multi-currency support

## Notes
- The app is designed to run completely offline with no external API calls
- The GGUF model file in the root is for future LLM integration (not yet implemented)
- Virtual environment is recommended: `.venv/`
