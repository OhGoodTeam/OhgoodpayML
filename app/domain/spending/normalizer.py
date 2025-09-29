import re

_CORP_WORDS = r"\b(주|㈜|주식회사|co\.|ltd\.|inc\.|corp\.|company)\b"

def normalize_merchant(name: str | None) -> str:
    if not name:
        return ""
    s = name.lower()
    s = re.sub(_CORP_WORDS, "", s)
    s = re.sub(r"[^a-z0-9가-힣\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s
