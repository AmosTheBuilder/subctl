#!/usr/bin/env python3
"""
SubCtl - Sub-Agent Management CLI (Simplified without etcd3)
Graduate-level orchestration for distributed AI systems
"""

import asyncio
import json
import sys
import time
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import redis
import psutil
import cryptography
import jwt as pyjwt

console = Console()

@dataclass
class AgentInfo:
    """Real-time agent information"""
    session_key: str
    label: str
    channel: str
    total_tokens: int
    status: str
    last_update: datetime
    assigned_tickets: List[str]
    package_compliance: float
    custom_code_ratio: float
    consensus_proof: Optional[str]

@dataclass
class AgentEvent:
    """Real-time agent event"""
    session_key: str
    event_type: str
    timestamp: datetime
    data: Dict[str, Any]
    cryptographic_hash: str

class SubCtlOrchestrator:
    """Simplified sub-agent orchestration without etcd3"""
    
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.agents: Dict[str, AgentInfo] = {}
        self.event_bus = redis.Redis(host='localhost', port=6379, decode_responses=True)
        
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
        except:
            pass
        
        # Fallback: return local cache
        return self.agents
    
    def get_agent_info(self, agent_label: str) -> Optional[AgentInfo]:
        """Get specific agent info"""
        all_agents = self.get_all_agents()
        return all_agents.get(agent_label)
    
    def record_agent_event(self, agent_label: str, event: AgentEvent):
        """Record agent event to Redis"""
        try:
            event_key = f"subctl:events:{agent_label}"
            self.redis_client.lpush(event_key, json.dumps(asdict(event)))
            self.redis_client.expire(event_key, 3600)  # Keep 1 hour
        except Exception as e:
            console.print(f"[red]Error recording event: {e}[/red]")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="SubCtl - Sub-Agent Management CLI (Simplified)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Agents commands
    agents_parser = subparsers.add_parser('agents', help='Agent management')
    agents_subparsers = agents_parser.add_subparsers(dest='agents_command')
    
    list_parser = agents_subparsers.add_parser('list', help='List all agents')
    list_parser.add_argument('--watch', action='store_true', help='Real-time monitoring')
    list_parser.add_argument('--refresh', type=int, default=5, help='Refresh interval (seconds)')
    
    inspect_parser = agents_subparsers.add_parser('inspect', help='Inspect specific agent')
    inspect_parser.add_argument('agent_label', help='Agent label to inspect')
    inspect_parser.add_argument('--logs', action='store_true', help='Show logs')
    inspect_parser.add_argument('--tools', action='store_true', help='Show tool calls')
    inspect_parser.add_argument('--tokens', action='store_true', help='Show token usage')
    inspect_parser.add_argument('--packages', action='store_true', help='Show package compliance')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
        
    orchestrator = SubCtlOrchestrator()
    
    if args.command == 'agents':
        if args.agents_command == 'list':
            if args.watch:
                console.print("[bold blue]Real-time Agent Monitoring[/bold blue]")
                
                try:
                    while True:
                        agents = orchestrator.get_all_agents()
                        table = generate_agents_table(agents)
                        console.print(table)
                        time.sleep(args.refresh)
                except KeyboardInterrupt:
                    console.print("\n[dim]Monitoring stopped[/dim]")
            else:
                console.print(generate_agents_table(orchestrator.get_all_agents()))
                
        elif args.agents_command == 'inspect':
            agent_info = orchestrator.get_agent_info(args.agent_label)
            if agent_info:
                console.print(f"[bold]Agent: {agent_info.label}[/bold]")
                console.print(f"Status: {agent_info.status}")
                console.print(f"Tokens: {agent_info.total_tokens:,}")
                console.print(f"Package Compliance: {agent_info.package_compliance:.1%}")
                console.print(f"Last Update: {agent_info.last_update.strftime('%Y-%m-%d %H:%M:%S')}")
                
                if args.logs:
                    console.print(f"\n[dim]--- Recent Activity (last 10 minutes) ---[/dim]")
                    # Could fetch logs from Redis here
                
                if args.tools:
                    console.print(f"\n[dim]--- Recent Tool Calls ---[/dim]")
                    # Could fetch tools from Redis here
                
                if args.tokens:
                    console.print(f"\n[dim]--- Token Usage ---[/dim]")
                    # Could fetch tokens from Redis here
                
                if args.packages:
                    console.print(f"\n[dim]--- Package Compliance ---[/dim]")
                    # Could fetch packages from Redis here
            else:
                console.print(f"[red]Agent {args.agent_label} not found[/red]")

def generate_agents_table(agents: Dict[str, AgentInfo]) -> Table:
    """Generate rich table of agent information"""
    table = Table(title="Sub-Agent Status")
    
    table.add_column("Agent", style="cyan", no_wrap=True)
    table.add_column("Status", style="magenta")
    table.add_column("Tokens", justify="right", style="green")
    table.add_column("Package Compliance", justify="right", style="yellow")
    table.add_column("Tickets", style="blue")
    table.add_column("Last Update", style="dim")
    
    for agent in agents.values():
        status_color = {
            "working": "green",
            "stalled": "red",
            "completed": "blue",
            "error": "red"
        }.get(agent.status, "white")
        
        compliance_text = f"{agent.package_compliance:.1%}"
        if agent.package_compliance < 0.8:
            compliance_text = f"[red]{compliance_text}[/red]"
        elif agent.package_compliance < 0.95:
            compliance_text = f"[yellow]{compliance_text}[/yellow]"
        
        table.add_row(
            agent.label,
            f"[{status_color}]{agent.status}[/{status_color}]",
            f"{agent.total_tokens:,}",
            compliance_text,
            ", ".join(agent.assigned_tickets[:3]),
            agent.last_update.strftime("%H:%M:%S")
        )
    
    return table

if __name__ == '__main__':
    main()