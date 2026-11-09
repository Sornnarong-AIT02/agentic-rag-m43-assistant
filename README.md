# M43 Video Assistant & Agentic RAG

Production-grade Agentic RAG assistant and multi-tool system designed for Micro Four Thirds (M43) video cameras. The application leverages a FastAPI backend, an autonomous Agentic Loop (`Observe-Think-Act`), custom documentation tools with metadata pre-filtering, video-math calculators, and Server-Sent Events (SSE) streaming[cite: 8, 10, 14].

---

## Key Architecture & Features

- **Agentic Loop (`Observe-Think-Act`):** Built with a robust control flow, enforcing deterministic execution (`temperature=0`) and strict safety guardrails (`max_steps` capping, repeated-call detection, and argument validation)[cite: 8, 10].
- **Metadata Pre-filtering & Citation:** Solves the semantic search limitation on hard constraints by filtering document corpuses based on specific metadata attributes (e.g., camera models like `GM1`, `GH5`, `OM-1`) prior to similarity ranking, ensuring precise source citations (`[source]`)[cite: 8, 10, 20].
- **Custom Tools:**
  - `search_m43_docs`: Retrieves camera manuals, lens specifications, exposure parameters, and cinematic styling guides (e.g., Wong Kar-wai aesthetic) with strict metadata scoping[cite: 8, 10, 16].
  - `calculate_video_settings`: Performs exact domain-specific computations, including the 180-degree shutter rule (`shutter_angle`) and M43 2x crop factor equivalency (`crop_factor`)[cite: 8, 11].
- **Backend & Streaming (FastAPI & SSE):** Structured cleanly following the `router -> service` architectural pattern. Implements asynchronous Server-Sent Events (SSE) via `text/event-stream` and `asyncio.to_thread` to prevent event-loop blocking and lower perceived latency[cite: 10, 14, 15].
- **Quantitative Evaluation Harness:** Includes an evaluation script (`eval/run_eval.py`) and a labeled test dataset (`eval/eval_set.json`) to compute Recall@1 and tool routing accuracy[cite: 8, 21].

---

## Project Structure

```text
├── app/
│   ├── main.py            # FastAPI entrypoint, health checks, REST routes, and SSE streaming
│   ├── schemas.py         # Pydantic models for request/response validation
│   ├── static/
│   │   └── index.html     # Interactive Chat Web UI (Vanilla JS & SSE buffer parser)
│   └── services/
│       ├── agent.py       # Agentic loop logic, LLM tool dispatch, and guardrails
│       └── tools.py       # Custom tool implementations (Metadata pre-filtering & video math)
├── data/
│   └── m43_manuals.json   # Unified data corpus containing camera specs, lenses, and guides
├── eval/
│   ├── eval_set.json      # Benchmark test cases for quantitative evaluation
│   └── run_eval.py        # Evaluation harness script measuring Recall@1 and routing accuracy
├── .env.example           # Template for environment variables
├── pyproject.toml         # Project dependencies and tool configurations
└── README.md              # Project documentation

Getting Started & Installation
1. Prerequisites
Ensure you have Python installed along with the uv package manager.

2. Configure Environment Variables
Clone the repository and create a .env file in the root directory based on .env.example:

OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=[https://llm.nat-d.uk/v1](https://llm.nat-d.uk/v1)

3. Run the Backend Server
Launch the FastAPI server using uv:

Bash
uv run uvicorn app.main:app --reload

Access the interactive Chat Web UI at: http://127.0.0.1:8000/

Explore the API documentation via Swagger UI at: http://127.0.0.1:8000/docs

Quantitative Evaluation
To run the evaluation benchmark and verify retrieval recall improvement and tool routing accuracy:

Bash
uv run python eval/run_eval.py