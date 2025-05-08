import os
import subprocess
import tempfile
import glob
from dotenv import load_dotenv

from supabase import create_client
import psycopg2
from openai import OpenAI

# 0) Load environment variables from worker/.env
load_dotenv()

# 1) Initialize Supabase client (service-role key)
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
)

# 2) Helper to get a fresh Postgres connection
def get_db_conn():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    conn.autocommit = True
    return conn

# 3) Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_video(job_id: int, prompt: str):
    """
    RQ task: generate and upload a Manim animation based on the prompt,
    then mark the job completed in Neon.
    """

    # ── STEP 1: mark the job as processing ────────────────────────────
    db = get_db_conn()
    with db.cursor() as cur:
        cur.execute(
            "UPDATE job SET status = %s WHERE id = %s",
            ("processing", job_id),
        )
    db.close()

    # ── STEP 2: generate the Manim script (or stub in DEV mode) ───────
    if os.getenv("DEV_NO_OPENAI") == "1":
        # simple hard‑coded fallback for local dev
        script = """
from manim import *

class Scene(Scene):
    def construct(self):
        square = Square()
        self.play(Create(square))
        self.wait(1)
"""
    else:
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Generate a Manim Python script defining a Scene class."
                },
                {"role": "user", "content": prompt},
            ],
        )
        # Prepend the import so the user script can assume manim symbols are available
        script = "from manim import *\n" + resp.choices[0].message.content

    # ── STEP 3: write the script into the OS temp directory ───────────
    temp_dir = tempfile.gettempdir()
    script_path = os.path.join(temp_dir, f"script_{job_id}.py")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script)

    # ── STEP 4: render the video with Manim ──────────────────────────
    media_dir = os.path.join(temp_dir, f"media_{job_id}")
    os.makedirs(media_dir, exist_ok=True)
    subprocess.run(
        ["manim", "-pql", "--media_dir", media_dir, script_path, "Scene"],
        check=True,
    )

    # ── STEP 5: locate the generated .mp4 (walk nested folders) ───────
    videos_root = os.path.join(media_dir, "videos")
    video_path = None
    for root, _, files in os.walk(videos_root):
        for fname in files:
            if fname.endswith(".mp4"):
                video_path = os.path.join(root, fname)
                break
        if video_path:
            break

    if not video_path:
        raise FileNotFoundError(f"No .mp4 found under {videos_root!r}")

    # ── STEP 6: upload to Supabase Storage ────────────────────────────
    storage_path = f"{job_id}.mp4"
    with open(video_path, "rb") as vid:
        res = supabase.storage.from_("videos").upload(storage_path, vid)

    # supabase-py v1 returns an object without .error; guard for both cases
    err = getattr(res, "error", None)
    if err is None and isinstance(res, dict):
        err = res.get("error")

    if err:
        raise Exception(f"Supabase upload failed: {err!r}")

    # ── STEP 7: mark job completed in Neon ────────────────────────────
    db = get_db_conn()
    with db.cursor() as cur:
        cur.execute(
            'UPDATE job SET status = %s, "storage_path" = %s WHERE id = %s',
            ("completed", storage_path, job_id),
        )
    db.close()

    print(f"✅ Job {job_id} completed, video at {storage_path}")
