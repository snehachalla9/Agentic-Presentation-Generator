# 🤖 Agentic AI PPT Generation

An agentic AI system that transforms a topic into a structured PowerPoint presentation through automated planning, research, content generation, audience adaptation, visual planning, validation, and programmatic PPTX generation.

The system is built as a modular multi-agent pipeline rather than a single LLM prompt. It separates presentation planning, web research, content generation, quality control, and PowerPoint rendering into dedicated components.

---

# ✨ Features

### 🤖 Multi-Agent Presentation Generation

* Supervisor Agent for workflow coordination
* Planner Agent for topic and curriculum planning
* Researcher Agent for web-based information retrieval
* Content Generation Agent for slide content creation
* Audience Adapter for audience-specific content
* Dedicated PPT Generator for PowerPoint rendering

### 🧠 Intelligent Planning

* Topic understanding and decomposition
* Curriculum and module planning
* Concept organization
* Research planning
* Structured presentation plans
* Graph-based workflow orchestration

### 🔍 Multi-Source Web Research

* Tavily search integration
* Serper search integration
* DuckDuckGo search integration
* Module-level research
* LLM-assisted research synthesis
* Configurable source limits and research settings

### 📝 AI Content Generation

* Structured slide content generation
* Content synthesis
* Content compression
* Audience adaptation
* Visual planning
* Speaker notes generation

### 🎨 Visual Presentation Generation

* Image planning
* Visual content construction
* Layout-aware slide generation
* Modular PowerPoint rendering
* `python-pptx` based PPTX generation

### ✅ Quality & Validation

* Generated-content validation
* Quality scoring
* Content compression
* Structured generation checks
* Modular processing for easier debugging

### 🛡️ LLM Reliability

* Configurable LLM provider
* Retry and fallback handling
* Modular generation to reduce large requests
* API failure handling
* Intermediate output storage

### 🌐 API Support

* FastAPI backend
* Presentation generation endpoint
* Generation status tracking
* Presentation download
* Health checking
* Browser-based generation interface

---

# 🏗️ System Architecture

The presentation-generation pipeline is organized into multiple stages:

```text
                         User Topic
                             │
                             ▼
                    ┌─────────────────┐
                    │ Supervisor Agent│
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Planner Agent  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Curriculum /    │
                    │ Topic Planning  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Research Agent  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Web Research    │
                    │ Tavily / Serper │
                    │ / DuckDuckGo    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Content Agent   │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
        Compression    Audience       Visual Planning
                       Adaptation
              │              │              │
              └──────────────┼──────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Quality /       │
                    │ Validation      │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ PPT Generator   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Final PPTX     │
                    └─────────────────┘
```

---

# 🔄 Generation Workflow

```text
Topic
  │
  ▼
Supervisor
  │
  ▼
Planning
  │
  ├── Topic Understanding
  ├── Curriculum Planning
  ├── Module Generation
  └── Research Planning
  │
  ▼
Research
  │
  ├── Tavily
  ├── Serper
  └── DuckDuckGo
  │
  ▼
Research Synthesis
  │
  ▼
Content Generation
  │
  ├── Content Synthesis
  ├── Compression
  ├── Audience Adaptation
  ├── Image Planning
  └── Speaker Notes
  │
  ▼
Validation / Quality Scoring
  │
  ▼
Visual & Layout Generation
  │
  ▼
PowerPoint Rendering
  │
  ▼
Final .pptx
```

---

# 🧩 Agents

## Supervisor Agent

The Supervisor coordinates the high-level presentation workflow and controls the transition between major generation stages.

It acts as the entry point for the agentic workflow before the request moves into planning, research, content generation, and presentation rendering.

---

## Planner Agent

The Planner converts an open-ended topic into a structured presentation plan.

### Responsibilities

* Understand the topic
* Decompose the topic into modules
* Build a presentation curriculum
* Organize concepts
* Determine research requirements
* Produce structured planning information

The planner is implemented as a separate module with its own configuration, source code, and tests.

---

## Researcher Agent

The Researcher Agent provides external information required by the presentation pipeline.

The research subsystem separates search providers into individual services:

```text
Researcher Agent
      │
      ├── Tavily Service
      │
      ├── Serper Service
      │
      └── DuckDuckGo Service
```

Research configuration includes source limits, content-length limits, LLM usage, provider selection, and maximum output tokens.

---

# 🔎 Research Pipeline

```text
Presentation Module
        │
        ▼
Research Requirement
        │
        ▼
Search Provider
        │
        ├── Tavily
        ├── Serper
        └── DuckDuckGo
        │
        ▼
Retrieved Information
        │
        ▼
LLM Synthesis
        │
        ▼
Research Context
```

This separation allows the research layer to work independently from the content-generation layer.

---

# 📝 Content Generation

The content-generation subsystem is composed of multiple specialized components rather than one large generation function.

```text
Content Generation
│
├── Agent
├── Audience Adapter
├── Compressor
├── Image Planner
├── Quality Scorer
├── Selector
├── Speaker Notes
├── Synthesizer
├── Validator
└── Visual Builder
```

This architecture allows different aspects of presentation generation to be handled independently.

---

# 🎯 Audience Adaptation

The system includes an audience-adaptation component that modifies generated presentation content according to the intended audience.

For example, the same topic can be structured differently depending on whether the target audience is:

* University students
* Technical professionals
* Business users
* General audiences

Audience adaptation occurs as part of the content-generation pipeline rather than requiring separate presentation templates for every audience.

---

# 🖼️ Visual Planning

The content-generation layer includes a dedicated image-planning component.

The visual planning stage determines where visual elements can be incorporated into the presentation before the final PowerPoint is rendered.

```text
Slide Content
     │
     ▼
Visual Planning
     │
     ▼
Visual Builder
     │
     ▼
PPT Rendering
```

This separates content decisions from the final slide-rendering process.

---

# 🗣️ Speaker Notes

Speaker-note generation is handled separately from the main slide content.

This allows the presentation to contain concise slide material while maintaining additional explanatory material for the presenter.

```text
Generated Slide Content
        │
        ├── Slide Content
        │
        └── Speaker Notes
```

---

# ✅ Quality Control

The content-generation layer contains dedicated components for:

* Quality scoring
* Validation
* Content selection
* Compression

This provides a quality-control stage before the generated content reaches the PowerPoint rendering layer.

```text
Generated Content
       │
       ▼
Quality Scoring
       │
       ▼
Validation
       │
       ▼
Content Selection
       │
       ▼
PPT Generation
```

---

# 🧠 Orchestration

The project contains a dedicated orchestration layer using a graph/state-based workflow.

```text
agents/
└── orchestrator/
    ├── graph.py
    └── state.py
```

The graph manages the execution flow while the state layer maintains information passed between stages of the generation process.

This keeps the orchestration logic separate from individual agents.

---

# 📊 PowerPoint Generator V2

The PowerPoint generation layer is separated from the AI generation pipeline.

```text
ppt_generator_v2/
│
├── components/
├── core/
├── layouts/
└── generator.py
```

The generator is responsible for converting structured presentation data into a PowerPoint file.

The separation provides a clean boundary:

```text
AI Pipeline
     │
     ▼
Structured Presentation Data
     │
     ▼
PPT Generator
     │
     ├── Layouts
     ├── Components
     └── Core Rendering
     │
     ▼
PowerPoint
```

This makes the rendering system independently extensible from the AI agents.

---

# 🌐 FastAPI Backend

The project exposes the generation pipeline through FastAPI.

The API layer initializes the planner, researcher, presentation planner, slide-content generation, and PPT generation components and provides a browser-facing interface for presentation generation.

### API Capabilities

* Start presentation generation
* Track generation progress
* Retrieve generation status
* Download generated presentations
* Perform health checks

The application also includes a browser-based interface for entering presentation parameters and monitoring generation progress.

---

# 📁 Project Structure

```text
Neurovia/
│
├── agents/
│   │
│   ├── content_gen/
│   │   ├── agent.py
│   │   ├── audience_adapter.py
│   │   ├── compressor.py
│   │   ├── image_planner.py
│   │   ├── quality_scorer.py
│   │   ├── selector.py
│   │   ├── speaker_notes.py
│   │   ├── synthesizer.py
│   │   ├── validator.py
│   │   └── visual_builder.py
│   │
│   ├── orchestrator/
│   │   ├── graph.py
│   │   └── state.py
│   │
│   ├── planner_agent/
│   │   ├── config/
│   │   ├── src/
│   │   ├── tests/
│   │   ├── main.py
│   │   └── test_groq.py
│   │
│   ├── ppt_generator_v2/
│   │   ├── components/
│   │   ├── core/
│   │   ├── layouts/
│   │   └── generator.py
│   │
│   ├── researcher_agent/
│   │   ├── services/
│   │   │   ├── duckduckgo_service.py
│   │   │   ├── llm_service.py
│   │   │   ├── serper_service.py
│   │   │   └── tavily_service.py
│   │   │
│   │   ├── utils/
│   │   │   └── storage.py
│   │   │
│   │   ├── config.py
│   │   ├── researcher.py
│   │   └── schemas.py
│   │
│   └── supervisor/
│       └── supervisor.py
│
├── api.py
├── main.py
├── testing.py
└── requirements.txt
```

The structure reflects the actual separation of planning, orchestration, research, content generation, supervision, and PPT rendering in the repository.

---

# ⚙️ Tech Stack

### Programming Language

* Python

### AI & LLM

* Large Language Models
* Groq
* Google Gemini
* LangGraph

### Agentic Architecture

* Supervisor Agent
* Planner Agent
* Researcher Agent
* Content Generation Agent
* Graph-based orchestration

### Web Research

* Tavily
* Serper
* DuckDuckGo Search

### Presentation Generation

* python-pptx
* Pillow

### Backend

* FastAPI
* Uvicorn
* Pydantic

The technologies listed above are based on the repository's current dependency configuration.

---

# 🔑 Environment Variables

Create a `.env` file in the project root.

```env
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key

TAVILY_API_KEY=your_tavily_api_key
SERPER_API_KEY=your_serper_api_key
```

The research configuration also supports environment-based settings for source limits, content length, LLM usage, provider selection, model name, and maximum LLM tokens.

Example optional configuration:

```env
MAX_SOURCES=5
MAX_CONTENT_LENGTH=500
USE_LLM=true
LLM_PROVIDER=groq
LLM_MAX_TOKENS=500
MODEL_NAME=llama-3.3-70b-versatile
```

Never commit API keys to the repository.

---

# 🚀 Installation

Clone the repository:

```bash
git clone https://github.com/snehachalla9/Neurovia.git
cd Neurovia
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the environment.

### Linux / macOS

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# ▶️ Run the Application

The main entry point is:

```bash
python main.py
```

The project also provides a FastAPI application:

```bash
uvicorn api:app --reload
```

Then open:

```text
http://127.0.0.1:8000
```

---

# 📌 Example

### Input

```text
Topic:
Large Language Models
```

The system can then process the topic through:

```text
Topic
  ↓
Supervisor
  ↓
Planner
  ↓
Curriculum / Module Planning
  ↓
Research Planning
  ↓
Web Research
  ↓
Research Synthesis
  ↓
Content Generation
  ↓
Audience Adaptation
  ↓
Visual Planning
  ↓
Quality Scoring
  ↓
Validation
  ↓
PPT Generation
  ↓
Final PowerPoint
```

---

# 📂 Output

The project uses an output directory for generated artifacts and intermediate presentation-generation results.

The API code initializes:

```text
output/latest/
```

as the latest-generation output location.

Generated artifacts can include structured intermediate data as well as the final PowerPoint presentation.

---

# 💡 Use Cases

* Academic presentation generation
* Technical presentations
* Research presentations
* Educational presentations
* University course material
* Business presentations
* Technology topic explanations
* Automated presentation generation

---

# 🔬 Engineering Highlights

### Modular Agent Design

Planning, research, content generation, supervision, and presentation rendering are implemented as separate modules.

### Multi-Provider Research

The research layer supports multiple search providers rather than depending on a single web-search service.

### Graph-Based Orchestration

The project uses a dedicated orchestration layer with graph and state components to manage the generation workflow.

### Content Quality Pipeline

Content passes through dedicated synthesis, compression, scoring, validation, selection, and audience-adaptation components.

### Rendering Separation

The PPT generation layer is separated from the AI agents, allowing presentation rendering and layout logic to evolve independently.

### API-Based Execution

The complete pipeline can be exposed through FastAPI rather than being limited to a local Python script.

---

# 🚀 Future Enhancements

* More advanced slide-layout selection
* Improved visual asset retrieval
* Automated diagram generation
* Source citations inside presentations
* Slide-level factual verification
* Automated presentation evaluation
* More LLM providers
* Persistent generation jobs
* Cloud deployment
* Frontend dashboard
* Interactive presentation editing

---

# 👩‍💻 Author

**Sneha Challa**

Electronics and Communication Engineering
Rajiv Gandhi University of Knowledge Technologies (RGUKT), Basar

GitHub: https://github.com/snehachalla9

---

# ⭐ Support

If you found this project useful, consider giving the repository a ⭐ on GitHub.
