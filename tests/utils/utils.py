import random
import string

def random_lower_string(k: int = 32) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=k))

def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"
