from unittest.mock import patch
import pytest
from app.main import init_db

@pytest.mark.parametrize('delay', [-1, float('nan'), float('inf'), True, '1'])
def test_invalid_retry_delay_is_rejected_before_database_work(delay):
    with patch('app.main.Base.metadata.create_all') as create:
        with pytest.raises(ValueError, match='delay'):
            init_db(delay=delay)
        create.assert_not_called()

def test_zero_retry_delay_is_valid():
    with patch('app.main.Base.metadata.create_all') as create:
        init_db(delay=0)
        create.assert_called_once()
