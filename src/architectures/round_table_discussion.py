#!/usr/bin/env python3
"""
Round-Table Discussion Architecture for AI Agent Interactions

All agents participate in multiple rounds of discussion, building on each other's ideas.
Great for complex problem-solving and collaborative planning.
"""

import json
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import sys
import os

# Add parent directory to path to import ai_providers
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.ai_providers import create_ai_provider_manager

@dataclass
class DiscussionRound:
    round_number: int
    topic: str
    responses: List[Dict[str, Any]]
    consensus_items: List[str]
    unresolved_items: List[str]

class RoundTableDiscussion:
    def __init__(self, team_config_path: str = "ai_dev_team_config.json"):
        with open(team_config_path) as f:
            self.team_config = json.load(f)["members"]

        # Initialize AI provider manager
        self.ai_manager = create_ai_provider_manager()

        self.discussion_history: List[DiscussionRound] = []
        self.max_rounds = 3
    
    async def facilitate_discussion(self, task: Dict[str, Any]) -> List[DiscussionRound]:
        """Facilitate a multi-round discussion among all agents"""
        
        discussion_topics = [
            "Initial Analysis & Approach",
            "Risk Assessment & Mitigation", 
            "Implementation Planning & Timeline"
        ]
        
        for round_num, topic in enumerate(discussion_topics, 1):
            print(f"\n🗣️  Round {round_num}: {topic}")
            
            round_responses = []
            
            # Each agent contributes to this round
            for agent in self.team_config:
                prompt = self._generate_discussion_prompt(agent, task, topic, round_num)
                response = await self._get_agent_contribution(prompt, agent, topic)
                round_responses.append(response)
                
                print(f"  ✅ {agent['role']} contributed")
            
            # Analyze round for consensus and conflicts
            consensus, unresolved = self._analyze_round_consensus(round_responses)
            
            discussion_round = DiscussionRound(
                round_number=round_num,
                topic=topic,
                responses=round_responses,
                consensus_items=consensus,
                unresolved_items=unresolved
            )
            
            self.discussion_history.append(discussion_round)
            
            # Show round summary
            print(f"  📋 Consensus: {len(consensus)} items")
            print(f"  ⚠️  Unresolved: {len(unresolved)} items")
        
        return self.discussion_history
    
    def _generate_discussion_prompt(self, agent: Dict, task: Dict, topic: str, round_num: int) -> str:
        """Generate discussion prompt with context from previous rounds"""
        
        prompt = f"""{agent['personality_prompt']}

**Discussion Topic:** {topic} (Round {round_num})

**Task Context:**
- **Story ID:** {task.get('task_id', 'N/A')}
- **Title:** {task.get('title', 'N/A')}
- **Description:** {task.get('description', 'N/A')}
- **Priority:** {task.get('priority', 'medium')}

**Your Role:** {agent['role']}
**Your Capabilities:** {', '.join(agent['capabilities'])}
"""
        
        # Add context from previous discussion rounds
        if self.discussion_history:
            prompt += "\n**Previous Discussion Summary:**\n"
            for prev_round in self.discussion_history:
                prompt += f"\n**Round {prev_round.round_number} - {prev_round.topic}:**\n"
                prompt += f"- Team Consensus: {', '.join(prev_round.consensus_items[:3])}\n"
                if prev_round.unresolved_items:
                    prompt += f"- Unresolved Issues: {', '.join(prev_round.unresolved_items[:2])}\n"
        
        # Round-specific instructions
        round_instructions = {
            1: """Focus on your initial analysis of the task. What's your perspective on:
- Feasibility and complexity
- Key requirements from your role's viewpoint
- Initial approach you'd recommend""",
            
            2: """Based on Round 1 discussion, identify and address:
- Potential risks and challenges
- Dependencies between team members
- Mitigation strategies for identified risks""",
            
            3: """Finalize the implementation plan by addressing:
- Specific timeline estimates for your work
- Resource requirements and dependencies
- Final recommendations and next steps"""
        }
        
        prompt += f"""

**Round {round_num} Focus:**
{round_instructions.get(round_num, "Provide your perspective on the current topic.")}

**Instructions:**
Provide a focused response addressing the round topic. Consider what others might say and build on the discussion. Format as JSON:
{{
  "perspective": "Your main viewpoint",
  "key_points": ["point1", "point2", "point3"],
  "concerns": ["concern1", "concern2"],
  "suggestions": ["suggestion1", "suggestion2"],
  "questions_for_team": ["question1", "question2"]
}}
"""
        return prompt
    
    async def _get_agent_contribution(self, prompt: str, agent: Dict, topic: str) -> Dict[str, Any]:
        """Get agent's contribution to the discussion using real AI"""

        try:
            # Get AI response
            ai_response = await self.ai_manager.generate_response(
                prompt,
                agent_role=agent["role"],
                max_tokens=600,
                temperature=0.8  # Slightly higher for more creative discussion
            )

            # Parse the AI response
            contribution = self._parse_discussion_response(ai_response.content, agent, topic)

            return {
                "agent_id": agent["id"],
                "role": agent["role"],
                "timestamp": datetime.now().isoformat(),
                "contribution": contribution
            }

        except Exception as e:
            print(f"⚠️  AI call failed for {agent['role']} on {topic}: {e}")

            # Fallback to mock response
            return self._get_fallback_contribution(agent, topic)

    def _parse_discussion_response(self, ai_content: str, agent: Dict, topic: str) -> Dict[str, Any]:
        """Parse AI response for discussion contribution"""

        # Try to parse JSON response first
        try:
            import re
            json_match = re.search(r'\{.*\}', ai_content, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                return {
                    "perspective": parsed.get("perspective", ai_content[:200]),
                    "key_points": parsed.get("key_points", []),
                    "concerns": parsed.get("concerns", []),
                    "suggestions": parsed.get("suggestions", []),
                    "questions_for_team": parsed.get("questions_for_team", [])
                }
        except (json.JSONDecodeError, AttributeError):
            pass

        # Extract from text if JSON parsing fails
        return self._extract_discussion_points(ai_content, agent, topic)

    def _extract_discussion_points(self, content: str, agent: Dict, topic: str) -> Dict[str, Any]:
        """Extract discussion points from free-form text"""

        lines = content.split('\n')

        key_points = []
        concerns = []
        suggestions = []
        questions = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if any(word in line.lower() for word in ['concern', 'worry', 'risk', 'issue']):
                concerns.append(line)
            elif any(word in line.lower() for word in ['suggest', 'recommend', 'should', 'could']):
                suggestions.append(line)
            elif '?' in line:
                questions.append(line)
            elif any(word in line.lower() for word in ['key', 'important', 'main', 'primary']):
                key_points.append(line)

        return {
            "perspective": content[:200] + "..." if len(content) > 200 else content,
            "key_points": key_points[:3],
            "concerns": concerns[:3],
            "suggestions": suggestions[:3],
            "questions_for_team": questions[:2]
        }

    def _get_fallback_contribution(self, agent: Dict, topic: str) -> Dict[str, Any]:
        """Fallback contribution when AI is unavailable"""

        fallback_contributions = {
            ("manager", "Initial Analysis & Approach"): {
                "perspective": "Need clear timeline and resource allocation for successful delivery",
                "key_points": ["Sprint planning required", "Risk assessment needed", "Stakeholder communication plan"],
                "concerns": ["Scope creep", "Resource conflicts"],
                "suggestions": ["Weekly checkpoints", "Clear deliverable milestones"],
                "questions_for_team": ["What are the hard dependencies?", "Any external blockers?"]
            },
            ("tech_lead", "Risk Assessment & Mitigation"): {
                "perspective": "Technical risks need early identification and mitigation strategies",
                "key_points": ["Architecture decisions impact timeline", "Code review process", "Technical debt considerations"],
                "concerns": ["Scalability requirements", "Integration complexity"],
                "suggestions": ["Proof of concept first", "Incremental development"],
                "questions_for_team": ["What's the expected load?", "Any legacy system constraints?"]
            },
            ("product_owner", "Implementation Planning & Timeline"): {
                "perspective": "User value delivery should drive implementation priorities",
                "key_points": ["User story prioritization", "Acceptance criteria clarity", "Stakeholder feedback loops"],
                "concerns": ["Feature scope clarity", "User acceptance"],
                "suggestions": ["MVP approach", "User testing early"],
                "questions_for_team": ["What's the minimum viable feature set?", "How do we measure success?"]
            }
        }

        key = (agent["id"], topic)
        fallback_data = fallback_contributions.get(key, {
            "perspective": f"{agent['role']} perspective on {topic} (AI unavailable)",
            "key_points": [f"Key consideration from {agent['role']}"],
            "concerns": [f"Potential concern from {agent['role']}"],
            "suggestions": [f"Suggestion from {agent['role']}"],
            "questions_for_team": [f"Question from {agent['role']}"]
        })

        return {
            "agent_id": agent["id"],
            "role": agent["role"],
            "timestamp": datetime.now().isoformat(),
            "contribution": fallback_data
        }
    
    def _analyze_round_consensus(self, responses: List[Dict]) -> tuple[List[str], List[str]]:
        """Analyze responses to identify consensus and unresolved items"""
        
        # Simple consensus detection (in real implementation, use NLP/similarity)
        all_points = []
        all_concerns = []
        
        for response in responses:
            contrib = response["contribution"]
            all_points.extend(contrib.get("key_points", []))
            all_concerns.extend(contrib.get("concerns", []))
        
        # Mock consensus detection
        consensus = ["Clear requirements needed", "Timeline estimation important"]
        unresolved = ["Resource allocation", "Technical approach"]
        
        return consensus, unresolved
    
    def generate_discussion_summary(self) -> Dict[str, Any]:
        """Generate a comprehensive summary of the entire discussion"""
        
        all_consensus = []
        all_unresolved = []
        
        for round_data in self.discussion_history:
            all_consensus.extend(round_data.consensus_items)
            all_unresolved.extend(round_data.unresolved_items)
        
        return {
            "total_rounds": len(self.discussion_history),
            "final_consensus": list(set(all_consensus)),
            "remaining_issues": list(set(all_unresolved)),
            "next_actions": self._generate_next_actions(),
            "discussion_timeline": [
                {
                    "round": r.round_number,
                    "topic": r.topic,
                    "participants": len(r.responses)
                } for r in self.discussion_history
            ]
        }
    
    def _generate_next_actions(self) -> List[str]:
        """Generate recommended next actions based on discussion"""
        return [
            "Create detailed project plan",
            "Assign specific tasks to team members", 
            "Schedule follow-up meetings",
            "Document architectural decisions"
        ]

# Make this importable by other modules
def create_round_table_discussion(team_config_path: str = "ai_dev_team_config.json"):
    """Factory function to create a round table discussion instance"""
    return RoundTableDiscussion(team_config_path)

# Example usage
async def main():
    discussion = RoundTableDiscussion()

    task = {
        "task_id": "STORY-456",
        "title": "Real-time Chat Feature",
        "description": "Add real-time messaging to the application",
        "priority": "high"
    }

    print("🗣️  Starting Round-Table Discussion...")
    rounds = await discussion.facilitate_discussion(task)

    summary = discussion.generate_discussion_summary()
    print(f"\n📊 Discussion Complete!")
    print(f"Final Consensus: {', '.join(summary['final_consensus'])}")
    print(f"Next Actions: {', '.join(summary['next_actions'])}")

if __name__ == "__main__":
    asyncio.run(main())
