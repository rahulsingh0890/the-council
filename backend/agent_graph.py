"""
LangGraph-based multi-agent orchestration for PM High Council's Quad-Swarm Engine.
"""

import json
from typing import TypedDict, Optional

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END

from config import (
    SUPERVISOR_PROMPT,
    SYNTHESIZER_PROMPT,
    LLM_MODEL,
    OPENAI_API_KEY,
    SWARMS,
)
from agents.base_agent import create_swarm_agent


# State schema for the Quad-Swarm graph
class CouncilState(TypedDict):
    """State that flows through the PM High Council Quad-Swarm graph."""
    problem: str
    # Swarm queries
    founder_swarm_query: Optional[str]
    product_swarm_query: Optional[str]
    growth_swarm_query: Optional[str]
    engineering_swarm_query: Optional[str]
    # Swarm responses
    founder_swarm_response: Optional[dict]
    product_swarm_response: Optional[dict]
    growth_swarm_response: Optional[dict]
    engineering_swarm_response: Optional[dict]
    # Final synthesis
    synthesis: Optional[str]


# List of swarm names for iteration
SWARM_NAMES = ["founder_swarm", "product_swarm", "growth_swarm", "engineering_swarm"]


# Initialize LLM for supervisor and synthesizer
llm = ChatOpenAI(
    model=LLM_MODEL,
    openai_api_key=OPENAI_API_KEY,
    temperature=0.7
)


def supervisor_node(state: CouncilState) -> dict:
    """
    Supervisor node that analyzes the problem and creates focused queries for each swarm.
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", SUPERVISOR_PROMPT),
        ("human", "Product Problem: {problem}")
    ])

    chain = prompt | llm | StrOutputParser()

    response = chain.invoke({"problem": state["problem"]})

    # Parse JSON response
    try:
        queries = json.loads(response)
    except json.JSONDecodeError:
        # Fallback: use the problem directly with swarm-specific framing
        queries = {
            "founder_swarm_query": f"From a founder's perspective on vision and culture, how would you approach: {state['problem']}",
            "product_swarm_query": f"What product strategy and discovery process would you recommend for: {state['problem']}",
            "growth_swarm_query": f"What growth systems, metrics and loops should we focus on for: {state['problem']}",
            "engineering_swarm_query": f"What are the technical considerations and feasibility concerns for: {state['problem']}"
        }

    return {
        "founder_swarm_query": queries.get("founder_swarm_query", ""),
        "product_swarm_query": queries.get("product_swarm_query", ""),
        "growth_swarm_query": queries.get("growth_swarm_query", ""),
        "engineering_swarm_query": queries.get("engineering_swarm_query", "")
    }


def create_swarm_node(swarm_name: str):
    """Factory function to create swarm nodes."""
    config = SWARMS[swarm_name]

    # Create the swarm agent
    agent = create_swarm_agent(
        persona_type=swarm_name,
        system_prompt=config["system_prompt"],
        display_name=config["display_name"]
    )

    def node(state: CouncilState) -> dict:
        query_key = f"{swarm_name}_query"
        response_key = f"{swarm_name}_response"

        query = state.get(query_key, state["problem"])
        result = agent(query)

        return {response_key: result}

    return node


def synthesizer_node(state: CouncilState) -> dict:
    """
    Synthesizer node that combines all swarm responses into actionable guidance.
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a strategic advisor synthesizing multiple perspectives from expert collectives."),
        ("human", SYNTHESIZER_PROMPT)
    ])

    chain = prompt | llm | StrOutputParser()

    response = chain.invoke({
        "founder_swarm_response": state["founder_swarm_response"]["response"] if state.get("founder_swarm_response") else "No response from The Visionary",
        "product_swarm_response": state["product_swarm_response"]["response"] if state.get("product_swarm_response") else "No response from The Scaler",
        "growth_swarm_response": state["growth_swarm_response"]["response"] if state.get("growth_swarm_response") else "No response from The Scientist",
        "engineering_swarm_response": state["engineering_swarm_response"]["response"] if state.get("engineering_swarm_response") else "No response from The Architect"
    })

    return {"synthesis": response}


def build_council_graph() -> StateGraph:
    """Build and compile the PM High Council Quad-Swarm graph."""

    # Create the graph
    graph = StateGraph(CouncilState)

    # Add nodes
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("founder_swarm", create_swarm_node("founder_swarm"))
    graph.add_node("product_swarm", create_swarm_node("product_swarm"))
    graph.add_node("growth_swarm", create_swarm_node("growth_swarm"))
    graph.add_node("engineering_swarm", create_swarm_node("engineering_swarm"))
    graph.add_node("synthesizer", synthesizer_node)

    # Set entry point
    graph.set_entry_point("supervisor")

    # Add edges: supervisor -> all swarms in parallel
    for swarm_name in SWARM_NAMES:
        graph.add_edge("supervisor", swarm_name)

    # All swarms -> synthesizer
    for swarm_name in SWARM_NAMES:
        graph.add_edge(swarm_name, "synthesizer")

    # Synthesizer -> END
    graph.add_edge("synthesizer", END)

    return graph.compile()


# Compile the graph for use
council_graph = build_council_graph()


def invoke_council(problem: str) -> dict:
    """
    Convenience function to invoke the council with a problem statement.

    Args:
        problem: The product problem to discuss

    Returns:
        Dict with swarm responses and synthesis
    """
    result = council_graph.invoke({"problem": problem})

    return {
        "problem": result["problem"],
        "founder_swarm": result.get("founder_swarm_response"),
        "product_swarm": result.get("product_swarm_response"),
        "growth_swarm": result.get("growth_swarm_response"),
        "engineering_swarm": result.get("engineering_swarm_response"),
        "synthesis": result.get("synthesis")
    }


async def stream_council(problem: str):
    """
    Async generator that yields events as the council processes the problem.

    Yields SSE-formatted events for streaming to frontend.
    """
    config = {"recursion_limit": 50}

    async for event in council_graph.astream_events(
        {"problem": problem},
        config=config,
        version="v2"
    ):
        kind = event.get("event")
        name = event.get("name", "")

        # Handle swarm start events
        if kind == "on_chain_start" and name in SWARM_NAMES:
            yield {
                "event": "swarm_start",
                "data": {
                    "swarm": name,
                    "display_name": SWARMS[name]["display_name"]
                }
            }

        # Handle swarm completion events
        elif kind == "on_chain_end":
            if name in SWARM_NAMES:
                response_key = f"{name}_response"
                yield {
                    "event": "swarm_complete",
                    "data": {
                        "swarm": name,
                        "display_name": SWARMS[name]["display_name"],
                        "response": event["data"]["output"].get(response_key, {})
                    }
                }
            elif name == "synthesizer":
                yield {
                    "event": "synthesis_complete",
                    "data": {
                        "synthesis": event["data"]["output"].get("synthesis", "")
                    }
                }

    yield {"event": "done", "data": {}}


if __name__ == "__main__":
    # Test the graph
    result = invoke_council("High churn during user onboarding")
    print(json.dumps(result, indent=2, default=str))
