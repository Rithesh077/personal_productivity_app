"""Color utility functions for Stride."""

from constants.design import TEAL, AMBER, RED, PURPLE, MUTED


def get_performance_color(
    pct: int,
    high_threshold: int = 80,
    medium_threshold: int = 50,
    high_color: str = TEAL,
    medium_color: str = AMBER,
    low_color: str = MUTED,
) -> str:
    """Get color based on percentage thresholds.

    Args:
        pct: Percentage value (0-100)
        high_threshold: % for high color (default 80)
        medium_threshold: % for medium color (default 50)
        high_color: Color for >= high_threshold (default TEAL)
        medium_color: Color for >= medium_threshold (default AMBER)
        low_color: Color for < medium_threshold (default MUTED)

    Returns:
        Color hex string
    """
    if pct >= high_threshold:
        return high_color
    if pct >= medium_threshold:
        return medium_color
    return low_color


def get_on_time_color(pct: int) -> str:
    """Get color for on-time completion (80% TEAL, 50% AMBER, else RED)."""
    return get_performance_color(pct, high_threshold=80, medium_threshold=50,
                                 high_color=TEAL, medium_color=AMBER, low_color=RED)


def get_same_day_color(pct: int) -> str:
    """Get color for same-day execution (80% TEAL, 50% PURPLE, else MUTED)."""
    return get_performance_color(pct, high_threshold=80, medium_threshold=50,
                                 high_color=TEAL, medium_color=PURPLE, low_color=MUTED)
