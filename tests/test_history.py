import os
import unittest
from unittest.mock import Mock

os.environ['DATABASE_URL'] = 'sqlite://'

from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.db = Mock()
        self.db.scalars.return_value.all.return_value = []
        app.dependency_overrides[get_db] = lambda: self.db
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()
        self.client.close()

    def test_invalid_limits_do_not_query_database(self):
        for limit in ['-1', '0', '1001', 'invalid']:
            self.assertEqual(self.client.get('/metrics/history', params={'limit': limit}).status_code, 422)
        self.db.scalars.assert_not_called()

    def test_default_and_boundary_limits(self):
        for params in [{}, {'limit': 1}, {'limit': 1000}]:
            response = self.client.get('/metrics/history', params=params)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), [])


if __name__ == '__main__':
    unittest.main()
