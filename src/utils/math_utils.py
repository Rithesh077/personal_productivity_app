"""Math utility functions for Stride."""


def safe_percentage(numerator: int, denominator: int) -> int:
    """Calculate percentage safely, returning 0 if denominator is 0.

    Args:
        numerator: Numerator value
        denominator: Denominator value

    Returns:
        Percentage as integer (0-100), or 0 if denominator is 0
    """
    return int((numerator / denominator) * 100) if denominator > 0 else 0
