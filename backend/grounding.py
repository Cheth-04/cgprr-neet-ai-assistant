"""Conservative numeric grounding gate; not a full semantic fact checker."""
import re


def numbers_in(text):
    # Ignore digits within alphanumeric IDs such as FC001 and CR0005.
    return {int(m.replace(',', '')) for m in
            re.findall(r'(?<![A-Za-z0-9])\d[\d,]*(?![A-Za-z0-9])', text)}


def numerical_claims_supported(answer, retrieved_records):
    """Reject unseen numeric claims (including a planted false rank)."""
    if not retrieved_records:
        return False
    supported = set()
    for record in retrieved_records:
        supported |= numbers_in(record['text'])
    return numbers_in(answer).issubset(supported)
