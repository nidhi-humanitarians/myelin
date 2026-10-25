import re
from typing import Union

def execute(input_text: str) -> Union[str, str]:
    """Compiled habit for extracting airline reservation PNRs in tau-bench.
    Format: 6 alphanumeric characters with at least one letter and one digit.
    Returns the reservation code or 'unsure' if ambiguous.
    """
    if not input_text or not isinstance(input_text, str):
        return "unsure"

    pattern = r'\b([A-Z0-9]{6})\b'
    candidates = re.findall(pattern, input_text.upper())

    # Filter for valid PNRs (must contain at least one digit and one letter)
    valid_pnrs = list(set([
        c for c in candidates 
        if any(ch.isalpha() for ch in c) and any(ch.isdigit() for ch in c)
    ]))

    if len(valid_pnrs) == 1:
        return valid_pnrs[0]

    return "unsure"
