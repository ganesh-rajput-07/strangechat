# Basic moderation layer - banned words list
BANNED_WORDS = [
    "spam",
    "abuse",
    # Add more banned words as needed
]


def contains_banned_content(text: str) -> bool:
    """Check if text contains banned words"""
    text_lower = text.lower()
    for word in BANNED_WORDS:
        if word in text_lower:
            return True
    return False


def moderate_message(text: str) -> tuple[bool, str]:
    """
    Moderate a message.
    Returns (is_allowed, reason)
    """
    if contains_banned_content(text):
        return False, "Message contains inappropriate content"
    return True, ""
