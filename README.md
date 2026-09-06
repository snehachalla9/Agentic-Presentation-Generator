# Agentic AI PPT Generation

An AI-powered presentation generation system that converts a topic into a structured PowerPoint presentation using planning, web research, content generation, and automated PPT rendering.

## Features

- Automated topic planning
- Web-based research
- Multi-agent content generation
- Audience-specific content
- Automatic PowerPoint generation
- LLM fallback handling

## Workflow

Topic → Supervisor → Planner → Research Agent → Content Agent → PPT Generation

## Agents

- **Supervisor** – manages the overall workflow
- **Planner** – breaks the topic into presentation modules
- **Research Agent** – researches and synthesizes information
- **Content Agent** – generates slide content based on the target audience

## Tech Stack

- Python
- LLMs
- AI Agents
- Web Research
- python-pptx
- FastAPI

## Project Structure

```text
├── agents/
├── assets/
├── output/
├── api.py
├── main.py
├── testing.py
└── requirements.txt
