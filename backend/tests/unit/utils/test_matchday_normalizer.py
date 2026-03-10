"""Unit tests for matchday_normalizer utility."""

import pytest

from app.utils.matchday_normalizer import (
    get_search_friendly_matchday,
    normalize_matchday,
)


class TestNormalizeMatchday:
    """Test cases for normalize_matchday function."""

    def test_official_uefa_formats(self):
        """Test official UEFA naming conventions."""
        assert normalize_matchday("Round of 16 - 1st leg") == "Round of 16 - 1st leg"
        assert normalize_matchday("Round of 16 - 2nd leg") == "Round of 16 - 2nd leg"
        assert normalize_matchday("Quarter-finals") == "Quarter-finals"
        assert normalize_matchday("Semi-finals") == "Semi-finals"
        assert normalize_matchday("Final") == "Final"

    def test_mobile_abbreviations(self):
        """Test mobile app abbreviations (R16, QF, SF, F)."""
        assert normalize_matchday("R16") == "Round of 16"
        assert normalize_matchday("R16 - 1st leg") == "Round of 16 - 1st leg"
        assert normalize_matchday("r16 1st leg") == "Round of 16 - 1st leg"
        assert normalize_matchday("QF") == "Quarter-finals"
        assert normalize_matchday("QF - 2nd leg") == "Quarter-finals - 2nd leg"
        assert normalize_matchday("SF") == "Semi-finals"
        assert normalize_matchday("F") == "Final"

    def test_common_typos(self):
        """Test common typos and variations."""
        # "off" instead of "of"
        assert normalize_matchday("Round off 16 - 1st leg") == "Round of 16 - 1st leg"
        # Various spellings
        assert normalize_matchday("round of 16 first leg") == "Round of 16 - 1st leg"
        assert normalize_matchday("round 16 - 1st leg") == "Round of 16 - 1st leg"
        assert normalize_matchday("last 16 leg 1") == "Round of 16 - 1st leg"

    def test_alternative_names(self):
        """Test alternative names for stages."""
        assert normalize_matchday("last 16") == "Round of 16"
        assert normalize_matchday("quarters") == "Quarter-finals"
        assert normalize_matchday("last 8") == "Quarter-finals"
        assert normalize_matchday("semis") == "Semi-finals"
        assert normalize_matchday("last 4") == "Semi-finals"
        assert normalize_matchday("championship") == "Final"

    def test_leg_specifications(self):
        """Test various leg specification formats."""
        assert normalize_matchday("QF - first leg") == "Quarter-finals - 1st leg"
        assert normalize_matchday("SF leg 1") == "Semi-finals - 1st leg"
        assert normalize_matchday("R16 second leg") == "Round of 16 - 2nd leg"
        assert normalize_matchday("quarters leg 2") == "Quarter-finals - 2nd leg"

    def test_case_variations(self):
        """Test case-insensitive handling."""
        assert normalize_matchday("r16") == "Round of 16"
        assert normalize_matchday("R16") == "Round of 16"
        assert normalize_matchday("ROUND OF 16") == "Round of 16"
        assert normalize_matchday("qf") == "Quarter-finals"
        assert normalize_matchday("QF") == "Quarter-finals"

    def test_whitespace_handling(self):
        """Test extra whitespace handling."""
        assert normalize_matchday("  r16  -  1st  leg  ") == "Round of 16 - 1st leg"
        assert normalize_matchday("R16  1st leg") == "Round of 16 - 1st leg"

    def test_empty_input(self):
        """Test handling of None and empty string."""
        assert normalize_matchday(None) == ""
        assert normalize_matchday("") == ""
        assert normalize_matchday("   ") == ""

    def test_unknown_format_fallback(self):
        """Test fallback for unknown formats."""
        result = normalize_matchday("Unknown Format")
        assert result == "Unknown Format"


class TestGetSearchFriendlyMatchday:
    """Test cases for get_search_friendly_matchday function."""

    def test_ordinal_to_words(self):
        """Test conversion of ordinals to words."""
        assert (
            get_search_friendly_matchday("Round of 16 - 1st leg")
            == "Round of 16 first leg"
        )
        assert (
            get_search_friendly_matchday("Quarter-finals - 2nd leg")
            == "Quarter finals second leg"
        )

    def test_hyphen_removal(self):
        """Test hyphen and dash removal."""
        assert get_search_friendly_matchday("Semi-finals") == "Semi finals"
        assert get_search_friendly_matchday("Quarter-finals") == "Quarter finals"

    def test_whitespace_normalization(self):
        """Test whitespace normalization."""
        assert (
            get_search_friendly_matchday("Round  of  16  -  1st  leg")
            == "Round of 16 first leg"
        )

    @pytest.mark.parametrize(
        "normalized,expected",
        [
            ("Round of 16 - 1st leg", "Round of 16 first leg"),
            ("Round of 16 - 2nd leg", "Round of 16 second leg"),
            ("Quarter-finals - 1st leg", "Quarter finals first leg"),
            ("Semi-finals - 2nd leg", "Semi finals second leg"),
            ("Final", "Final"),
        ],
    )
    def test_search_friendly_conversion(self, normalized, expected):
        """Test comprehensive search-friendly conversion."""
        assert get_search_friendly_matchday(normalized) == expected


class TestFullNormalizationPipeline:
    """Integration tests for full normalization pipeline."""

    @pytest.mark.parametrize(
        "user_input,expected_normalized,expected_search",
        [
            # Mobile scenarios
            ("R16", "Round of 16", "Round of 16"),
            ("R16 - 1st leg", "Round of 16 - 1st leg", "Round of 16 first leg"),
            ("r16 1st leg", "Round of 16 - 1st leg", "Round of 16 first leg"),
            # Typo scenarios
            (
                "Round off 16 - 1st leg",
                "Round of 16 - 1st leg",
                "Round of 16 first leg",
            ),
            (
                "round of 16 first leg",
                "Round of 16 - 1st leg",
                "Round of 16 first leg",
            ),
            # Quarter-finals
            ("QF", "Quarter-finals", "Quarter finals"),
            ("QF - 2nd leg", "Quarter-finals - 2nd leg", "Quarter finals second leg"),
            # Semi-finals
            ("SF", "Semi-finals", "Semi finals"),
            ("semis 1st leg", "Semi-finals - 1st leg", "Semi finals first leg"),
            # Final
            ("F", "Final", "Final"),
            ("final", "Final", "Final"),
        ],
    )
    def test_full_pipeline(self, user_input, expected_normalized, expected_search):
        """Test full normalization and search-friendly conversion."""
        normalized = normalize_matchday(user_input)
        search_friendly = get_search_friendly_matchday(normalized)

        assert normalized == expected_normalized, (
            f"Normalization failed for '{user_input}': "
            f"expected '{expected_normalized}', got '{normalized}'"
        )
        assert search_friendly == expected_search, (
            f"Search conversion failed for '{normalized}': "
            f"expected '{expected_search}', got '{search_friendly}'"
        )
