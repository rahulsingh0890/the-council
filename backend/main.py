"""
FastAPI backend for PM High Council's Quad-Swarm Engine.
"""

import json
from contextlib import asynccontextmanager
from typing import Optional, List, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from agent_graph import invoke_council, stream_council
from config import SWARMS


class ProblemRequest(BaseModel):
    """Request body for council invocation."""
    problem: str


class SwarmResponse(BaseModel):
    """Response from a single swarm."""
    response: str
    sources: List[Dict]
    agent: str


class CouncilResponse(BaseModel):
    """Full response from the Quad-Swarm council."""
    problem: str
    founder_swarm: Optional[SwarmResponse] = None
    product_swarm: Optional[SwarmResponse] = None
    growth_swarm: Optional[SwarmResponse] = None
    engineering_swarm: Optional[SwarmResponse] = None
    synthesis: Optional[str] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    print("PM High Council Quad-Swarm Engine starting...")
    yield
    print("PM High Council Quad-Swarm Engine shutting down...")


app = FastAPI(
    title="PM High Council API",
    description="Quad-Swarm advisory system powered by collective product leadership wisdom",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "PM High Council Quad-Swarm Engine",
        "version": "2.0.0",
        "swarms": [
            {"name": "founder_swarm", "display_name": "The Visionary", "focus": SWARMS["founder_swarm"]["focus"]},
            {"name": "product_swarm", "display_name": "The Scaler", "focus": SWARMS["product_swarm"]["focus"]},
            {"name": "growth_swarm", "display_name": "The Scientist", "focus": SWARMS["growth_swarm"]["focus"]},
            {"name": "engineering_swarm", "display_name": "The Architect", "focus": SWARMS["engineering_swarm"]["focus"]}
        ]
    }


@app.post("/api/council", response_model=CouncilResponse)
async def convene_council(request: ProblemRequest):
    """
    Convene the PM High Council Quad-Swarm to discuss a product problem.

    Returns all swarm responses and synthesis in a single response.
    """
    if not request.problem.strip():
        raise HTTPException(status_code=400, detail="Problem statement cannot be empty")

    try:
        result = invoke_council(request.problem)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/council/stream")
async def stream_council_response(request: ProblemRequest):
    """
    Stream the PM High Council Quad-Swarm discussion as Server-Sent Events.

    Events:
    - swarm_start: {"swarm": "founder_swarm|product_swarm|growth_swarm|engineering_swarm", "display_name": "..."}
    - swarm_complete: {"swarm": "...", "display_name": "...", "response": {...}}
    - synthesis_complete: {"synthesis": "..."}
    - done: {}
    """
    if not request.problem.strip():
        raise HTTPException(status_code=400, detail="Problem statement cannot be empty")

    async def event_generator():
        try:
            async for event in stream_council(request.problem):
                yield {
                    "event": event["event"],
                    "data": json.dumps(event["data"])
                }
        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)})
            }

    return EventSourceResponse(event_generator())


@app.get("/api/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "components": {
            "api": "up",
            "swarms": {
                "founder_swarm": {"status": "ready", "display_name": "The Visionary"},
                "product_swarm": {"status": "ready", "display_name": "The Scaler"},
                "growth_swarm": {"status": "ready", "display_name": "The Scientist"},
                "engineering_swarm": {"status": "ready", "display_name": "The Architect"}
            }
        }
    }


@app.get("/api/swarms")
async def list_swarms():
    """List all available swarms and their configurations."""
    return {
        "swarms": [
            {
                "name": swarm_name,
                "display_name": config["display_name"],
                "focus": config["focus"],
                "color": config["color"]
            }
            for swarm_name, config in SWARMS.items()
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
