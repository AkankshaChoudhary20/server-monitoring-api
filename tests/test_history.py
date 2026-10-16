import os
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import unittest
from unittest.mock import Mock

os.environ['DATABASE_URL'] = 'sqlite://'
from app.database import Base
from app.models import MetricRecord

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


class HistoryOrderingTests(unittest.TestCase):
    def test_tied_timestamps_select_newest_ids_and_return_oldest_first(self):
        from app.main import metrics_history
        engine = create_engine('sqlite://')
        Base.metadata.create_all(engine)
        try:
            with Session(engine) as db:
                timestamp = datetime(2026, 1, 1, tzinfo=timezone.utc)
                for cpu in [10, 20, 30, 40]:
                    db.add(MetricRecord(timestamp=timestamp, cpu_usage=cpu,
                                        memory_usage=1, disk_usage=1, status='healthy'))
                db.commit()
                self.assertEqual([row['cpu'] for row in metrics_history(limit=2, db=db)], [30, 40])
                self.assertEqual([row['cpu'] for row in metrics_history(limit=1, db=db)], [40])
        finally:
            engine.dispose()


if __name__ == '__main__':
    unittest.main()
