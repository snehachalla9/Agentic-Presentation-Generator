Agentic AI PPT Generation System

Agentic AI PPT Generation is a Python-based presentation generation system that transforms a topic into a structured PowerPoint presentation through automated planning, research, content generation, and PPTX rendering.

Overview

Creating a presentation usually requires multiple steps: deciding what to cover, researching the topic, organizing the material, writing slide content, and formatting the final presentation.

The system combines these steps into an automated pipeline using specialized AI agents and programmatic PowerPoint generation.

Key Features

Automated presentation planning — decomposes a topic into a structured presentation flow.

AI-powered research — gathers and synthesizes information for presentation modules.

Multi-agent workflow — separates planning, research, and content-generation responsibilities.

Audience-aware content generation — adapts generated material based on the intended audience.

PowerPoint generation — converts generated content into .pptx presentations using python-pptx.

Fallback handling — provides alternative generation paths when an LLM or research step encounters failures.

CLI and API access — supports both terminal-based generation and a FastAPI service.

Architecture

                         User Topic
                             |
                             v
                     +---------------+
                     |   Supervisor  |
                     +-------+-------+
                             |
                             v
                     +---------------+
                     |    Planner    |
                     +-------+-------+
                             |
                 +-----------+-----------+
                 |                       |
                 v                       v
          +-------------+         +-------------+
          |  Research   |         |   Content   |
          |    Agent    |         |    Agent    |
          +------+------+         +------+------+
                 |                       |
                 +-----------+-----------+
                             |
                             v
                    Presentation Content
                             |
                             v
                     +---------------+
                     |  PPT Renderer |
                     +-------+-------+
                             |
                             v
                    PowerPoint (.pptx)

Project Structure

Agentic-PPT-Generation/
├── agents/              # Planning, research, and content-generation agents
├── assets/              # Presentation assets and resources
├── output/              # Generated JSON and PowerPoint files
├── api.py               # FastAPI application
├── main.py              # CLI presentation-generation pipeline
├── testing.py           # Testing utilities
├── requirements.txt     # Python dependencies
└── README.md

Tech Stack

Language: Python

LLMs: Gemini / Groq

AI Architecture: Multi-agent workflow

Web Research: Tavily / Serper

Backend: FastAPI

Presentation Generation: python-pptx

Output: PowerPoint (.pptx) and intermediate JSON

Getting Started

1. Clone the repository

git clone https://github.com/snehachalla9/Agentic AI PPT Generation.git
cd Agentic AI PPT Generation

2. Create a virtual environment

python3 -m venv venv
source venv/bin/activate

3. Install dependencies

pip install -r requirements.txt

4. Configure API keys

Create a .env file in the project root:

TAVILY_API_KEY=your_tavily_api_key
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
SERPER_API_KEY=your_serper_api_key

Keep API keys private. Do not commit the .env file.

Run with CLI

python main.py

The CLI prompts for a topic and runs the presentation-generation pipeline. Intermediate outputs are stored under output/, and the generated PowerPoint is written there as well.

Run the FastAPI Application

Start the API server:

uvicorn api:app --reload

Open:

http://127.0.0.1:8000/

API Endpoints

Method

Endpoint

Purpose

GET

/

Web UI

POST

/generate

Start presentation generation

GET

/status

Check generation status

GET

/download

Download generated PPTX

GET

/health

Health check

Example

curl -X POST http://127.0.0.1:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"topic":"Cyber Security","theme":"professional"}'

Then check the generation status:

curl http://127.0.0.1:8000/status

Generation Flow

Topic
  ↓
Planning
  ↓
Research
  ↓
Content Generation
  ↓
Audience Adaptation
  ↓
PPTX Rendering
  ↓
Generated Presentation

The system also supports fallback handling so that individual research or LLM-generation failures do not necessarily stop the complete presentation-generation workflow.

Example Use Cases

The system can be used to generate presentations for:

University lectures

Technical topics

Research summaries

Business presentations

Educational content

Technology overviews

Future Improvements

More presentation themes and layouts

Improved slide-level content validation

Additional research providers

More granular control over presentation length and audience

Automated visual selection for slides

Evaluation of generated presentations using quality metrics

Author

Sneha Challa

GitHub: https://github.com/snehachalla9
