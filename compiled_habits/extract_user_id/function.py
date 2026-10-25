import re
from typing import Union

def execute(input_text: str) -> Union[str, str]:
    """Compiled habit for extracting user_id in tau-bench.
    Format: [first_name]_[last_name]_[4-digits], e.g. 'omar_davis_3817'.
    Returns the user_id or 'unsure' if ambiguous.
    """
    if not input_text or not isinstance(input_text, str):
        return "unsure"

    # Match candidate user IDs
    pattern = r'\b([a-z]+_[a-z]+_\d{4})\b'
    matches = list(set(re.findall(pattern, input_text.lower())))

    # If exactly one distinct user ID is found:
    if len(matches) == 1:
        return matches[0]

    # If zero or multiple competing user IDs exist:
    return "unsure"
