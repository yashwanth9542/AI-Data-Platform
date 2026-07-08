import unittest

from app.services.sql_validator import validate_select_statement


class SQLValidatorTests(unittest.TestCase):
    def test_allows_simple_select(self) -> None:
        self.assertTrue(validate_select_statement("SELECT * FROM sales"))

    def test_rejects_update_statement(self) -> None:
        self.assertFalse(validate_select_statement("UPDATE sales SET value = 1"))

    def test_rejects_drop_statement(self) -> None:
        self.assertFalse(validate_select_statement("DROP TABLE sales"))


if __name__ == "__main__":
    unittest.main()
