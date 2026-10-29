import shutil
import threading
import time
import uuid
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from agents.llm_gateway import LLMGateway
from agents.orchestrator.graph import build_graph

JOBS_DIR = Path("output/jobs")
JOBS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Neurovia API", version="1.0")
from fastapi.responses import RedirectResponse

@app.get("/", include_in_schema=False)
def index():
    return FileResponse("static/edit.html")

jobs: dict = {}                      # job_id -> status dict (in memory)
pipeline_lock = threading.Lock()     # agents write to shared output/ paths, so one job at a time
graph = build_graph(llm_gateway=LLMGateway())


class GenerateRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=200)


def make_initial_state(topic: str) -> dict:
    return {
        "topic": topic,
        "errors": [],
        "validation_results": {},
        "retry_count": {"planner": 0, "research": 0, "content": 0, "ppt": 0},
    }


def run_job(job_id: str, topic: str):
    job = jobs[job_id]
    with pipeline_lock:
        job["status"] = "running"
        started = time.time()
        try:
            final_state = graph.invoke(make_initial_state(topic))

            ppt = final_state.get("ppt")
            if not ppt or not Path(ppt).exists():
                reasons = "; ".join(map(str, final_state.get("errors", []))) or "unknown error"
                raise RuntimeError(f"No PPT produced: {reasons}")

            job_dir = JOBS_DIR / job_id
            job_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(ppt, job_dir / "presentation.pptx")

            slides = (final_state.get("content") or {}).get("slides", [])
            job.update(
                status="completed",
                pptx_path=str(job_dir / "presentation.pptx"),
                slide_count=len(slides),
                warnings=len(final_state.get("validation_results", {}).get("content_warnings", [])),
                errors=final_state.get("errors", []),
                slides=slides,
            )
        except Exception as e:
            job.update(status="failed", error=f"{type(e).__name__}: {e}")
        finally:
            job["duration_seconds"] = round(time.time() - started, 1)


@app.post("/generate", status_code=202)
def generate(req: GenerateRequest, background: BackgroundTasks):
    job_id = uuid.uuid4().hex[:12]
    jobs[job_id] = {"job_id": job_id, "topic": req.topic, "status": "queued"}
    background.add_task(run_job, job_id, req.topic)
    return {"job_id": job_id, "status": "queued"}


@app.get("/jobs/{job_id}")
def job_status(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return {k: v for k, v in job.items() if k != "slides"}


@app.get("/jobs/{job_id}/slides")
def job_slides(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    if job["status"] != "completed":
        raise HTTPException(409, f"Job is {job['status']}")
    return {"job_id": job_id, "slides": job["slides"]}


@app.get("/jobs/{job_id}/download")
def job_download(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    if job["status"] != "completed":
        raise HTTPException(409, f"Job is {job['status']}")
    return FileResponse(
        job["pptx_path"],
        filename=f"{job['topic'][:40].strip().replace(' ', '_')}.pptx",
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
    )


@app.get("/jobs")
def list_jobs():
    return [{k: v for k, v in j.items() if k != "slides"} for j in jobs.values()]


@app.get("/health")
def health():
    return {"status": "healthy", "jobs": len(jobs)}