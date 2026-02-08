"""
Data models for SubCtl
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any


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
