"""Categorization Agent

Assigns categories and subcategories to transactions using:
- Learned memory labels (keyword -> category/subcategory)
- Simple heuristics by description/amount
- Optional LLM suggestions if available

Also returns a list of uncertain transactions for manual review.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple

from .llm_handler import is_llm_available, get_llm_handler
from .finance_db import get_mem_labels, get_conn


@dataclass
class Categorized:
    date: Optional[str]
    amount: Optional[float]
    description: str
    category: str
    subcategory: Optional[str] = None


def _norm(s: str) -> str:
    return (s or "").strip().lower()


class CategorizationAgent:
    """Lightweight categorization agent."""

    def __init__(self) -> None:
        self.use_llm = is_llm_available()
        # cache memory labels at start; agent methods can accept overrides
        self.mem_labels = self._load_mem_labels()

    def _load_mem_labels(self) -> List[Tuple[str, str, Optional[str]]]:
        # Backwards-compatible: get_mem_labels() returns (keyword, category)
        # If subcategory also exists in DB, fetch via SQL here to avoid API changes.
        rows: List[Tuple[str, str]] = get_mem_labels()
        enriched: List[Tuple[str, str, Optional[str]]] = []
        try:
            con = get_conn()
            cur = con.cursor()
            cur.execute("PRAGMA table_info(mem_labels)")
            cols = [r[1] for r in cur.fetchall()]
            has_sub = "subcategory" in cols
            if has_sub:
                cur.execute("SELECT keyword, category, subcategory FROM mem_labels")
                enriched = [(k, c, sc) for k, c, sc in cur.fetchall()]
            else:
                enriched = [(k, c, None) for k, c in rows]
        finally:
            try:
                con.close()
            except Exception:
                pass
        # Sort labels by keyword length desc so longest match wins
        enriched.sort(key=lambda t: len(t[0] or ""), reverse=True)
        return enriched

    def categorize_transactions(self, transactions: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Tuple[str, str]]]:
        """Categorize a batch of transaction dicts.

        Args:
            transactions: list of dicts with at least description and amount

        Returns:
            (updated_transactions, uncertain_items)
            - updated_transactions: original list with category/subcategory set
            - uncertain_items: list of (description, source_file) for manual review
        """
        updated: List[Dict[str, Any]] = []
        uncertain: List[Tuple[str, str]] = []

        for t in transactions:
            desc = str(t.get("description") or "").strip()
            src = str(t.get("source_file") or t.get("_source_file") or "")
            amount = t.get("amount")

            category, subcategory, certain = self._categorize_single(desc, amount)

            t_out = dict(t)
            if category:
                t_out["category"] = category
            if subcategory:
                t_out["subcategory"] = subcategory

            # Mark uncertain if we couldn't assign a category confidently
            if not category or not certain:
                uncertain.append((desc, src))
                # Ensure at least placeholder category
                t_out.setdefault("category", "Uncategorized")

            updated.append(t_out)

        # dedupe uncertain list
        seen = set()
        deduped: List[Tuple[str, str]] = []
        for d, s in uncertain:
            key = (d.strip(), s.strip())
            if key in seen:
                continue
            seen.add(key)
            deduped.append(key)

        return updated, deduped

    def _categorize_single(self, description: str, amount: Optional[float]) -> Tuple[Optional[str], Optional[str], bool]:
        d = _norm(description)
        if not d:
            return None, None, False

        # 1) Memory labels (longest keyword wins)
        for keyword, cat, subcat in self.mem_labels:
            if keyword and keyword in d:
                return cat, subcat, True

        # 2) Simple heuristics
        cat, subcat = self._heuristics(description, amount)
        if cat:
            return cat, subcat, True

        # 3) Optional LLM suggestion
        if self.use_llm:
            try:
                llm = get_llm_handler()
                prompt = llm.create_instruct_prompt(
                    instruction=(
                        "You are a finance categorization assistant. "
                        "Given a transaction description and amount (negative expense, positive income), "
                        "return a JSON with fields: category, subcategory, confidence (0-1). "
                        "Use common personal finance categories like Groceries, Dining, Transport, Housing, Utilities, Healthcare, Entertainment, Subscriptions, Income, Savings, Adjustments."
                    ),
                    context=f"description: {description}\namount: {amount}")
                res = llm.generate_json(prompt, max_tokens=128, temperature=0.1, agent_type="organizer")
                cat2 = (res or {}).get("category")
                sub2 = (res or {}).get("subcategory")
                conf = float((res or {}).get("confidence", 0))
                if cat2 and conf >= 0.6:
                    return cat2, sub2, conf >= 0.8
                # If LLM suggested but low confidence, keep as uncertain but include suggestion
                if cat2:
                    return cat2, sub2, False
            except Exception:
                pass

        return None, None, False

    def _heuristics(self, description: str, amount: Optional[float]) -> Tuple[Optional[str], Optional[str]]:
        d = _norm(description)
        if amount is not None and amount > 0 and any(k in d for k in ["salary", "payroll", "transfer in", "refund", "deposit"]):
            return "Income", "Payroll" if "salary" in d or "payroll" in d else None
        if any(k in d for k in ["whole foods", "trader joe", "aldi", "walmart", "tesco", "sainsbury", "grocery", "supermarket"]):
            return "Groceries", None
        if any(k in d for k in ["uber", "lyft", "shell", "bp ", "exxon", "fuel", "metro", "train", "bus"]):
            return "Transport", None
        if any(k in d for k in ["netflix", "spotify", "prime", "icloud", "subscription", "subs"]):
            return "Subscriptions", None
        if any(k in d for k in ["airbnb", "hotel", "booking.com", "expedia", "travel"]):
            return "Entertainment", "Travel"
        if any(k in d for k in ["rent", "mortgage", "landlord"]):
            return "Housing", None
        if any(k in d for k in ["electric", "gas bill", "water", "utility", "utilities", "internet", "broadband"]):
            return "Utilities", None
        if any(k in d for k in ["starbucks", "cafe", "coffee", "restaurant", "mcdonald", "kfc", "dining"]):
            return "Dining", None
        if any(k in d for k in ["pharmacy", "doctor", "hospital", "clinic"]):
            return "Healthcare", None
        return None, None
