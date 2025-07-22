# AI Multi-Agent Team System

A flexible system for creating AI agents that interact with each other using different architectural patterns. Each team member has their own personality and capabilities, and you can easily switch between different interaction architectures.

## 🏗️ Available Architectures

### 1. **Sequential Pipeline** (Default)
- **Flow**: Product Owner → Tech Lead → Developer → QA → Manager
- **Best for**: Structured workflows with clear handoffs
- **Use case**: Traditional project planning and execution

### 2. **Round-Table Discussion**
- **Flow**: All agents participate in multiple discussion rounds
- **Best for**: Collaborative decision-making and brainstorming
- **Use case**: Complex problem-solving requiring consensus

### 3. **Event-Driven Reactive**
- **Flow**: Agents react to events and trigger other agents dynamically
- **Best for**: Dynamic workflows and real-time collaboration
- **Use case**: Agile development with changing requirements

### 4. **Hierarchical Decision Tree** (Coming Soon)
- **Flow**: Bottom-up analysis, top-down decision approval
- **Best for**: Complex decisions with clear authority levels
- **Use case**: Enterprise-level project governance

## 📁 Project Structure

```
AiTeam/
├── README.md
├── requirements.txt
├── config/                    # Configuration files
│   ├── ai_config.json
│   ├── ai_dev_team_config.json
│   └── tasks.json
├── src/                       # Source code
│   ├── core/                  # Core modules
│   │   ├── agent_architecture_manager.py
│   │   ├── ai_providers.py
│   │   └── task_router.py
│   ├── architectures/         # Agent architectures
│   │   ├── event_driven_reactive.py
│   │   ├── hierarchical_decision_tree.py
│   │   ├── round_table_discussion.py
│   │   └── sequential_pipeline.py
│   └── api/                   # API endpoints
│       ├── multi_agent_api.py
│       └── task_router_api.py
├── frontend/                  # Web interface
│   ├── index.html
│   ├── script.js
│   ├── styles.css
│   └── data/                  # Frontend data files
│       ├── ai_dev_team_config.json
│       └── backlog.json
├── scripts/                   # Utility scripts
│   ├── demo_multi_agent_system.py
│   ├── setup_ai_providers.py
│   └── show_detailed_responses.py
└── tests/                     # Test files
    ├── test_ai_integration.py
    ├── test_architectures.py
    ├── test_improved_fallbacks.py
    └── test_openai_integration.py
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the APIs
```bash
# Start Multi-Agent API (port 5001)
cd src/api && python3 multi_agent_api.py

# Start Task Router API (port 5002)
cd src/api && python3 task_router_api.py
```

### 3. Start the Frontend
```bash
cd frontend && python3 -m http.server 8080
```
Then open `http://localhost:8080` in your browser

### 4. Try the Demo
```bash
python3 scripts/demo_multi_agent_system.py
```

## 🎮 How to Use

### Web Interface
1. **Enable Multi-Agent Processing**: Check the toggle in the web interface
2. **Select Architecture**: Choose from the dropdown (Sequential, Round-Table, Reactive)
3. **Process Tasks**: Click "Run" on any story to process it with multiple agents
4. **View Results**: See detailed responses from all agents in the modal

### API Endpoints

#### Get Available Architectures
```bash
GET http://localhost:5001/architectures
```

#### Set Architecture
```bash
POST http://localhost:5001/set_architecture
Content-Type: application/json

{
  "architecture": "sequential"
}
```

#### Process Task with Agents
```bash
POST http://localhost:5001/process_with_agents
Content-Type: application/json

{
  "task_id": "STORY-123",
  "title": "User Authentication",
  "description": "Implement secure login system",
  "priority": "high"
}
```

#### Get Performance Comparison
```bash
GET http://localhost:5001/performance_comparison
```

## 👥 Team Members

The system includes 6 AI team members, each with unique personalities and capabilities:

- **Project Manager**: Schedule-driven, focuses on timelines and coordination
- **Product Owner**: Detail-oriented, translates business goals into features
- **Tech Lead**: Systems thinker, balances pragmatism with code quality
- **QA Engineer**: Meticulous, cares about stability and edge cases
- **Frontend Developer**: Creative, user-focused, builds responsive interfaces
- **Backend Developer**: Reliable, builds scalable services and APIs

## 🔧 Architecture Details

### Sequential Pipeline
```python
from agent_architecture_manager import AgentArchitectureManager

manager = AgentArchitectureManager()
manager.set_architecture("sequential")

task = {
    "task_id": "DEMO-001",
    "title": "Payment System",
    "description": "Implement Stripe integration",
    "priority": "high"
}

result = await manager.process_task(task)
```

### Round-Table Discussion
```python
manager.set_architecture("round_table")
result = await manager.process_task(task)

# Access discussion rounds
for round_data in result.results:
    print(f"Round {round_data.round_number}: {round_data.topic}")
    print(f"Consensus: {round_data.consensus_items}")
```

### Event-Driven Reactive
```python
manager.set_architecture("reactive")
result = await manager.process_task(task)

# Access events
for event in result.results:
    print(f"Event: {event.event_type.value} from {event.source_agent}")
```

## 📊 Features

### ✅ Easy Architecture Switching
- Switch between architectures with a single function call
- Web interface with dropdown selection
- API endpoint for programmatic switching

### ✅ Comprehensive Results
- Detailed responses from each agent
- Processing time and metadata
- Architecture-specific result formats

### ✅ Export Functionality
- JSON export for programmatic use
- Markdown export for documentation
- Performance comparison reports

### ✅ Real-time Processing
- Async processing for better performance
- Event-driven updates (in reactive mode)
- Processing history tracking

## 🔄 Integration with Existing System

The multi-agent system integrates seamlessly with your existing task router:

```python
# Enhanced route_task endpoint
@app.route('/route_task', methods=['POST'])
def route_task_enhanced():
    task_data = request.json
    use_multi_agent = task_data.get("use_multi_agent", False)
    
    if use_multi_agent:
        return process_with_agents()  # Multi-agent processing
    else:
        return route_task_endpoint()  # Original single-agent routing
```

## 📈 Performance Monitoring

Track performance across different architectures:

```python
manager = AgentArchitectureManager()

# Process tasks with different architectures
for arch in ["sequential", "round_table", "reactive"]:
    manager.set_architecture(arch)
    result = await manager.process_task(task)

# Compare performance
performance = manager.compare_architectures_performance()
for arch, metrics in performance.items():
    print(f"{arch}: {metrics['avg_time']:.2f}s average")
```

## 🛠️ Customization

### Adding New Team Members
Edit `ai_dev_team_config.json`:

```json
{
  "members": [
    {
      "id": "new_member",
      "role": "DevOps Engineer",
      "description": "Manages infrastructure and deployments",
      "capabilities": ["CI/CD", "Docker", "Kubernetes"],
      "personality_prompt": "You are a reliability-focused DevOps engineer..."
    }
  ]
}
```

### Creating New Architectures
1. Create a new architecture file in `agent_architectures/`
2. Implement the required interface
3. Add it to `AgentArchitectureManager`
4. Update the web interface

## 🐛 Troubleshooting

### API Connection Issues
- Ensure the multi-agent API is running on port 5001
- Check CORS settings if accessing from different domains
- Verify Flask and flask-cors are installed

### Architecture Not Working
- Check that the architecture is properly implemented
- Verify team configuration is loaded correctly
- Look at console logs for detailed error messages

### Performance Issues
- Use async processing for better performance
- Consider caching team configurations
- Monitor memory usage with large result sets

## 🚀 Next Steps

1. **Implement Real AI Integration**: Replace mock responses with actual AI API calls
2. **Add WebSocket Support**: Real-time updates for reactive architecture
3. **Persistent Storage**: Save processing history to database
4. **Advanced Analytics**: Detailed performance and quality metrics
5. **Custom Workflows**: User-defined agent interaction patterns

## 📝 License

This project is part of the AI Dev Team system. See the main project for licensing information.

---

**Ready to get started?** Run `python demo_multi_agent_system.py` to see all architectures in action!
