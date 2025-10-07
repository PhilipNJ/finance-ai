"""Multi-agent system for intelligent file processing and data extraction.

Implements three specialized agents:
- Agent 1 (ExtractionAgent): Extracts all information from uploaded files
- Agent 2 (OrganizerAgent): Organizes extracted data into structured JSONs
- Agent 3 (DatabaseAgent): Manages database schema and writes data
"""
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import pandas as pd

from llm_handler import get_llm_handler, is_llm_available
from parsers import extract_text_from_pdf, parse_csv
from finance_db import get_conn


class AgentWorkflow:
    """Orchestrator for the multi-agent workflow."""
    
    def __init__(self, temp_dir: Path):
        """Initialize the agent workflow.
        
        Args:
            temp_dir: Directory for temporary file storage.
        """
        self.temp_dir = temp_dir
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        self.extraction_agent = ExtractionAgent(temp_dir)
        self.organizer_agent = OrganizerAgent(temp_dir)
        self.database_agent = DatabaseAgent(temp_dir)
    
    def process_file(
        self,
        filename: str,
        content: bytes,
        file_type: str
    ) -> Tuple[bool, str, int]:
        """Process a file through the complete agent workflow.
        
        Args:
            filename: Name of the uploaded file.
            content: Raw file content.
            file_type: File extension (.csv, .pdf, .txt).
            
        Returns:
            Tuple of (success, message, num_records).
        """
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        
        try:
            # Agent 1: Extract information
            print(f"[Agent 1] Extracting information from {filename}...")
            output_1_path = self.extraction_agent.extract(
                filename, content, file_type, session_id
            )
            
            if not output_1_path.exists():
                return False, "Agent 1 failed to extract data", 0
            
            # Agent 2: Organize into structured data
            print(f"[Agent 2] Organizing extracted data...")
            organized_jsons = self.organizer_agent.organize(output_1_path, session_id)
            
            if not organized_jsons:
                return False, "Agent 2 failed to organize data", 0
            
            # Agent 3: Write to database
            print(f"[Agent 3] Writing to database...")
            num_records = self.database_agent.write_to_db(organized_jsons, filename)
            
            # Cleanup temporary files
            self._cleanup_session(session_id)
            
            return True, f"Successfully processed {filename}", num_records
            
        except Exception as e:
            # Cleanup on error
            self._cleanup_session(session_id)
            return False, f"Error processing {filename}: {str(e)}", 0
    
    def _cleanup_session(self, session_id: str):
        """Clean up temporary files for a session.
        
        Args:
            session_id: Unique session identifier.
        """
        try:
            for file in self.temp_dir.glob(f"*{session_id}*"):
                file.unlink()
            print(f"Cleaned up temporary files for session {session_id}")
        except Exception as e:
            print(f"Warning: Failed to cleanup session {session_id}: {e}")


class ExtractionAgent:
    """Agent 1: Extracts all information from uploaded files.
    
    This agent requires LLM support for intelligent extraction.
    """
    
    def __init__(self, temp_dir: Path):
        """Initialize the extraction agent.
        
        Args:
            temp_dir: Directory for temporary file storage.
        """
        self.temp_dir = temp_dir
        self.use_llm = is_llm_available()
        
        if not self.use_llm:
            print("WARNING: LLM not available. Extraction quality will be reduced.")
            print("Install llama-cpp-python for full AI capabilities.")
    
    def extract(
        self,
        filename: str,
        content: bytes,
        file_type: str,
        session_id: str
    ) -> Path:
        """Extract all information from a file.
        
        Args:
            filename: Name of the file.
            content: Raw file content.
            file_type: File extension (.csv, .pdf, .txt).
            session_id: Unique session identifier.
            
        Returns:
            Path to output_1.json file.
        """
        output_path = self.temp_dir / f"output_1_{session_id}.json"
        
        # Extract raw content based on file type
        if file_type == '.csv':
            raw_data = self._extract_from_csv(content)
        elif file_type == '.pdf':
            raw_data = self._extract_from_pdf(content)
        elif file_type == '.txt':
            raw_data = self._extract_from_text(content)
        else:
            raw_data = self._extract_from_text(content)
        
        # Always attempt LLM enhancement (AI-first approach)
        if raw_data.get('text') or raw_data.get('rows'):
            enhanced_data = self._llm_enhance_extraction(raw_data)
        else:
            enhanced_data = raw_data
        
        # Save output_1
        output_1 = {
            "filename": filename,
            "file_type": file_type,
            "session_id": session_id,
            "extracted_at": datetime.now().isoformat(),
            "raw_data": raw_data,
            "enhanced_data": enhanced_data
        }
        
        with open(output_path, 'w') as f:
            json.dump(output_1, f, indent=2)
        
        return output_path
    
    def _extract_from_csv(self, content: bytes) -> Dict[str, Any]:
        """Extract data from CSV file.
        
        Args:
            content: Raw CSV content.
            
        Returns:
            dict: Extracted data including rows and metadata.
        """
        try:
            df = parse_csv(content)
            return {
                "type": "csv",
                "rows": df.to_dict('records'),
                "columns": list(df.columns),
                "row_count": len(df),
                "text": df.to_string()
            }
        except Exception as e:
            return {
                "type": "csv",
                "error": str(e),
                "text": content.decode('utf-8', errors='ignore')
            }
    
    def _extract_from_pdf(self, content: bytes) -> Dict[str, Any]:
        """Extract data from PDF file.
        
        Args:
            content: Raw PDF content.
            
        Returns:
            dict: Extracted text and metadata.
        """
        try:
            text = extract_text_from_pdf(content)
            return {
                "type": "pdf",
                "text": text,
                "text_length": len(text)
            }
        except Exception as e:
            return {
                "type": "pdf",
                "error": str(e),
                "text": ""
            }
    
    def _extract_from_text(self, content: bytes) -> Dict[str, Any]:
        """Extract data from text file.
        
        Args:
            content: Raw text content.
            
        Returns:
            dict: Extracted text.
        """
        try:
            text = content.decode('utf-8', errors='ignore')
            return {
                "type": "text",
                "text": text,
                "text_length": len(text)
            }
        except Exception as e:
            return {
                "type": "text",
                "error": str(e),
                "text": ""
            }
    
    def _llm_enhance_extraction(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to enhance and structure the extracted data.
        
        Args:
            raw_data: Raw extracted data.
            
        Returns:
            dict: Enhanced data with LLM insights.
        """
        try:
            llm = get_llm_handler()
            
            # Get text content
            text = raw_data.get('text', '')
            if isinstance(raw_data.get('rows'), list):
                text = json.dumps(raw_data['rows'][:50])  # Limit to first 50 rows
            
            # Truncate if too long
            text = text[:3000]
            
            prompt = llm.create_instruct_prompt(
                instruction="""Analyze this financial document and extract key information.
Identify:
1. Document type (bank statement, credit card, invoice, budget, etc.)
2. Date range or relevant dates
3. Account information (if present)
4. Currency
5. Key financial entities (transactions, balances, totals)

Return your analysis as JSON with these fields: document_type, date_range, account_info, currency, entities.""",
                context=text
            )
            
            llm_response = llm.generate_json(prompt, max_tokens=512, temperature=0.1, agent_type="extraction")
            
            return {
                **raw_data,
                "llm_analysis": llm_response
            }
        except Exception as e:
            print(f"LLM enhancement failed: {e}")
            return raw_data


class OrganizerAgent:
    """Agent 2: Organizes extracted data into structured JSONs.
    
    This agent requires LLM support for intelligent data organization.
    """
    
    def __init__(self, temp_dir: Path):
        """Initialize the organizer agent.
        
        Args:
            temp_dir: Directory for temporary file storage.
        """
        self.temp_dir = temp_dir
        self.use_llm = is_llm_available()
        
        if not self.use_llm:
            print("WARNING: LLM not available. Organization will use pattern matching only.")
            print("Install llama-cpp-python for intelligent data organization.")
    
    def organize(self, output_1_path: Path, session_id: str) -> List[Path]:
        """Organize extracted data into structured JSONs.
        
        Args:
            output_1_path: Path to output_1.json file.
            session_id: Unique session identifier.
            
        Returns:
            List of paths to organized JSON files.
        """
        # Load output_1
        with open(output_1_path) as f:
            output_1 = json.load(f)
        
        organized_files = []
        
        # Determine data types present
        data_types = self._identify_data_types(output_1)
        
        # Create organized JSONs for each data type
        for data_type in data_types:
            organized_data = self._organize_by_type(output_1, data_type)
            
            if organized_data:
                output_path = self.temp_dir / f"organized_{data_type}_{session_id}.json"
                with open(output_path, 'w') as f:
                    json.dump(organized_data, f, indent=2)
                organized_files.append(output_path)
        
        return organized_files
    
    def _identify_data_types(self, output_1: Dict[str, Any]) -> List[str]:
        """Identify what types of data are present in the extraction.
        
        Args:
            output_1: Extracted data from Agent 1.
            
        Returns:
            List of data type identifiers.
        """
        data_types = []
        
        raw_data = output_1.get('raw_data', {})
        enhanced_data = output_1.get('enhanced_data', {})
        
        # Check for transactions (most common)
        if raw_data.get('type') == 'csv' and raw_data.get('rows'):
            # CSV likely contains transactions
            data_types.append('transactions')
        elif raw_data.get('type') in ['pdf', 'text']:
            # PDF/text might contain transactions or other data
            data_types.append('transactions')
        
        # Check LLM analysis for other data types
        llm_analysis = enhanced_data.get('llm_analysis', {})
        if llm_analysis:
            doc_type = llm_analysis.get('document_type', '').lower()
            
            if 'budget' in doc_type:
                data_types.append('budgets')
            if 'account' in doc_type or 'balance' in doc_type:
                data_types.append('accounts')
            if 'invoice' in doc_type:
                data_types.append('invoices')
        
        # Default to transactions if nothing identified
        if not data_types:
            data_types.append('transactions')
        
        return list(set(data_types))
    
    def _organize_by_type(
        self,
        output_1: Dict[str, Any],
        data_type: str
    ) -> Dict[str, Any]:
        """Organize data for a specific data type.
        
        Args:
            output_1: Extracted data from Agent 1.
            data_type: Type of data to organize.
            
        Returns:
            dict: Organized data structure.
        """
        if data_type == 'transactions':
            return self._organize_transactions(output_1)
        elif data_type == 'accounts':
            return self._organize_accounts(output_1)
        elif data_type == 'budgets':
            return self._organize_budgets(output_1)
        elif data_type == 'invoices':
            return self._organize_invoices(output_1)
        else:
            return {}
    
    def _organize_transactions(self, output_1: Dict[str, Any]) -> Dict[str, Any]:
        """Organize transaction data.
        
        Args:
            output_1: Extracted data from Agent 1.
            
        Returns:
            dict: Organized transaction data.
        """
        raw_data = output_1.get('raw_data', {})
        enhanced_data = output_1.get('enhanced_data', {})
        
        transactions = []
        
        # AI-first approach: Try LLM extraction for all types
        if self.use_llm:
            # Use LLM for intelligent extraction even from CSV
            transactions = self._llm_extract_transactions(output_1)
            
            # If LLM extraction failed or returned nothing, fall back to CSV parsing
            if not transactions and raw_data.get('type') == 'csv' and raw_data.get('rows'):
                print("LLM extraction returned no results, using structured CSV data...")
                for row in raw_data['rows']:
                    trans = self._normalize_transaction(row)
                    if trans:
                        transactions.append(trans)
        else:
            # Fallback to structured parsing only if LLM unavailable
            if raw_data.get('type') == 'csv' and raw_data.get('rows'):
                for row in raw_data['rows']:
                    trans = self._normalize_transaction(row)
                    if trans:
                        transactions.append(trans)
            else:
                transactions = self._pattern_extract_transactions(raw_data.get('text', ''))
        
        return {
            "data_type": "transactions",
            "records": transactions,
            "metadata": {
                "source_file": output_1.get('filename'),
                "extracted_at": output_1.get('extracted_at'),
                "record_count": len(transactions)
            }
        }
    
    def _normalize_transaction(self, row: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normalize a transaction row to standard format.
        
        Args:
            row: Raw transaction data.
            
        Returns:
            dict: Normalized transaction or None if invalid.
        """
        # Try to extract date, amount, description
        trans = {}
        
        # Find date field
        for key in ['date', 'transaction_date', 'posted', 'time']:
            if key in row:
                trans['date'] = str(row[key])
                break
        
        # Find amount field
        for key in ['amount', 'amt', 'value', 'debit', 'credit']:
            if key in row:
                try:
                    trans['amount'] = float(row[key])
                    break
                except (ValueError, TypeError):
                    pass
        
        # Find description field
        for key in ['description', 'memo', 'narrative', 'details', 'name']:
            if key in row:
                trans['description'] = str(row[key])
                break
        
        # Additional fields
        trans['category'] = row.get('category', 'Uncategorized')
        trans['notes'] = row.get('notes', '')
        
        # Validate required fields
        if 'amount' not in trans:
            return None
        
        return trans
    
    def _llm_extract_transactions(self, output_1: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Use LLM to extract transactions from unstructured text.
        
        Args:
            output_1: Extracted data from Agent 1.
            
        Returns:
            List of transaction dictionaries.
        """
        try:
            llm = get_llm_handler()
            
            text = output_1.get('raw_data', {}).get('text', '')[:3000]
            
            prompt = llm.create_instruct_prompt(
                instruction="""Extract all financial transactions from this text.
For each transaction, identify:
- date (in YYYY-MM-DD format if possible)
- amount (as a number, negative for expenses, positive for income)
- description (what the transaction was for)

Return as JSON array: [{"date": "...", "amount": 0.0, "description": "..."}]""",
                context=text
            )
            
            llm_response = llm.generate_json(prompt, max_tokens=512, temperature=0.1, agent_type="extraction")
            
            if isinstance(llm_response, list):
                transactions = llm_response
            elif isinstance(llm_response, dict) and 'transactions' in llm_response:
                transactions = llm_response['transactions']
            else:
                transactions = []
            
            # Normalize each transaction
            return [self._normalize_transaction(t) for t in transactions if self._normalize_transaction(t)]
            
        except Exception as e:
            print(f"LLM transaction extraction failed: {e}")
            return []
    
    def _pattern_extract_transactions(self, text: str) -> List[Dict[str, Any]]:
        """Extract transactions using regex patterns (fallback method).
        
        Args:
            text: Raw text content.
            
        Returns:
            List of transaction dictionaries.
        """
        transactions = []
        
        # Simple pattern matching for common transaction formats
        date_pattern = r'(\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{2,4})'
        amount_pattern = r'[-+]?\$?\d{1,3}(?:,\d{3})*(?:\.\d{2})?'
        
        lines = text.split('\n')
        for line in lines:
            date_match = re.search(date_pattern, line)
            amount_matches = re.findall(amount_pattern, line)
            
            if date_match and amount_matches:
                # Extract transaction info
                date_str = date_match.group(0)
                amount_str = amount_matches[-1].replace('$', '').replace(',', '')
                
                try:
                    amount = float(amount_str)
                    # Remove date and amount from line to get description
                    desc = line.replace(date_str, '').replace(amount_matches[-1], '').strip(' -|:\t')
                    
                    transactions.append({
                        'date': date_str,
                        'amount': amount,
                        'description': desc,
                        'category': 'Uncategorized'
                    })
                except ValueError:
                    continue
        
        return transactions
    
    def _organize_accounts(self, output_1: Dict[str, Any]) -> Dict[str, Any]:
        """Organize account/balance data.
        
        Args:
            output_1: Extracted data from Agent 1.
            
        Returns:
            dict: Organized account data.
        """
        # Placeholder for account organization
        return {
            "data_type": "accounts",
            "records": [],
            "metadata": {
                "source_file": output_1.get('filename'),
                "extracted_at": output_1.get('extracted_at')
            }
        }
    
    def _organize_budgets(self, output_1: Dict[str, Any]) -> Dict[str, Any]:
        """Organize budget data.
        
        Args:
            output_1: Extracted data from Agent 1.
            
        Returns:
            dict: Organized budget data.
        """
        # Placeholder for budget organization
        return {
            "data_type": "budgets",
            "records": [],
            "metadata": {
                "source_file": output_1.get('filename'),
                "extracted_at": output_1.get('extracted_at')
            }
        }
    
    def _organize_invoices(self, output_1: Dict[str, Any]) -> Dict[str, Any]:
        """Organize invoice data.
        
        Args:
            output_1: Extracted data from Agent 1.
            
        Returns:
            dict: Organized invoice data.
        """
        # Placeholder for invoice organization
        return {
            "data_type": "invoices",
            "records": [],
            "metadata": {
                "source_file": output_1.get('filename'),
                "extracted_at": output_1.get('extracted_at')
            }
        }


class DatabaseAgent:
    """Agent 3: Manages database schema evolution and data writing."""
    
    def __init__(self, temp_dir: Path):
        """Initialize the database agent.
        
        Args:
            temp_dir: Directory for temporary file storage.
        """
        self.temp_dir = temp_dir
    
    def write_to_db(self, organized_jsons: List[Path], source_filename: str) -> int:
        """Analyze organized data and write to database.
        
        Args:
            organized_jsons: List of paths to organized JSON files.
            source_filename: Original source filename for tracking.
            
        Returns:
            int: Total number of records written.
        """
        total_records = 0
        
        for json_path in organized_jsons:
            with open(json_path) as f:
                organized_data = json.load(f)
            
            data_type = organized_data.get('data_type')
            records = organized_data.get('records', [])
            
            if not records:
                continue
            
            # Ensure table exists and matches data structure
            self._ensure_table_schema(data_type, records[0] if records else {})
            
            # Write records to database
            num_written = self._write_records(data_type, records, source_filename)
            total_records += num_written
        
        return total_records
    
    def _ensure_table_schema(self, data_type: str, sample_record: Dict[str, Any]):
        """Ensure database table exists with appropriate schema.
        
        Args:
            data_type: Type of data (transactions, accounts, etc.).
            sample_record: Sample record to infer schema from.
        """
        con = get_conn()
        try:
            cur = con.cursor()
            
            # Check if table exists
            cur.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (data_type,)
            )
            table_exists = cur.fetchone() is not None
            
            if data_type == 'transactions':
                # Transactions table should already exist, but check for new columns
                if table_exists:
                    self._add_missing_columns(cur, data_type, sample_record)
                # If not exists, it will be created by existing init_db()
            else:
                # Create new table for new data type
                if not table_exists:
                    self._create_dynamic_table(cur, data_type, sample_record)
                else:
                    self._add_missing_columns(cur, data_type, sample_record)
            
            con.commit()
        finally:
            con.close()
    
    def _create_dynamic_table(
        self,
        cursor,
        table_name: str,
        sample_record: Dict[str, Any]
    ):
        """Create a new table dynamically based on data structure.
        
        Args:
            cursor: Database cursor.
            table_name: Name of the table to create.
            sample_record: Sample record to infer schema from.
        """
        # Infer column types from sample record
        columns = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]
        
        for key, value in sample_record.items():
            col_type = self._infer_sql_type(value)
            columns.append(f"{key} {col_type}")
        
        # Add metadata columns
        columns.append("source_file TEXT")
        columns.append("created_at TEXT")
        
        create_sql = f"CREATE TABLE {table_name} ({', '.join(columns)})"
        
        print(f"Creating new table: {table_name}")
        cursor.execute(create_sql)
    
    def _add_missing_columns(
        self,
        cursor,
        table_name: str,
        sample_record: Dict[str, Any]
    ):
        """Add missing columns to an existing table.
        
        Args:
            cursor: Database cursor.
            table_name: Name of the table.
            sample_record: Sample record with potential new fields.
        """
        # Get existing columns
        cursor.execute(f"PRAGMA table_info({table_name})")
        existing_cols = {row[1] for row in cursor.fetchall()}
        
        # Add missing columns
        for key, value in sample_record.items():
            if key not in existing_cols:
                col_type = self._infer_sql_type(value)
                try:
                    cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {key} {col_type}")
                    print(f"Added column {key} to {table_name}")
                except Exception as e:
                    print(f"Failed to add column {key}: {e}")
    
    def _infer_sql_type(self, value: Any) -> str:
        """Infer SQL column type from Python value.
        
        Args:
            value: Python value to infer type from.
            
        Returns:
            str: SQL column type.
        """
        if isinstance(value, bool):
            return "INTEGER"  # SQLite uses INTEGER for boolean
        elif isinstance(value, int):
            return "INTEGER"
        elif isinstance(value, float):
            return "REAL"
        else:
            return "TEXT"
    
    def _write_records(
        self,
        data_type: str,
        records: List[Dict[str, Any]],
        source_filename: str
    ) -> int:
        """Write records to the database.
        
        Args:
            data_type: Type of data (table name).
            records: List of records to write.
            source_filename: Original source filename.
            
        Returns:
            int: Number of records written.
        """
        if not records:
            return 0
        
        con = get_conn()
        try:
            cur = con.cursor()
            
            # Get document_id if writing to transactions table
            document_id = None
            if data_type == 'transactions':
                from finance_db import insert_document
                document_id = insert_document(source_filename)
            
            written = 0
            for record in records:
                try:
                    # Prepare record with metadata
                    full_record = {**record}
                    full_record['source_file'] = source_filename
                    full_record['created_at'] = datetime.now().isoformat()
                    
                    # Special handling for transactions table
                    if data_type == 'transactions' and document_id:
                        full_record['document_id'] = document_id
                    
                    # Build INSERT query
                    columns = list(full_record.keys())
                    placeholders = ', '.join(['?' for _ in columns])
                    values = [full_record[col] for col in columns]
                    
                    insert_sql = f"INSERT INTO {data_type} ({', '.join(columns)}) VALUES ({placeholders})"
                    cur.execute(insert_sql, values)
                    written += 1
                    
                except Exception as e:
                    print(f"Failed to write record: {e}")
                    continue
            
            con.commit()
            return written
            
        finally:
            con.close()
