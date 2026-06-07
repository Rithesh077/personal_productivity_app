"""tests for math utility functions."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.math_utils import safe_percentage


class TestSafePercentage:

    def test_normal_percentage(self):
        assert safe_percentage(50, 100) == 50

    def test_zero_denominator(self):
        assert safe_percentage(10, 0) == 0

    def test_full_completion(self):
        assert safe_percentage(5, 5) == 100

    def test_zero_numerator(self):
        assert safe_percentage(0, 10) == 0

    def test_truncates_to_int(self):
        # 1/3 = 33.33...% → should be 33
        assert safe_percentage(1, 3) == 33

    def test_both_zero(self):
        assert safe_percentage(0, 0) == 0

    def test_large_numbers(self):
        assert safe_percentage(999, 1000) == 99
