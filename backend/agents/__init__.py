"""
PM High Council Swarm Agents.

This module provides the base swarm agent factory for the Quad-Swarm Engine.
Individual persona agents (chesky, cagan, verna) have been replaced by
collective swarm agents (founder_swarm, product_swarm, growth_swarm, engineering_swarm).
"""

from .base_agent import create_swarm_agent, create_rag_agent

__all__ = ["create_swarm_agent", "create_rag_agent"]
