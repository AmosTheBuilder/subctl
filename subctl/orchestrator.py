"""
Orchestrator for managing sub-agents
"""

import json
from datetime import datetime
from typing import Dict, Optional
import redis
from rich.console import Console

from .models import AgentInfo, AgentEvent

console = Console()


class SubCtlOrchestrator:
    """Simplified sub-agent orchestration without etcd3"""

    def __init__(self, redis_host='localhost', redis_port=6379):
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=True
        )
        self.event_bus = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=True
        )

    def get_all_agents(self) -> Dict[str, AgentInfo]:
        """Get all known agents"""
        # Try to read from Redis first
        try:
            agent_data = self.redis_client.get("subctl:agents")
            if agent_data:
                raw_data = json.loads(agent_data)
                # Convert dicts back to AgentInfo objects
                result = {}
                for key, value in raw_data.items():
                    if isinstance(value, dict):
                        # Handle datetime string conversion
                        if 'last_update' in value and isinstance(value['last_update'], str):
                            value['last_update'] = datetime.fromisoformat(value['last_update'])
                        result[key] = AgentInfo(**value)
                    else:
                        result[key] = value
                return result
        except Exception as e:
            console.print(f"[red]Error reading from Redis: {e}[/red]")

        # Fallback: return empty dict
        return {}
    
    def get_active_agents(self, max_age_minutes: int = 10) -> Dict[str, AgentInfo]:
        """Get only agents that have updated within the specified time window"""
        all_agents = self.get_all_agents()
        now = datetime.now()
        active_agents = {}
        
        for label, agent in all_agents.items():
            if isinstance(agent, AgentInfo):
                age_minutes = (now - agent.last_update).total_seconds() / 60
                if age_minutes <= max_age_minutes:
                    active_agents[label] = agent
                    
        return active_agents

    def get_agent_info(self, agent_label: str) -> Optional[AgentInfo]:
        """Get specific agent info"""
        all_agents = self.get_all_agents()
        return all_agents.get(agent_label)

    def record_agent_event(self, agent_label: str, event: AgentEvent):
        """Record agent event to Redis"""
        try:
            event_key = f"subctl:events:{agent_label}"
            self.redis_client.lpush(
                event_key,
                json.dumps(asdict(event))
            )
            self.redis_client.expire(event_key, 3600)  # Keep 1 hour
        except Exception as e:
            console.print(f"[red]Error recording event: {e}[/red]")
