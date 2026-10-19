from unittest.mock import Mock
import pytest
from sqlalchemy.exc import OperationalError
from app import main

def test_failed_metric_commit_rolls_back_and_preserves_error(monkeypatch):
    monkeypatch.setattr(main, 'get_status_report', lambda: {'cpu': 1, 'memory': 2, 'disk': 3, 'status': 'OK'})
    db = Mock()
    error = OperationalError('INSERT', {}, Exception('database unavailable'))
    db.commit.side_effect = error
    with pytest.raises(OperationalError) as caught:
        main.metrics(db)
    assert caught.value is error
    db.rollback.assert_called_once_with()

def test_successful_metric_commit_does_not_roll_back(monkeypatch):
    report = {'cpu': 1, 'memory': 2, 'disk': 3, 'status': 'OK'}
    monkeypatch.setattr(main, 'get_status_report', lambda: report)
    db = Mock()
    assert main.metrics(db) == report
    db.commit.assert_called_once_with()
    db.rollback.assert_not_called()
