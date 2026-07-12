import unittest
from unittest.mock import patch

from app.providers.database.postgres import PostgresConnector
from app.providers.database.sqlite import SQLiteConnector
from app.providers.llm.factory import LLMProviderFactory


class ProviderTests(unittest.TestCase):
    def test_sqlite_connector_uses_config_path(self) -> None:
        connector = SQLiteConnector(path="/tmp/test.db")
        self.assertEqual(connector.path.name, "test.db")

    def test_postgres_connector_requires_dsn(self) -> None:
        connector = PostgresConnector(dsn=None)
        with self.assertRaises(Exception):
            connector.connect()

    def test_llm_provider_factory_requires_api_key(self) -> None:
        factory = LLMProviderFactory()
        with self.assertRaises(Exception):
            factory.create("openai")

    def test_llm_provider_factory_supports_grok(self) -> None:
        factory = LLMProviderFactory()
        with patch("app.providers.llm.factory.settings") as mock_settings:
            mock_settings.grok_api_key = "fake-key"
            provider = factory.create("grok")
            self.assertEqual(provider.__class__.__name__, "GrokProvider")


if __name__ == "__main__":
    unittest.main()
