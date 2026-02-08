# SubCtl - Sub-Agent Management CLI

Graduate-level orchestration for distributed AI systems.

## Features

- **Real-time Agent Monitoring**: List and inspect sub-agents with live status updates
- **Token Usage Tracking**: Monitor token consumption across all agents
- **Package Compliance**: Track agent adherence to package-based workflows
- **Ticket Assignment**: Manage work distribution among agents
- **Redis-Backed State**: Persistent, distributed state storage
- **Rich Terminal UI**: Beautiful, colorized output with Rich library

## Installation

### From GitHub Release (Recommended)

```bash
pip install https://github.com/AmosTheBuilder/subctl/archive/v0.1.0.tar.gz
```

### From Source

```bash
git clone https://github.com/AmosTheBuilder/subctl.git
cd subctl
pip install -e .
```

### Dependencies

- Python 3.8+
- Redis server
- See `requirements.txt` for full list

```bash
pip install -r requirements.txt
```

## Usage

### List Active Agents (Default)
Shows only agents that have updated within the last 10 minutes:

```bash
subctl agents list
```

### List All Agents (Including Historical)
Shows all agent data including stale/historical entries:

```bash
subctl agents list --stale
```

### Real-Time Monitoring
Monitors only active agents in real-time:

```bash
subctl agents list --watch
```

### Inspect Specific Agent

```bash
subctl agents inspect <agent_label>
```

### Inspect with Details

```bash
subctl agents inspect <agent_label> --logs --tools --tokens --packages
```

## Architecture

SubCtl uses a simplified architecture without etcd3:

- **Redis**: State storage and event bus
- **Rich**: Terminal UI and formatting
- **psutil**: System monitoring
- **cryptography & JWT**: Event integrity verification

## Development

### Project Structure

```
subctl/
├── subctl/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py          # CLI commands and argument parsing
│   ├── orchestrator.py  # Core orchestration logic
│   └── models.py       # Data models (AgentInfo, AgentEvent)
├── requirements.txt
├── setup.py
└── README.md
```

### Running from Source

```bash
python -m subctl agents list
```

## Configuration

SubCtl connects to Redis at `localhost:6379` by default. To change this, modify the connection in `orchestrator.py`:

```python
self.redis_client = redis.Redis(host='your-host', port=6379, decode_responses=True)
```

## Roadmap

- [ ] Redis-based locking system
- [ ] Agent crash recovery
- [ ] Health check loop
- [ ] Automatic reassignment of orphaned tickets
- [ ] etcd3 integration for multi-host deployments
- [ ] Leader election for distributed orchestrators

## Contributing

Contributions welcome! Please submit pull requests or open issues.

## License

MIT License - see LICENSE file for details
