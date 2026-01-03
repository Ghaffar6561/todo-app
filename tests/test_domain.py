"""Tests for domain models and validation."""

import pytest
from datetime import date

from todo.domain.models import (
    validate_title,
    parse_due_date,
    validate_priority,
    parse_tags,
)
from todo.domain.errors import ValidationError


class TestValidateTitle:
    def test_valid_title(self):
        assert validate_title("Buy groceries") == "Buy groceries"

    def test_strips_whitespace(self):
        assert validate_title("  Buy groceries  ") == "Buy groceries"

    def test_empty_string_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_title("")
        assert "cannot be empty" in exc_info.value.message

    def test_whitespace_only_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_title("   ")
        assert "cannot be empty" in exc_info.value.message


class TestParseDueDate:
    def test_none_returns_none(self):
        assert parse_due_date(None) is None

    def test_valid_date(self):
        result = parse_due_date("2025-12-31")
        assert result == date(2025, 12, 31)

    def test_invalid_format_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            parse_due_date("12-31-2025")
        assert "Invalid date format" in exc_info.value.message

    def test_invalid_date_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            parse_due_date("2025-02-30")
        assert "Invalid date format" in exc_info.value.message

    def test_nonsense_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            parse_due_date("not-a-date")
        assert "Invalid date format" in exc_info.value.message


class TestValidatePriority:
    def test_none_returns_none(self):
        assert validate_priority(None) is None

    def test_low(self):
        assert validate_priority("low") == "low"

    def test_med(self):
        assert validate_priority("med") == "med"

    def test_high(self):
        assert validate_priority("high") == "high"

    def test_invalid_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_priority("urgent")
        assert "Invalid priority" in exc_info.value.message

    def test_case_sensitive(self):
        with pytest.raises(ValidationError):
            validate_priority("HIGH")


class TestParseTags:
    def test_none_returns_empty_list(self):
        assert parse_tags(None) == []

    def test_single_tag(self):
        assert parse_tags("work") == ["work"]

    def test_multiple_tags(self):
        assert parse_tags("work,home,urgent") == ["work", "home", "urgent"]

    def test_strips_whitespace(self):
        assert parse_tags(" work , home , urgent ") == ["work", "home", "urgent"]

    def test_empty_string_returns_empty_list(self):
        assert parse_tags("") == []

    def test_empty_tags_filtered(self):
        assert parse_tags("work,,home") == ["work", "home"]
