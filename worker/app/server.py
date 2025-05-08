import signal
signal.SIGALRM = signal.SIGTERM  # or any valid signal on Windows

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from redis import Redis
from rq import Queue
import os

from .tasks import generate_video
from dotenv import load_dotenv
load_dotenv() 

class EnqueueRequest(BaseModel):
    jobId: int
    prompt: str

app = FastAPI()
redis_conn = Redis.from_url(os.getenv("REDIS_URL"))
queue = Queue('videos', connection=redis_conn)

@app.post("/enqueue")
async def enqueue(req: EnqueueRequest):
    try:
        queue.enqueue(generate_video, req.jobId, req.prompt)
    except Exception as e:
        raise HTTPException(500, str(e))
    return {"status": "enqueued", "jobId": req.jobId}