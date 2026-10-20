import asyncio
import threading
from app import main

def test_database_initialization_runs_off_the_event_loop(monkeypatch):
 loop_thread=threading.get_ident()
 initialized=[]
 monkeypatch.setattr(main,'init_db',lambda: initialized.append(threading.get_ident()))
 async def start():
  async with main.lifespan(main.app):
   assert len(initialized)==1
   assert initialized[0]!=loop_thread
 asyncio.run(start())
