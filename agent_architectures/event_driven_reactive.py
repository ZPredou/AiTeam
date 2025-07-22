#!/usr/bin/env python3
"""
Event-Driven Reactive Architecture for AI Agent Interactions

Agents react to events and trigger other agents based on conditions.
Great for dynamic workflows and real-time collaboration.
"""

import json
import asyncio
from typing import Dict, List, Any, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import uuid

class EventType(Enum):
    TASK_CREATED = "task_created"
    ANALYSIS_COMPLETE = "analysis_complete"
    CONCERN_RAISED = "concern_raised"
    APPROVAL_NEEDED = "approval_needed"
    IMPLEMENTATION_READY = "implementation_ready"
    TESTING_REQUIRED = "testing_required"
    REVIEW_REQUESTED = "review_requested"

@dataclass
class Event:
    id: str
    event_type: EventType
    source_agent: str
    timestamp: datetime
    data: Dict[str, Any]
    target_agents: List[str] = None  # None means broadcast to all

@dataclass
class AgentReaction:
    agent_id: str
    reaction_type: str
    response: str
    triggered_events: List[Event]

class EventBus:
    def __init__(self):
        self.subscribers: Dict[EventType, List[Callable]] = {}
        self.event_history: List[Event] = []
    
    def subscribe(self, event_type: EventType, handler: Callable):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
    
    async def publish(self, event: Event):
        self.event_history.append(event)
        print(f"📡 Event: {event.event_type.value} from {event.source_agent}")
        
        if event.event_type in self.subscribers:
            for handler in self.subscribers[event.event_type]:
                await handler(event)

class ReactiveAgent:
    def __init__(self, agent_config: Dict, event_bus: EventBus):
        self.config = agent_config
        self.event_bus = event_bus
        self.state = "idle"
        self.current_tasks = []
        
        # Subscribe to relevant events
        self._setup_event_subscriptions()
    
    def _setup_event_subscriptions(self):
        """Setup event subscriptions based on agent role"""
        role_subscriptions = {
            "manager": [EventType.CONCERN_RAISED, EventType.APPROVAL_NEEDED],
            "product_owner": [EventType.TASK_CREATED, EventType.REVIEW_REQUESTED],
            "tech_lead": [EventType.TASK_CREATED, EventType.CONCERN_RAISED, EventType.REVIEW_REQUESTED],
            "qa_engineer": [EventType.IMPLEMENTATION_READY, EventType.TESTING_REQUIRED],
            "developer_1": [EventType.IMPLEMENTATION_READY, EventType.REVIEW_REQUESTED],
            "developer_2": [EventType.IMPLEMENTATION_READY, EventType.REVIEW_REQUESTED]
        }
        
        subscriptions = role_subscriptions.get(self.config["id"], [EventType.TASK_CREATED])
        
        for event_type in subscriptions:
            self.event_bus.subscribe(event_type, self.handle_event)
    
    async def handle_event(self, event: Event):
        """Handle incoming events and react accordingly"""
        
        # Skip if event is targeted to specific agents and we're not included
        if event.target_agents and self.config["id"] not in event.target_agents:
            return
        
        # Skip our own events
        if event.source_agent == self.config["id"]:
            return
        
        print(f"  🎯 {self.config['role']} reacting to {event.event_type.value}")
        
        reaction = await self._generate_reaction(event)
        
        # Trigger new events based on reaction
        for new_event in reaction.triggered_events:
            await self.event_bus.publish(new_event)
    
    async def _generate_reaction(self, event: Event) -> AgentReaction:
        """Generate reaction to an event"""
        
        # Create context-aware prompt
        prompt = self._create_reaction_prompt(event)
        
        # Simulate AI response (replace with actual AI API)
        response_data = await self._call_ai_for_reaction(prompt)
        
        # Determine what events to trigger based on response
        triggered_events = self._determine_triggered_events(event, response_data)
        
        return AgentReaction(
            agent_id=self.config["id"],
            reaction_type=f"reaction_to_{event.event_type.value}",
            response=response_data["response"],
            triggered_events=triggered_events
        )
    
    def _create_reaction_prompt(self, event: Event) -> str:
        """Create a prompt for reacting to an event"""
        
        return f"""{self.config['personality_prompt']}

**Event Alert:**
- **Event Type:** {event.event_type.value}
- **From:** {event.source_agent}
- **Time:** {event.timestamp}
- **Event Data:** {json.dumps(event.data, indent=2)}

**Your Role:** {self.config['role']}
**Your Capabilities:** {', '.join(self.config['capabilities'])}

**Instructions:**
React to this event from your role's perspective. Consider:
1. Is this event relevant to your responsibilities?
2. What action (if any) should you take?
3. Do you need to alert other team members?
4. Are there any concerns or recommendations?

Respond in JSON format:
{{
  "relevance": "high/medium/low",
  "response": "Your detailed reaction",
  "action_needed": true/false,
  "alert_team": ["agent_id1", "agent_id2"] or [],
  "concerns": ["concern1", "concern2"],
  "recommendations": ["rec1", "rec2"]
}}
"""
    
    async def _call_ai_for_reaction(self, prompt: str) -> Dict[str, Any]:
        """Simulate AI API call for reaction"""
        await asyncio.sleep(0.1)
        
        # Mock responses based on role and event type
        return {
            "relevance": "high",
            "response": f"Reaction from {self.config['role']}",
            "action_needed": True,
            "alert_team": [],
            "concerns": ["Sample concern"],
            "recommendations": ["Sample recommendation"]
        }
    
    def _determine_triggered_events(self, original_event: Event, response_data: Dict) -> List[Event]:
        """Determine what events to trigger based on the reaction"""
        
        triggered_events = []
        
        # Role-specific event triggering logic
        if self.config["id"] == "tech_lead" and original_event.event_type == EventType.TASK_CREATED:
            # Tech lead triggers architecture review
            triggered_events.append(Event(
                id=str(uuid.uuid4()),
                event_type=EventType.REVIEW_REQUESTED,
                source_agent=self.config["id"],
                timestamp=datetime.now(),
                data={
                    "review_type": "architecture",
                    "original_task": original_event.data
                },
                target_agents=["developer_1", "developer_2"]
            ))
        
        elif self.config["id"] == "qa_engineer" and original_event.event_type == EventType.IMPLEMENTATION_READY:
            # QA triggers testing required
            triggered_events.append(Event(
                id=str(uuid.uuid4()),
                event_type=EventType.TESTING_REQUIRED,
                source_agent=self.config["id"],
                timestamp=datetime.now(),
                data={
                    "testing_scope": "full regression",
                    "implementation_details": original_event.data
                }
            ))
        
        # Add concern events if agent has concerns
        if response_data.get("concerns"):
            triggered_events.append(Event(
                id=str(uuid.uuid4()),
                event_type=EventType.CONCERN_RAISED,
                source_agent=self.config["id"],
                timestamp=datetime.now(),
                data={
                    "concerns": response_data["concerns"],
                    "context": original_event.data
                },
                target_agents=["manager"]
            ))
        
        return triggered_events

class ReactiveAgentSystem:
    def __init__(self, team_config_path: str = "ai_dev_team_config.json"):
        with open(team_config_path) as f:
            self.team_config = json.load(f)["members"]
        
        self.event_bus = EventBus()
        self.agents = {}
        
        # Create reactive agents
        for agent_config in self.team_config:
            self.agents[agent_config["id"]] = ReactiveAgent(agent_config, self.event_bus)
    
    async def process_task(self, task: Dict[str, Any]):
        """Start processing a task by triggering the initial event"""
        
        initial_event = Event(
            id=str(uuid.uuid4()),
            event_type=EventType.TASK_CREATED,
            source_agent="system",
            timestamp=datetime.now(),
            data=task
        )
        
        print(f"🚀 Starting reactive processing for: {task['title']}")
        await self.event_bus.publish(initial_event)
        
        # Allow time for event propagation
        await asyncio.sleep(2)
        
        return self.event_bus.event_history
    
    def get_system_state(self) -> Dict[str, Any]:
        """Get current state of all agents and events"""
        return {
            "total_events": len(self.event_bus.event_history),
            "event_types": list(set(e.event_type.value for e in self.event_bus.event_history)),
            "active_agents": list(self.agents.keys()),
            "recent_events": [
                {
                    "type": e.event_type.value,
                    "source": e.source_agent,
                    "timestamp": e.timestamp.isoformat()
                } for e in self.event_bus.event_history[-5:]
            ]
        }

# Make this importable by other modules
def create_reactive_agent_system(team_config_path: str = "ai_dev_team_config.json"):
    """Factory function to create a reactive agent system instance"""
    return ReactiveAgentSystem(team_config_path)

# Example usage
async def main():
    system = ReactiveAgentSystem()

    task = {
        "task_id": "STORY-789",
        "title": "Payment Processing Integration",
        "description": "Integrate with Stripe payment API",
        "priority": "critical"
    }

    print("⚡ Starting Reactive Agent System...")
    event_history = await system.process_task(task)

    state = system.get_system_state()
    print(f"\n📊 System processed {state['total_events']} events")
    print(f"Event types: {', '.join(state['event_types'])}")

if __name__ == "__main__":
    asyncio.run(main())
