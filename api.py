import json
import os
import random
from pathlib import Path
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()
import sys
import traceback

def exception_handler(exc_type, exc_value, exc_traceback):
    traceback.print_exception(exc_type, exc_value, exc_traceback)

sys.excepthook = exception_handler

from agents.planner_agent.main import UniversalPlanner
from agents.researcher_agent.researcher import ResearcherAgent
from agents.content_generator.presentation_plan import PresentationPlannerAgent
from agents.content_generator.slide_content_agent import SlideContentAgent   # ✅ FIXED
from agents.content_generator.ppt_generator import AdvancedPPTGenerator

OUTPUT_DIR = Path("output/latest")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI()

# ─── HTML UI ────────────────────────────────────────────────────────────────

HTML_UI = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Neurovia Presentation Generator</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: system-ui, -apple-system, sans-serif; background: #f8fafc; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }
        .card { background: white; border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.08); padding: 40px; max-width: 600px; width: 100%; }
        h1 { font-size: 28px; font-weight: 700; color: #0f172a; margin-bottom: 8px; display: flex; align-items: center; gap: 10px; }
        .sub { color: #64748b; margin-bottom: 30px; font-size: 15px; }
        label { display: block; font-weight: 600; color: #1e293b; margin-bottom: 6px; font-size: 14px; }
        input, select { width: 100%; padding: 12px 16px; border: 1.5px solid #e2e8f0; border-radius: 12px; font-size: 15px; transition: 0.2s; background: #f8fafc; margin-bottom: 18px; }
        input:focus, select:focus { outline: none; border-color: #4f46e5; background: white; box-shadow: 0 0 0 3px rgba(79,70,229,0.1); }
        button { width: 100%; padding: 14px; background: #4f46e5; color: white; border: none; border-radius: 12px; font-size: 16px; font-weight: 600; cursor: pointer; transition: 0.2s; }
        button:hover { background: #4338ca; transform: translateY(-1px); }
        button:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
        #status { margin-top: 24px; padding: 16px 20px; border-radius: 12px; background: #f1f5f9; display: none; }
        #status .step { font-weight: 500; color: #1e293b; }
        #status .progress { margin-top: 8px; height: 6px; background: #e2e8f0; border-radius: 4px; overflow: hidden; }
        #status .progress-bar { height: 100%; width: 0%; background: #4f46e5; transition: width 0.3s; }
        #status .error { color: #dc2626; margin-top: 8px; }
        #download-btn { display: none; margin-top: 16px; background: #16a34a; }
        #download-btn:hover { background: #15803d; }
        .theme-info { font-size: 13px; color: #64748b; margin-top: -10px; margin-bottom: 16px; }
    </style>
</head>
<body>
<div class="card">
    <h1>🧠 Neurovia</h1>
    <p class="sub">Generate a professional PowerPoint presentation from any topic</p>

    <label for="topic">Topic</label>
    <input type="text" id="topic" placeholder="e.g. Deep Machine Learning" value="Cyber Security">

    <label for="theme">Theme</label>
    <select id="theme">
        <option value="random">🎲 Random</option>
        <option value="professional" selected>💼 Professional</option>
        <option value="medical">🏥 Medical</option>
        <option value="cyber">🔒 Cyber Security</option>
        <option value="business">💼 Business</option>
        <option value="tech">🚀 Technology</option>
        <option value="sunset">🌅 Sunset</option>
        <option value="nature">🌿 Nature</option>
        <option value="luxury">✨ Luxury</option>
        <option value="dark">🌙 Dark</option>
    </select>
    <p class="theme-info">Choose a theme or pick "Random" for a surprise</p>

    <button id="generate-btn">✨ Generate Presentation</button>

    <div id="status">
        <div class="step" id="step-text">⏳ Starting...</div>
        <div class="progress"><div class="progress-bar" id="progress-bar"></div></div>
        <div class="error" id="error-text"></div>
    </div>

    <button id="download-btn">⬇️ Download PPT</button>
</div>

<script>
    const generateBtn = document.getElementById('generate-btn');
    const downloadBtn = document.getElementById('download-btn');
    const statusDiv = document.getElementById('status');
    const stepText = document.getElementById('step-text');
    const progressBar = document.getElementById('progress-bar');
    const errorText = document.getElementById('error-text');
    let jobId = null;

    generateBtn.addEventListener('click', async () => {
        const topic = document.getElementById('topic').value.trim();
        if (!topic) { alert('Please enter a topic'); return; }
        const theme = document.getElementById('theme').value;

        generateBtn.disabled = true;
        generateBtn.textContent = '⏳ Generating...';
        statusDiv.style.display = 'block';
        stepText.textContent = '⏳ Starting generation...';
        progressBar.style.width = '0%';
        errorText.textContent = '';
        downloadBtn.style.display = 'none';

        try {
            const res = await fetch('/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic, theme })
            });
            const data = await res.json();
            if (res.ok) {
                pollStatus();
            } else {
                throw new Error(data.detail || 'Failed to start generation');
            }
        } catch (err) {
            stepText.textContent = '❌ Error';
            errorText.textContent = err.message;
            generateBtn.disabled = false;
            generateBtn.textContent = '✨ Generate Presentation';
        }
    });

    async function pollStatus() {
        try {
            const res = await fetch('/status');
            const data = await res.json();
            if (data.status === 'running') {
                stepText.textContent = `⏳ ${data.step || 'Processing...'}`;
                progressBar.style.width = (data.progress || 10) + '%';
                setTimeout(pollStatus, 2000);
            } else if (data.status === 'completed') {
                stepText.textContent = '✅ Done! Your presentation is ready.';
                progressBar.style.width = '100%';
                generateBtn.disabled = false;
                generateBtn.textContent = '✨ Generate Presentation';
                downloadBtn.style.display = 'block';
                jobId = data.result?.job_id || 'latest';
            } else if (data.status === 'failed') {
                stepText.textContent = '❌ Generation failed';
                errorText.textContent = data.error || 'Unknown error';
                generateBtn.disabled = false;
                generateBtn.textContent = '✨ Generate Presentation';
            } else {
                setTimeout(pollStatus, 2000);
            }
        } catch (err) {
            errorText.textContent = 'Error checking status';
            setTimeout(pollStatus, 3000);
        }
    }

    downloadBtn.addEventListener('click', () => {
        window.location.href = '/download';
    });
</script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def root():
    return HTML_UI

# ─── Request Model ────────────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    topic: str
    theme: str = "professional"

AVAILABLE_THEMES = ['professional', 'medical', 'cyber', 'business', 'tech', 'sunset', 'nature', 'luxury', 'dark']

def run_pipeline(topic: str, theme: str) -> dict:
    original_dir = os.getcwd()
    os.chdir(OUTPUT_DIR)

    if theme == "random" or theme not in AVAILABLE_THEMES:
        theme = random.choice(AVAILABLE_THEMES)
    print(f"🎨 Theme: {theme.upper()}")

    try:
        planner = UniversalPlanner()
        planner_output = planner.create_presentation(topic)
        planner.save_output(planner_output)

        researcher = ResearcherAgent()
        research_data = researcher.run(planner_output)
        with open("research_output.json", "w") as f:
            json.dump(research_data, f, indent=4)

        pres_planner = PresentationPlannerAgent()
        pres_plan = pres_planner.run(research_data)
        with open("presentation_plan.json", "w") as f:
            json.dump(pres_plan, f, indent=4)

        # ✅ Use SlideContentAgent, not LayoutRegistry
        content_agent = SlideContentAgent()
        slide_plan = content_agent.run(research_data, pres_plan)
        with open("slide_plan.json", "w") as f:
            json.dump(slide_plan, f, indent=4)

        generator = AdvancedPPTGenerator(theme=theme)
        pptx_filename = generator.generate(slide_plan)
        pptx_path = Path.cwd() / pptx_filename

        return {
            "topic": topic,
            "theme_used": theme,
            "pptx_path": str(pptx_path),
            "slide_count": len(slide_plan.get("slides", [])),
        }
    finally:
        os.chdir(original_dir)

# ─── Background Task ──────────────────────────────────────────────────────

generation_status = {"status": "idle", "result": None, "error": None}

def background_generate(request: GenerateRequest):
    global generation_status
    try:
        generation_status["status"] = "running"
        generation_status["step"] = "Starting pipeline..."
        generation_status["progress"] = 10
        result = run_pipeline(request.topic, request.theme)
        generation_status["result"] = result
        generation_status["status"] = "completed"
        generation_status["progress"] = 100
        generation_status["step"] = "Done"
    except Exception as e:
        generation_status["status"] = "failed"
        generation_status["error"] = str(e)

# ─── Endpoints ─────────────────────────────────────────────────────────────

@app.post("/generate")
def generate(request: GenerateRequest, background_tasks: BackgroundTasks):
    global generation_status
    if generation_status["status"] == "running":
        raise HTTPException(409, "Generation already in progress. Please wait.")
    generation_status = {"status": "pending", "step": "Queued", "progress": 0, "result": None, "error": None}
    background_tasks.add_task(background_generate, request)
    return {"message": "Generation started"}

@app.get("/status")
def get_status():
    return generation_status

@app.get("/download")
def download_latest():
    if generation_status["status"] != "completed":
        raise HTTPException(400, "PPT not ready yet.")
    pptx_path = generation_status["result"].get("pptx_path")
    if not pptx_path or not Path(pptx_path).exists():
        raise HTTPException(404, "PPT file not found.")
    return FileResponse(pptx_path, filename=Path(pptx_path).name)

@app.get("/health")
def health():
    return {"status": "healthy", "output_dir": str(OUTPUT_DIR)}