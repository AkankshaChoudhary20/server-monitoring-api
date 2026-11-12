import asyncio
from unittest.mock import Mock
import pytest
from app import main

@pytest.mark.parametrize('fail', [False, True])
def test_lifespan_disposes_pool_on_shutdown(monkeypatch, fail):
    monkeypatch.setattr(main, 'init_db', Mock())
    dispose = Mock()
    monkeypatch.setattr(main.engine, 'dispose', dispose)
    async def run():
        async with main.lifespan(main.app):
            dispose.assert_not_called()
            if fail:
                raise RuntimeError('service failure')
    if fail:
        with pytest.raises(RuntimeError):
            asyncio.run(run())
    else:
        asyncio.run(run())
    dispose.assert_called_once_with()
