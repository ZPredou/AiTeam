#!/usr/bin/env python3
"""
Hierarchical Decision Tree Architecture for AI Agent Interactions

Agents are organized in a hierarchy with decision-making authority.
Decisions flow up for approval and instructions flow down for execution.
"""

import json
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class DecisionType(Enum):
    TECHNICAL_APPROACH = "technical_approach"
    RESOURCE_ALLOCATION = "resource_allocation"
    TIMELINE_CHANGE = "timeline_change"
    SCOPE_CHANGE = "scope_change"
    RISK_MITIGATION = "risk_mitigation"

class DecisionStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"

@dataclass
class Decision:
    id: str
    decision_type: DecisionType
    proposed_by: str
    description: str
    rationale: str
    impact_assessment: Dict[str, Any]
    status: DecisionStatus
    approver: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class HierarchyNode:
    agent_id: str
    role: str
    level: int  # 0 = top level (manager), higher = lower in hierarchy
    reports_to: Optional[str]
    direct_reports: List[str]
    decision_authority: List[DecisionType]

class HierarchicalDecisionSystem:
    def __init__(self, team_config_path: str = "ai_dev_team_config.json"):
        with open(team_config_path) as f:
            self.team_config = json.load(f)["members"]
        
        self.hierarchy = self._build_hierarchy()
        self.pending_decisions: List[Decision] = []
        self.decision_history: List[Decision] = []
    
    def _build_hierarchy(self) -> Dict[str, HierarchyNode]:
        """Build the organizational hierarchy"""
        
        hierarchy = {
            "manager": HierarchyNode(
                agent_id="manager",
                role="Project Manager", 
                level=0,
                reports_to=None,
                direct_reports=["product_owner", "tech_lead"],
                decision_authority=[DecisionType.RESOURCE_ALLOCATION, DecisionType.TIMELINE_CHANGE, DecisionType.SCOPE_CHANGE]
            ),
            "product_owner": HierarchyNode(
                agent_id="product_owner",
                role="Product Owner",
                level=1,
                reports_to="manager",
                direct_reports=[],
                decision_authority=[DecisionType.SCOPE_CHANGE]
            ),
            "tech_lead": HierarchyNode(
                agent_id="tech_lead", 
                role="Tech Lead",
                level=1,
                reports_to="manager",
                direct_reports=["developer_1", "developer_2", "qa_engineer"],
                decision_authority=[DecisionType.TECHNICAL_APPROACH, DecisionType.RISK_MITIGATION]
            ),
            "developer_1": HierarchyNode(
                agent_id="developer_1",
                role="Software Developer (Frontend)",
                level=2,
                reports_to="tech_lead",
                direct_reports=[],
                decision_authority=[]
            ),
            "developer_2": HierarchyNode(
                agent_id="developer_2",
                role="Software Developer (Backend)", 
                level=2,
                reports_to="tech_lead",
                direct_reports=[],
                decision_authority=[]
            ),
            "qa_engineer": HierarchyNode(
                agent_id="qa_engineer",
                role="QA Engineer",
                level=2,
                reports_to="tech_lead", 
                direct_reports=[],
                decision_authority=[]
            )
        }
        
        return hierarchy
    
    async def process_task_hierarchically(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process task through hierarchical decision-making"""
        
        print(f"🏢 Starting hierarchical processing for: {task['title']}")
        
        # Phase 1: Bottom-up analysis
        analysis_results = await self._bottom_up_analysis(task)
        
        # Phase 2: Decision proposals
        decisions = await self._generate_decision_proposals(task, analysis_results)
        
        # Phase 3: Decision approval process
        approved_decisions = await self._process_decisions(decisions)
        
        # Phase 4: Top-down execution planning
        execution_plan = await self._create_execution_plan(task, approved_decisions)
        
        return {
            "task": task,
            "analysis_results": analysis_results,
            "approved_decisions": approved_decisions,
            "execution_plan": execution_plan,
            "decision_timeline": [d.timestamp.isoformat() for d in approved_decisions]
        }
    
    async def _bottom_up_analysis(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Collect analysis from bottom level up"""
        
        analysis_by_level = {}
        
        # Start from highest level (bottom of hierarchy)
        max_level = max(node.level for node in self.hierarchy.values())
        
        for level in range(max_level, -1, -1):
            level_agents = [node for node in self.hierarchy.values() if node.level == level]
            level_analysis = []
            
            for node in level_agents:
                agent_config = next(a for a in self.team_config if a["id"] == node.agent_id)
                analysis = await self._get_agent_analysis(agent_config, task, analysis_by_level)
                level_analysis.append(analysis)
                
                print(f"  📊 Level {level}: {node.role} completed analysis")
            
            analysis_by_level[level] = level_analysis
        
        return analysis_by_level
    
    async def _get_agent_analysis(self, agent: Dict, task: Dict, previous_analysis: Dict) -> Dict[str, Any]:
        """Get analysis from a specific agent"""
        
        prompt = f"""{agent['personality_prompt']}

**Task Analysis Request:**
- **Story ID:** {task.get('task_id', 'N/A')}
- **Title:** {task.get('title', 'N/A')}
- **Description:** {task.get('description', 'N/A')}
- **Priority:** {task.get('priority', 'medium')}

**Your Role:** {agent['role']}
**Your Position:** {"Leadership" if self.hierarchy[agent["id"]].level <= 1 else "Individual Contributor"}

**Previous Analysis Context:**
{json.dumps(previous_analysis, indent=2) if previous_analysis else "None available"}

**Instructions:**
Provide your analysis focusing on your role's perspective. Include:
1. Feasibility assessment
2. Resource requirements
3. Risk identification
4. Recommendations for decisions needed
5. Dependencies on other team members

Format as JSON:
{{
  "feasibility": "high/medium/low",
  "resource_estimate": "X hours/days",
  "risks": ["risk1", "risk2"],
  "decision_recommendations": [
    {{
      "type": "technical_approach/resource_allocation/etc",
      "description": "What decision is needed",
      "rationale": "Why this decision is important"
    }}
  ],
  "dependencies": ["agent_id1", "agent_id2"]
}}
"""
        
        # Simulate AI response
        await asyncio.sleep(0.1)
        
        # Mock response based on role
        mock_responses = {
            "manager": {
                "feasibility": "high",
                "resource_estimate": "2 weeks",
                "risks": ["Timeline pressure", "Resource conflicts"],
                "decision_recommendations": [
                    {
                        "type": "resource_allocation",
                        "description": "Allocate dedicated resources for 2 weeks",
                        "rationale": "Ensures focused delivery without conflicts"
                    }
                ],
                "dependencies": ["tech_lead", "product_owner"]
            },
            "tech_lead": {
                "feasibility": "medium",
                "resource_estimate": "1.5 weeks",
                "risks": ["Technical complexity", "Integration challenges"],
                "decision_recommendations": [
                    {
                        "type": "technical_approach",
                        "description": "Use microservices architecture",
                        "rationale": "Better scalability and maintainability"
                    }
                ],
                "dependencies": ["developer_1", "developer_2"]
            }
        }
        
        return {
            "agent_id": agent["id"],
            "role": agent["role"],
            "analysis": mock_responses.get(agent["id"], {
                "feasibility": "medium",
                "resource_estimate": "TBD",
                "risks": ["General risk"],
                "decision_recommendations": [],
                "dependencies": []
            })
        }
    
    async def _generate_decision_proposals(self, task: Dict, analysis: Dict) -> List[Decision]:
        """Generate decision proposals from analysis"""
        
        decisions = []
        decision_counter = 1
        
        # Extract decision recommendations from all analysis
        for level_analysis in analysis.values():
            for agent_analysis in level_analysis:
                for rec in agent_analysis["analysis"].get("decision_recommendations", []):
                    decision = Decision(
                        id=f"DEC-{decision_counter:03d}",
                        decision_type=DecisionType(rec["type"]),
                        proposed_by=agent_analysis["agent_id"],
                        description=rec["description"],
                        rationale=rec["rationale"],
                        impact_assessment={
                            "timeline_impact": "TBD",
                            "resource_impact": "TBD",
                            "risk_impact": "TBD"
                        },
                        status=DecisionStatus.PENDING
                    )
                    decisions.append(decision)
                    decision_counter += 1
        
        return decisions
    
    async def _process_decisions(self, decisions: List[Decision]) -> List[Decision]:
        """Process decisions through approval hierarchy"""
        
        approved_decisions = []
        
        for decision in decisions:
            print(f"  🤔 Processing decision: {decision.description}")
            
            # Find appropriate approver
            approver = self._find_decision_approver(decision)
            
            if approver:
                # Simulate approval process
                approval_result = await self._get_approval(decision, approver)
                
                if approval_result["approved"]:
                    decision.status = DecisionStatus.APPROVED
                    decision.approver = approver
                    approved_decisions.append(decision)
                    print(f"    ✅ Approved by {self.hierarchy[approver].role}")
                else:
                    decision.status = DecisionStatus.REJECTED
                    print(f"    ❌ Rejected by {self.hierarchy[approver].role}")
            else:
                decision.status = DecisionStatus.ESCALATED
                print(f"    ⬆️  Escalated - no clear approver")
        
        return approved_decisions
    
    def _find_decision_approver(self, decision: Decision) -> Optional[str]:
        """Find the appropriate approver for a decision"""
        
        # Find agents with authority for this decision type
        authorized_agents = [
            agent_id for agent_id, node in self.hierarchy.items()
            if decision.decision_type in node.decision_authority
        ]
        
        if not authorized_agents:
            return None
        
        # Return the one with lowest level (highest authority)
        return min(authorized_agents, key=lambda x: self.hierarchy[x].level)
    
    async def _get_approval(self, decision: Decision, approver_id: str) -> Dict[str, Any]:
        """Get approval decision from approver"""
        
        approver = self.hierarchy[approver_id]
        agent_config = next(a for a in self.team_config if a["id"] == approver_id)
        
        # Simulate approval decision (replace with actual AI call)
        await asyncio.sleep(0.1)
        
        # Mock approval logic
        approval_rates = {
            "manager": 0.8,  # Approves 80% of decisions
            "tech_lead": 0.9,  # Approves 90% of technical decisions
            "product_owner": 0.7  # Approves 70% of scope decisions
        }
        
        import random
        approved = random.random() < approval_rates.get(approver_id, 0.8)
        
        return {
            "approved": approved,
            "rationale": f"Decision {'approved' if approved else 'rejected'} by {approver.role}",
            "conditions": [] if approved else ["Needs more analysis"]
        }
    
    async def _create_execution_plan(self, task: Dict, decisions: List[Decision]) -> Dict[str, Any]:
        """Create top-down execution plan based on approved decisions"""
        
        # Manager creates overall execution plan
        manager_node = self.hierarchy["manager"]
        
        execution_plan = {
            "overall_timeline": "2 weeks",
            "phases": [
                {
                    "phase": "Planning & Design",
                    "duration": "3 days",
                    "responsible": ["tech_lead", "product_owner"],
                    "deliverables": ["Architecture design", "Detailed requirements"]
                },
                {
                    "phase": "Implementation", 
                    "duration": "7 days",
                    "responsible": ["developer_1", "developer_2"],
                    "deliverables": ["Frontend components", "Backend APIs"]
                },
                {
                    "phase": "Testing & QA",
                    "duration": "3 days", 
                    "responsible": ["qa_engineer"],
                    "deliverables": ["Test results", "Bug reports"]
                },
                {
                    "phase": "Deployment",
                    "duration": "1 day",
                    "responsible": ["tech_lead", "developer_2"],
                    "deliverables": ["Production deployment"]
                }
            ],
            "approved_decisions": [d.id for d in decisions],
            "success_criteria": ["All tests pass", "Performance benchmarks met", "User acceptance complete"]
        }
        
        return execution_plan

# Example usage
async def main():
    system = HierarchicalDecisionSystem()
    
    task = {
        "task_id": "STORY-999",
        "title": "Multi-tenant Architecture Migration",
        "description": "Migrate single-tenant system to multi-tenant architecture",
        "priority": "critical"
    }
    
    print("🏢 Starting Hierarchical Decision Processing...")
    result = await system.process_task_hierarchically(task)
    
    print(f"\n📊 Processing Complete!")
    print(f"Approved Decisions: {len(result['approved_decisions'])}")
    print(f"Execution Phases: {len(result['execution_plan']['phases'])}")

if __name__ == "__main__":
    asyncio.run(main())
