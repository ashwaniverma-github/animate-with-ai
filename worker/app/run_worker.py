import os
import signal

# Monkey‑patch signal on Windows so RQ’s timeout logic doesn’t break
if os.name == 'nt':
    signal.SIGALRM = signal.SIGTERM
    signal.alarm = lambda secs: None
    signal.signal = lambda *args, **kwargs: None

from dotenv import load_dotenv
load_dotenv()  # loads REDIS_URL, etc., from worker/.env

from redis import Redis
from rq import Queue, SimpleWorker
from app.tasks import generate_video


if __name__ == '__main__':
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    conn = Redis.from_url(redis_url)
    q = Queue('videos', connection=conn)

    print("Starting SimpleWorker on queue 'videos' (no fork)…")
    worker = SimpleWorker([q], connection=conn)
    worker.work()
