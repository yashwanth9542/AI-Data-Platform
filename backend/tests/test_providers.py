import unittest

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


if __name__ == "__main__":
    unittest.main()
