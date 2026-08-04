"""math utility functions."""


def safe_percentage(numerator: int, denominator: int) -> int:
    """integer percentage, safe against division by zero."""
    if denominator == 0:
        return 0
    return int(numerator / denominator * 100)
