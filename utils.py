import hashlib
import os
import re


def unique_filename(original_name: str, content: bytes) -> str:
    sha = hashlib.sha1(content).hexdigest()[:12]
    base, ext = os.path.splitext(os.path.basename(original_name))
    safe_base = re.sub(r"[^A-Za-z0-9._-]", "_", base)[:40]
    return f"{safe_base}_{sha}{ext or ''}"
