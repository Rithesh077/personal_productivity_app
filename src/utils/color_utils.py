"""color utility functions."""

from constants.design import TEAL, AMBER, RED, PURPLE, MUTED


def get_performance_color(
    pct: int,
    high_threshold: int = 80,
    medium_threshold: int = 50,
    high_color: str = TEAL,
    medium_color: str = AMBER,
    low_color: str = MUTED,
) -> str:
    """return color based on percentage thresholds."""
    if pct >= high_threshold:
        return high_color
    if pct >= medium_threshold:
        return medium_color
    return low_color


def get_on_time_color(pct: int) -> str:
    """color for on-time completion rates."""
    return get_performance_color(
        pct, high_threshold=80, medium_threshold=50,
        high_color=TEAL, medium_color=AMBER, low_color=RED,
    )


def get_same_day_color(pct: int) -> str:
    """color for same-day execution rates."""
    return get_performance_color(
        pct, high_threshold=80, medium_threshold=50,
        high_color=TEAL, medium_color=PURPLE, low_color=MUTED,
    )
