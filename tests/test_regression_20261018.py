import os
os.environ['DATABASE_URL'] = 'sqlite://'
import unittest
from unittest.mock import patch
from sqlalchemy.exc import OperationalError
from app.main import init_db

class StartupRetryTests(unittest.TestCase):
    def test_invalid_retry_counts_do_not_silently_skip_initialization(self):
        for retries in [0, -1, True, 1.5, '2']:
            with self.subTest(retries=retries), self.assertRaises(ValueError):
                init_db(retries=retries)

    def test_retries_then_succeeds(self):
        error = OperationalError('connect', {}, Exception('unavailable'))
        with patch('app.main.Base.metadata.create_all', side_effect=[error, None]) as create, patch('app.main.time.sleep') as sleep:
            init_db(retries=2, delay=0)
            self.assertEqual(create.call_count, 2)
            sleep.assert_called_once_with(0)

    def test_last_failure_is_propagated(self):
        error = OperationalError('connect', {}, Exception('unavailable'))
        with patch('app.main.Base.metadata.create_all', side_effect=error), patch('app.main.time.sleep') as sleep:
            with self.assertRaises(OperationalError):
                init_db(retries=1)
            sleep.assert_not_called()
