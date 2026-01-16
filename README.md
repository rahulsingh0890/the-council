# PM High Council

**Deploy the world's best operators on your hardest problems.**

PM High Council is a strategic advisory tool that synthesizes wisdom from elite product leaders. It analyzes your toughest decisions through four distinct perspectives, then delivers a clear verdict with two actionable paths forward.

---

## How It Works

1. **You brief the Council** on your situation—a product dilemma, team conflict, strategic decision, or growth challenge.

2. **Four expert perspectives analyze your problem:**
   - **The Visionary** (Founders) — Vision, intuition, culture, founder mode
   - **The Scaler** (Product Leaders) — Strategy, empowered teams, discovery
   - **The Scientist** (Growth Experts) — Loops, acquisition, pricing, retention
   - **The Architect** (Engineering Leaders) — Systems, trade-offs, feasibility

3. **The Verdict synthesizes everything** into two mutually exclusive paths:
   - **Path A: The Bold Move** — Higher risk, higher reward
   - **Path B: The Measured Move** — Structured, lower risk
   - **The Tie-Breaker** — A clear recommendation

---

## The Intelligence

The Council's wisdom is derived from the [Lenny's Podcast](https://www.lennysnewsletter.com/) archive—284 episodes of conversations with world-class operators including:

| Persona | Key Voices |
|---------|-----------|
| **Founders** | Brian Chesky, Tobi Lutke, Dylan Field, Stewart Butterfield, Ben Horowitz |
| **Product** | Marty Cagan, Shreyas Doshi, Julie Zhuo, Gibson Biddle, Lenny Rachitsky |
| **Growth** | Elena Verna, Brian Balfour, Casey Winters, Sean Ellis, Patrick Campbell |
| **Engineering** | Will Larson, Camille Fournier, David Singleton, Chip Huyen |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                       │
│                     localhost:3000                               │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                           │
│                     localhost:8000                               │
│                                                                  │
│  ┌──────────────┐    ┌───────────────────────────────────────────────┐   │
│  │  Supervisor  │───▶│            Four Parallel Swarms               │   │
│  │    (GPT-4o)  │    │                                               │   │
│  └──────────────┘    │  ┌─────────┐ ┌───────┐ ┌─────────┐ ┌────────┐ │   │
│                      │  │Visionary│ │ Scaler│ │Scientist│ │Architect│ │   │
│                      │  └────┬────┘ └───┬───┘ └────┬────┘ └───┬────┘ │   │
│                      │       │          │          │          │      │   │
│                      │  ┌────┴──────────┴──────────┴──────────┴────┐ │   │
│                      │  │               ChromaDB                   │ │   │
│                      │  │          (Vector Store + RAG)            │ │   │
│                      │  └──────────────────────────────────────────┘ │   │
│                      └───────────────────────────────────────────────┘   │
│                                     │                            │
│                                     ▼                            │
│                      ┌──────────────────────────────────────┐   │
│                      │     Synthesizer (Executive Coach)    │   │
│                      │         → THE VERDICT                │   │
│                      └──────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

**Key Components:**

- **Supervisor** — Routes your problem to each swarm with tailored queries
- **Swarm Agents** — RAG-powered agents that retrieve relevant wisdom from ChromaDB
- **ChromaDB** — Vector database storing chunked podcast transcripts with speaker/persona metadata
- **Synthesizer** — Analyzes tensions between perspectives and produces the Strategic Fork

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14, React, TypeScript, Tailwind CSS |
| Backend | FastAPI, LangChain, LangGraph |
| LLM | GPT-4o (OpenAI) |
| Embeddings | text-embedding-3-small (OpenAI) |
| Vector Store | ChromaDB |
| Data | Lenny's Podcast transcripts (Markdown + YAML frontmatter) |

---

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.9+
- OpenAI API key

### 1. Clone the repository

```bash
git clone https://github.com/your-repo/pm-high-council.git
cd pm-high-council
```

### 2. Set up the backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. Ingest the transcript data

```bash
# From the backend directory
python ingest_data.py
```

This will:
- Parse all podcast transcripts from `/episodes`
- Chunk them by speaker segments
- Generate embeddings
- Store in ChromaDB with persona metadata

### 4. Start the backend

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 5. Set up the frontend

```bash
cd ../frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 6. Open the app

Navigate to [http://localhost:3000](http://localhost:3000)

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API info |
| `GET` | `/api/health` | Health check with swarm status |
| `GET` | `/api/swarms` | List all available swarms |
| `POST` | `/api/council` | Submit a problem, get full council response |
| `POST` | `/api/council/stream` | Submit a problem, stream responses via SSE |

### Example Request

```bash
curl -X POST http://localhost:8000/api/council \
  -H "Content-Type: application/json" \
  -d '{"problem": "My PM is blocking every initiative. I have exec support but do not want to burn bridges."}'
```

---

## Project Structure

```
pm-high-council/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── config.py            # Prompts and swarm configurations
│   ├── agent_graph.py       # LangGraph orchestration
│   ├── persona_mapping.py   # Speaker → Swarm mapping
│   ├── ingest_data.py       # Data ingestion script
│   └── agents/
│       └── base_agent.py    # RAG agent factory
├── frontend/
│   ├── app/
│   │   ├── page.tsx         # Main page
│   │   ├── layout.tsx       # App layout
│   │   └── globals.css      # Premium styling
│   ├── components/
│   │   ├── problem-input.tsx
│   │   ├── agent-card.tsx
│   │   └── synthesis-block.tsx
│   └── lib/
│       └── api.ts           # API client
├── episodes/                 # Podcast transcripts
└── chroma_db/               # Vector database (generated)
```

---

## The Synthesizer Philosophy

The Verdict is designed to be a **Wartime Consigliere**, not a corporate consultant.

**What it avoids:**
- Generic advice ("implement a framework")
- Numbered lists of 5 steps
- False consensus that tries to please everyone
- Hedging without making a call

**What it delivers:**
- The core tension that cannot be optimized away
- Two mutually exclusive paths with tactical execution steps
- A clear recommendation with acknowledged trade-offs
- The one question to validate the choice

---

## Adding New Speakers

1. Add the speaker to the appropriate swarm in `backend/persona_mapping.py`:

```python
PERSONA_MAP = {
    "founder_swarm": [
        "brian-chesky",
        "your-new-founder",  # Add here
        ...
    ],
    ...
}
```

2. Add their transcript to `/episodes/speaker-name-##/transcript.md`

3. Re-run ingestion:

```bash
cd backend
python ingest_data.py
```

---

## License

MIT

---

## Credits

- Intelligence derived from [Lenny's Newsletter](https://www.lennysnewsletter.com/) and Lenny's Podcast
- Built with love for product people making hard decisions

---

*"The best product decisions aren't about finding the right answer. They're about understanding the trade-offs well enough to make a choice you can defend."*
