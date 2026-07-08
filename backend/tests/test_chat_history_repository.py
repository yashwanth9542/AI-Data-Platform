import os
import tempfile
import unittest

from app.repositories.sqlite_chat_history_repository import SQLiteChatHistoryRepository


class ChatHistoryRepositoryTests(unittest.TestCase):
    def test_persists_messages_to_sqlite(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repository = SQLiteChatHistoryRepository(db_path=os.path.join(tmpdir, "history.db"))
            repository.add_message("session-1", "user", "hello")
            repository.add_message("session-1", "assistant", "hi")
            session = repository.get_session("session-1")
            self.assertEqual(len(session["messages"]), 2)


if __name__ == "__main__":
    unittest.main()
