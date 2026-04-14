"""math utility functions."""


def safe_percentage(numerator: int, denominator: int) -> int:
    """percentage safe from division by zero, returns 0-100."""
    return int((numerator / denominator) * 100) if denominator > 0 else 0
