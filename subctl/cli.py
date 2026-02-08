"""
CLI interface for SubCtl
"""

import argparse
import time
from typing import Dict
from rich.console import Console
from rich.table import Table

from .orchestrator import SubCtlOrchestrator
from .models import AgentInfo

import datetime

console = Console()


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
    list_parser.add_argument('--stale', action='store_true', help='Include stale/historical data')

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
                        agents = orchestrator.get_active_agents()
                        if agents:
                            table = generate_agents_table(agents)
                            console.print(table)
                        else:
                            console.print("[yellow]No active agents found[/yellow]")
                            console.print("[dim]Use --stale to see historical data[/dim]")
                        time.sleep(args.refresh)
                except KeyboardInterrupt:
                    console.print("\n[dim]Monitoring stopped[/dim]")
            else:
                if args.stale:
                    # Show all data including stale
                    agents = orchestrator.get_all_agents()
                    if agents:
                        console.print(generate_agents_table(agents))
                    else:
                        console.print("[yellow]No agent data found in Redis[/yellow]")
                else:
                    # Show only active agents
                    agents = orchestrator.get_active_agents()
                    if agents:
                        console.print(generate_agents_table(agents))
                    else:
                        console.print("[yellow]No active agents found[/yellow]")
                        console.print("[dim]Use --stale to see historical data[/dim]")

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


if __name__ == '__main__':
    main()
