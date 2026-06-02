import secrets
import string


def generate_random_password(length: int = 16) -> str:
    """Generate a random strong password of specified length."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(alphabet) for _ in range(length))
