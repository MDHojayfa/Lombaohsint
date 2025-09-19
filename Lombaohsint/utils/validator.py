import re

def validate_target(target):
    """
    Validates if target is a valid email, phone number, username, or keyword.
    Returns True if valid, False otherwise.
    """
    if not target or not isinstance(target, str):
        return False

    # Email regex (RFC 5322 simplified)
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    # Phone number regex (E.164 format: +1234567890, with optional spaces/dashes/parens)
    phone_pattern = r'^\+?[0-9\s\-()\[\]]+$'

    # Username: alphanumeric, underscore, hyphen, 3–30 chars
    username_pattern = r'^[a-zA-Z0-9._-]{3,30}$'

    # Keyword: any non-whitespace string, 1–100 chars
    keyword_pattern = r'^[^\s]{1,100}$'

    # Check each type
    if re.match(email_pattern, target):
        return True
    if re.match(phone_pattern, target):
        # Validate as real phone number using phonenumbers lib if available
        try:
            import phonenumbers
            parsed = phonenumbers.parse(target, None)
            if phonenumbers.is_valid_number(parsed):
                return True
        except ImportError:
            # Fallback: just check format if phonenumbers not installed
            return True
        return False
    if re.match(username_pattern, target):
        return True
    if re.match(keyword_pattern, target):
        return True

    return False
