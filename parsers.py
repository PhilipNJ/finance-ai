import io
import re
from typing import List, Tuple

import pandas as pd

# Optional dependencies for PDF/OCR
try:
    import pdfplumber  # type: ignore
except Exception:
    pdfplumber = None

try:
    import pytesseract  # type: ignore
    from PIL import Image  # type: ignore
except Exception:
    pytesseract = None
    Image = None

DEFAULT_RULES = [
    (r"salary|payroll|direct\s*deposit", "Income"),
    (r"uber|lyft|taxi|transport", "Transport"),
    (r"grocery|supermarket|whole\s*foods|trader\s*joes|aldi|costco", "Groceries"),
    (r"rent|mortgage|landlord", "Housing"),
    (r"netflix|spotify|subscription|prime", "Subscriptions"),
    (r"interest|dividend|refund|rebate", "Adjustments"),
    (r"coffee|cafe|starbucks", "Dining"),
]


def parse_csv(content: bytes) -> pd.DataFrame:
    bio = io.BytesIO(content)
    try:
        df = pd.read_csv(bio)
    except Exception:
        bio.seek(0)
        df = pd.read_csv(bio, sep=';')
    cols = {c.lower().strip(): c for c in df.columns}
    date_col = next((cols[c] for c in cols if c in {'date', 'transaction date', 'posted', 'time'}), None)
    amt_col = next((cols[c] for c in cols if c in {'amount', 'amt', 'value', 'debit', 'credit'}), None)
    desc_col = next((cols[c] for c in cols if c in {'description', 'memo', 'narrative', 'details', 'name'}), None)
    if not (date_col and amt_col and desc_col):
        possible = list(df.columns)
        date_col = date_col or possible[0]
        amt_col = amt_col or possible[1] if len(possible) > 1 else possible[0]
        desc_col = desc_col or possible[2] if len(possible) > 2 else possible[-1]
    out = pd.DataFrame({
        'date': pd.to_datetime(df[date_col], errors='coerce').dt.date.astype(str),
        'amount': pd.to_numeric(df[amt_col], errors='coerce').fillna(0.0),
        'description': df[desc_col].astype(str).fillna('')
    })
    return out


def extract_text_from_pdf(content: bytes) -> str:
    if pdfplumber is None:
        return ""
    text_chunks = []
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            if not text and pytesseract and Image:
                try:
                    img = page.to_image(resolution=300).original
                    pil_img = Image.fromarray(img)
                    text = pytesseract.image_to_string(pil_img)
                except Exception:
                    text = ""
            text_chunks.append(text)
    return "\n".join(text_chunks)


def parse_pdf_to_rows(content: bytes) -> pd.DataFrame:
    raw = extract_text_from_pdf(content)
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    rows = []
    date_pat = re.compile(r"(\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{2,4})")
    amt_pat = re.compile(r"[-+]?\d{1,3}(?:,\d{3})*(?:\.\d{2})")
    for ln in lines:
        d_match = date_pat.search(ln)
        a_match = list(amt_pat.finditer(ln))
        if d_match and a_match:
            date_str = d_match.group(0)
            try:
                date = pd.to_datetime(date_str, dayfirst=False, errors='coerce').date()
            except Exception:
                date = None
            amount_str = a_match[-1].group(0).replace(',', '')
            try:
                amount = float(amount_str)
            except Exception:
                amount = 0.0
            desc = ln
            desc = desc.replace(date_str, '').replace(a_match[-1].group(0), '').strip(' -|:\t')
            rows.append({'date': str(date) if date else '', 'amount': amount, 'description': desc})
    if not rows:
        rows = [{'date': '', 'amount': 0.0, 'description': ln} for ln in lines]
    return pd.DataFrame(rows)


def categorize(description: str, amount: float, mem: List[Tuple[str, str]]) -> str:
    desc = (description or '').lower()
    for kw, cat in mem:
        if kw and kw in desc:
            return cat
    for pat, cat in DEFAULT_RULES:
        if re.search(pat, desc):
            return cat
    if amount > 0:
        return "Income"
    return "Uncategorized"
