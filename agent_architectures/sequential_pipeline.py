#!/usr/bin/env python3
"""
Sequential Pipeline Architecture for AI Agent Interactions

Flow: Product Owner → Tech Lead → Developer → QA → Project Manager
Each agent processes the task and passes enriched context to the next agent.
"""

import json
import asyncio
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import sys
import os

# Add parent directory to path to import ai_providers
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_providers import create_ai_provider_manager, AIResponse

@dataclass
class AgentResponse:
    agent_id: str
    role: str
    timestamp: datetime
    response: str
    recommendations: List[str]
    concerns: List[str]
    next_steps: List[str]
    estimated_effort: str

class SequentialPipeline:
    def __init__(self, team_config_path: str = "ai_dev_team_config.json"):
        with open(team_config_path) as f:
            self.team_config = json.load(f)["members"]

        # Initialize AI provider manager
        self.ai_manager = create_ai_provider_manager()

        # Define the pipeline order
        self.pipeline_order = [
            "product_owner",    # Clarifies requirements
            "tech_lead",        # Designs architecture
            "developer_1",      # Frontend implementation
            "developer_2",      # Backend implementation
            "qa_engineer",      # Testing strategy
            "manager"           # Final coordination
        ]
    
    async def process_task(self, task: Dict[str, Any]) -> List[AgentResponse]:
        """Process a task through the sequential pipeline"""
        responses = []
        accumulated_context = task.copy()
        
        for agent_id in self.pipeline_order:
            agent = self._get_agent(agent_id)
            if not agent:
                continue
                
            # Generate prompt with accumulated context
            prompt = self._generate_contextual_prompt(agent, accumulated_context, responses)
            
            # Call AI agent with task context for better fallbacks
            response = await self._call_ai_agent(prompt, agent, task)
            
            # Add response to accumulated context
            accumulated_context[f"{agent_id}_response"] = response.response
            responses.append(response)
            
            print(f"✅ {agent['role']} completed analysis")
        
        return responses
    
    def _get_agent(self, agent_id: str) -> Dict[str, Any]:
        return next((m for m in self.team_config if m["id"] == agent_id), None)
    
    def _generate_contextual_prompt(self, agent: Dict, task: Dict, previous_responses: List[AgentResponse]) -> str:
        """Generate prompt with context from previous agents"""
        
        # Base prompt
        prompt = f"""{agent['personality_prompt']}

**Task Assignment:**
- **Story ID:** {task.get('task_id', 'N/A')}
- **Title:** {task.get('title', 'N/A')}
- **Description:** {task.get('description', 'N/A')}
- **Priority:** {task.get('priority', 'medium')}

**Your Role:** {agent['role']}
**Your Capabilities:** {', '.join(agent['capabilities'])}
"""
        
        # Add context from previous agents
        if previous_responses:
            prompt += "\n**Previous Team Analysis:**\n"
            for resp in previous_responses:
                prompt += f"\n**{resp.role}:**\n"
                prompt += f"- Response: {resp.response[:200]}...\n"
                prompt += f"- Key Concerns: {', '.join(resp.concerns[:2])}\n"
                prompt += f"- Recommendations: {', '.join(resp.recommendations[:2])}\n"
        
        prompt += """
**Instructions:**
As an expert in your role, provide a comprehensive analysis. Be thorough and specific to this task.

**Required Response Format (JSON):**
{
  "analysis": "Your detailed analysis of the task from your role's perspective (2-3 sentences)",
  "concerns": [
    "Specific concern 1 relevant to your role and this task",
    "Specific concern 2 relevant to your role and this task",
    "Specific concern 3 relevant to your role and this task",
    "Specific concern 4 relevant to your role and this task",
    "Specific concern 5 relevant to your role and this task",
    "Specific concern 6 relevant to your role and this task",
    "Specific concern 7 relevant to your role and this task"
  ],
  "recommendations": [
    "Specific actionable recommendation 1 for this task",
    "Specific actionable recommendation 2 for this task",
    "Specific actionable recommendation 3 for this task",
    "Specific actionable recommendation 4 for this task",
    "Specific actionable recommendation 5 for this task",
    "Specific actionable recommendation 6 for this task",
    "Specific actionable recommendation 7 for this task",
    "Specific actionable recommendation 8 for this task"
  ],
  "effort_estimate": "Realistic time estimate (e.g., '3-5 days', '1-2 weeks')",
  "next_steps": [
    "Immediate next step 1",
    "Immediate next step 2",
    "Immediate next step 3"
  ]
}

**Important:**
- Provide exactly 7 concerns and 8 recommendations minimum
- Make each concern and recommendation specific to this task and your role
- Be professional and detailed
- Consider the task description, priority, and previous team input
"""
        return prompt
    
    async def _call_ai_agent(self, prompt: str, agent: Dict, task: Dict = None) -> AgentResponse:
        """Call real AI agent using the AI provider manager"""

        try:
            # Get AI response
            ai_response = await self.ai_manager.generate_response(
                prompt,
                agent_role=agent["role"],
                max_tokens=800,
                temperature=0.7
            )

            # Parse the AI response to extract structured data
            parsed_response = self._parse_ai_response(ai_response.content, agent)

            return AgentResponse(
                agent_id=agent["id"],
                role=agent["role"],
                timestamp=datetime.now(),
                response=parsed_response["analysis"],
                recommendations=parsed_response["recommendations"],
                concerns=parsed_response["concerns"],
                next_steps=parsed_response["next_steps"],
                estimated_effort=parsed_response["effort_estimate"]
            )

        except Exception as e:
            print(f"⚠️  AI call failed for {agent['role']}: {e}")

            # Fallback to intelligent response if AI fails
            return self._get_fallback_response(agent, task)

    def _parse_ai_response(self, ai_content: str, agent: Dict) -> Dict[str, Any]:
        """Parse AI response to extract structured information"""

        # Try to parse JSON response first
        try:
            # Look for JSON in the response
            import re
            json_match = re.search(r'\{.*\}', ai_content, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                return {
                    "analysis": parsed.get("analysis", ai_content),
                    "concerns": parsed.get("concerns", []),
                    "recommendations": parsed.get("recommendations", []),
                    "effort_estimate": parsed.get("effort_estimate", "TBD"),
                    "next_steps": parsed.get("next_steps", [])
                }
        except (json.JSONDecodeError, AttributeError):
            pass

        # If JSON parsing fails, extract information using text parsing
        return self._extract_from_text(ai_content, agent)

    def _extract_from_text(self, content: str, agent: Dict) -> Dict[str, Any]:
        """Extract structured information from free-form text with enhanced parsing"""

        lines = content.split('\n')

        concerns = []
        recommendations = []
        next_steps = []
        effort_estimate = "TBD"
        analysis_lines = []

        # Enhanced parsing to extract lists and structured content
        in_concerns_section = False
        in_recommendations_section = False
        in_next_steps_section = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for section headers
            if any(word in line.lower() for word in ['concerns:', 'risks:', 'issues:']):
                in_concerns_section = True
                in_recommendations_section = False
                in_next_steps_section = False
                continue
            elif any(word in line.lower() for word in ['recommendations:', 'suggests:', 'should:']):
                in_concerns_section = False
                in_recommendations_section = True
                in_next_steps_section = False
                continue
            elif any(word in line.lower() for word in ['next steps:', 'actions:', 'follow-up:']):
                in_concerns_section = False
                in_recommendations_section = False
                in_next_steps_section = True
                continue

            # Extract content based on current section
            if in_concerns_section:
                if line.startswith(('-', '•', '*', '1.', '2.', '3.', '4.', '5.', '6.', '7.')):
                    concerns.append(line.lstrip('-•*0123456789. '))
                elif any(word in line.lower() for word in ['concern', 'risk', 'issue', 'problem', 'challenge']):
                    concerns.append(line)
            elif in_recommendations_section:
                if line.startswith(('-', '•', '*', '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.')):
                    recommendations.append(line.lstrip('-•*0123456789. '))
                elif any(word in line.lower() for word in ['recommend', 'suggest', 'should', 'implement', 'create', 'establish']):
                    recommendations.append(line)
            elif in_next_steps_section:
                if line.startswith(('-', '•', '*', '1.', '2.', '3.')):
                    next_steps.append(line.lstrip('-•*0123456789. '))
            else:
                # General content parsing
                if any(word in line.lower() for word in ['hour', 'day', 'week', 'month', 'effort', 'estimate']):
                    effort_estimate = line
                elif len(analysis_lines) < 3:  # Collect first few lines for analysis
                    analysis_lines.append(line)

        # If no structured sections found, fall back to keyword-based extraction
        if not concerns and not recommendations:
            for line in lines:
                line = line.strip()
                if any(word in line.lower() for word in ['concern', 'risk', 'issue', 'problem', 'challenge']):
                    concerns.append(line)
                elif any(word in line.lower() for word in ['recommend', 'suggest', 'should', 'implement']):
                    recommendations.append(line)
                elif any(word in line.lower() for word in ['next', 'step', 'action', 'follow']):
                    next_steps.append(line)

        # Create analysis from collected lines or use beginning of content
        analysis = ' '.join(analysis_lines) if analysis_lines else content[:300] + "..." if len(content) > 300 else content

        return {
            "analysis": analysis,
            "concerns": concerns[:7],  # Up to 7 concerns as requested
            "recommendations": recommendations[:8],  # Up to 8 recommendations as requested
            "effort_estimate": effort_estimate,
            "next_steps": next_steps[:3]
        }

    def _get_fallback_response(self, agent: Dict, task: Dict = None) -> AgentResponse:
        """Fallback response when AI is unavailable - provides intelligent analysis based on task"""

        # If we have task information, provide contextual analysis
        if task:
            return self._generate_contextual_fallback(agent, task)

        # Otherwise use generic fallback responses
        fallback_responses = {
            "product_owner": {
                "analysis": "Requirements need clarification and user acceptance criteria",
                "concerns": ["Missing user personas", "Unclear success metrics"],
                "recommendations": ["Add acceptance criteria", "Define user flows"],
                "effort_estimate": "2-3 days",
                "next_steps": ["Create detailed user stories", "Review with stakeholders"]
            },
            "tech_lead": {
                "analysis": "Technical approach needs architectural review and design decisions",
                "concerns": ["Scalability requirements", "Integration complexity"],
                "recommendations": ["Design system architecture", "Define API contracts"],
                "effort_estimate": "1 week",
                "next_steps": ["Create architecture diagram", "Review technical stack"]
            },
            "developer_1": {
                "analysis": "Frontend implementation requires UI/UX design and component planning",
                "concerns": ["Browser compatibility", "Performance optimization"],
                "recommendations": ["Create component library", "Implement responsive design"],
                "effort_estimate": "1-2 weeks",
                "next_steps": ["Set up development environment", "Create UI mockups"]
            },
            "developer_2": {
                "analysis": "Backend development needs database design and API implementation",
                "concerns": ["Data security", "API performance"],
                "recommendations": ["Design database schema", "Implement authentication"],
                "effort_estimate": "1-2 weeks",
                "next_steps": ["Set up database", "Create API endpoints"]
            },
            "qa_engineer": {
                "analysis": "Testing strategy requires test plan creation and automation setup",
                "concerns": ["Test coverage", "Regression testing"],
                "recommendations": ["Create automated tests", "Set up CI/CD pipeline"],
                "effort_estimate": "3-5 days",
                "next_steps": ["Write test cases", "Set up testing framework"]
            },
            "manager": {
                "analysis": "Project coordination requires timeline planning and resource allocation",
                "concerns": ["Resource availability", "Timeline constraints"],
                "recommendations": ["Create project timeline", "Assign team responsibilities"],
                "effort_estimate": "1-2 days",
                "next_steps": ["Schedule team meetings", "Track project progress"]
            }
        }

        fallback_data = fallback_responses.get(agent["id"], {
            "analysis": f"Analysis from {agent['role']} (AI unavailable)",
            "concerns": ["General concern"],
            "recommendations": ["General recommendation"],
            "effort_estimate": "TBD",
            "next_steps": ["Next step"]
        })

        return AgentResponse(
            agent_id=agent["id"],
            role=agent["role"],
            timestamp=datetime.now(),
            response=fallback_data["analysis"],
            recommendations=fallback_data["recommendations"],
            concerns=fallback_data["concerns"],
            next_steps=fallback_data["next_steps"],
            estimated_effort=fallback_data["effort_estimate"]
        )

    def _generate_contextual_fallback(self, agent: Dict, task: Dict) -> AgentResponse:
        """Generate contextual fallback response based on task and agent role"""

        task_title = task.get('title', 'Unknown Task')
        task_description = task.get('description', 'No description provided')
        task_priority = task.get('priority', 'medium')

        # Role-specific contextual analysis
        if agent["id"] == "product_owner":
            analysis = f"For '{task_title}', I need to ensure we have clear user acceptance criteria and business value definition. "
            if 'user' in task_description.lower() or 'login' in task_description.lower():
                analysis += "This involves user experience considerations and authentication flows. "
            if 'payment' in task_description.lower() or 'checkout' in task_description.lower():
                analysis += "Payment security and compliance (PCI DSS) are critical. "
            if 'mobile' in task_description.lower() or 'app' in task_description.lower():
                analysis += "Mobile user experience and cross-platform considerations are essential. "

            concerns = [
                "User acceptance criteria may be incomplete or ambiguous",
                "Business value and ROI metrics are not clearly defined",
                "Stakeholder alignment on priorities and scope",
                "User personas and journey mapping need validation",
                "Compliance requirements (GDPR, accessibility) may be overlooked",
                "Market competition and differentiation factors",
                "Integration with existing business processes"
            ]

            recommendations = [
                "Conduct comprehensive stakeholder interviews to gather requirements",
                "Create detailed user stories with clear acceptance criteria",
                "Define measurable success metrics and KPIs",
                "Develop user personas based on market research",
                "Create user journey maps for all key workflows",
                "Establish a feedback loop with end users through prototyping",
                "Document business rules and edge cases thoroughly",
                "Plan for A/B testing to validate assumptions"
            ]

            effort = "2-3 days for requirements analysis"
            next_steps = ["Stakeholder interviews", "User story creation"]

        elif agent["id"] == "tech_lead":
            analysis = f"For '{task_title}', I need to design the technical architecture and identify system dependencies. "
            if 'api' in task_description.lower() or 'service' in task_description.lower():
                analysis += "This requires API design and service architecture planning. "
            if 'database' in task_description.lower() or 'data' in task_description.lower():
                analysis += "Database schema design and data modeling are needed. "
            if 'real-time' in task_description.lower() or 'websocket' in task_description.lower():
                analysis += "Real-time communication architecture and WebSocket implementation are critical. "

            concerns = [
                "System scalability under high load conditions",
                "Technical debt accumulation from rushed implementation",
                "Security vulnerabilities in API endpoints and data handling",
                "Database performance bottlenecks and query optimization",
                "Third-party service dependencies and potential failures",
                "Code maintainability and documentation standards",
                "Integration complexity with existing systems",
                "Performance monitoring and alerting gaps",
                "Disaster recovery and backup strategies"
            ]

            recommendations = [
                "Design microservices architecture with clear service boundaries",
                "Implement comprehensive API documentation with OpenAPI/Swagger",
                "Establish database indexing strategy and query optimization",
                "Set up automated testing pipeline with unit, integration, and E2E tests",
                "Implement proper logging, monitoring, and alerting systems",
                "Create detailed technical documentation and architecture diagrams",
                "Establish code review processes and coding standards",
                "Plan for horizontal scaling and load balancing",
                "Implement circuit breakers and retry mechanisms for resilience",
                "Set up staging environment that mirrors production"
            ]

            effort = "1 week for technical design"
            next_steps = ["Architecture review", "Technology stack selection"]

        elif agent["id"] == "developer_1":  # Frontend
            analysis = f"For '{task_title}', I'll focus on the user interface and frontend implementation. "
            if 'mobile' in task_description.lower():
                analysis += "This requires responsive design and mobile optimization. "
            if 'dashboard' in task_description.lower() or 'chart' in task_description.lower():
                analysis += "Data visualization and interactive components will be needed. "
            if 'real-time' in task_description.lower():
                analysis += "Real-time UI updates and WebSocket integration are essential. "

            concerns = [
                "Cross-browser compatibility issues across different versions",
                "Performance optimization for large datasets and complex UIs",
                "Accessibility compliance (WCAG 2.1) for all user interactions",
                "Mobile responsiveness and touch interface optimization",
                "State management complexity in dynamic applications",
                "Bundle size optimization and lazy loading implementation",
                "SEO considerations for single-page applications",
                "User experience consistency across different screen sizes",
                "Frontend security vulnerabilities (XSS, CSRF protection)"
            ]

            recommendations = [
                "Implement a comprehensive component library with Storybook documentation",
                "Set up automated testing with Jest, React Testing Library, and Cypress",
                "Use CSS-in-JS or CSS modules for maintainable styling",
                "Implement progressive web app features for better user experience",
                "Set up performance monitoring with Core Web Vitals tracking",
                "Create responsive design system with consistent spacing and typography",
                "Implement proper error boundaries and loading states",
                "Use code splitting and lazy loading for optimal bundle sizes",
                "Set up accessibility testing and screen reader compatibility",
                "Implement proper form validation and user feedback mechanisms"
            ]

            effort = "1-2 weeks for frontend development"
            next_steps = ["UI mockups", "Component development"]

        elif agent["id"] == "developer_2":  # Backend
            analysis = f"For '{task_title}', I'll handle the server-side logic and data management. "
            if 'authentication' in task_description.lower() or 'login' in task_description.lower():
                analysis += "This requires secure authentication implementation with JWT tokens. "
            if 'integration' in task_description.lower() or 'api' in task_description.lower():
                analysis += "Third-party API integration and error handling are key. "
            if 'payment' in task_description.lower():
                analysis += "PCI DSS compliance and secure payment processing are critical. "

            concerns = [
                "Data security and encryption for sensitive information",
                "API performance under high concurrent load",
                "Database query optimization and connection pooling",
                "Third-party service reliability and timeout handling",
                "Data validation and sanitization vulnerabilities",
                "Scalability bottlenecks in business logic processing",
                "Error handling and logging for debugging production issues",
                "Data backup and recovery procedures",
                "API rate limiting and abuse prevention"
            ]

            recommendations = [
                "Implement robust authentication and authorization with JWT/OAuth2",
                "Design normalized database schema with proper indexing strategy",
                "Set up comprehensive input validation and sanitization",
                "Implement API versioning and backward compatibility",
                "Create detailed API documentation with request/response examples",
                "Set up database migrations and version control",
                "Implement caching strategy with Redis for frequently accessed data",
                "Create comprehensive error handling with proper HTTP status codes",
                "Set up monitoring and alerting for API performance and errors",
                "Implement automated backup procedures and disaster recovery plan"
            ]

            effort = "1-2 weeks for backend development"
            next_steps = ["Database setup", "API endpoint creation"]

        elif agent["id"] == "qa_engineer":
            analysis = f"For '{task_title}', I need to develop comprehensive testing strategies. "
            if 'payment' in task_description.lower() or 'security' in task_description.lower():
                analysis += "Security testing and payment flow validation are critical. "
            if 'performance' in task_description.lower() or 'load' in task_description.lower():
                analysis += "Performance and load testing will be essential. "
            if 'mobile' in task_description.lower():
                analysis += "Cross-device testing and mobile-specific scenarios are required. "

            concerns = [
                "Insufficient test coverage for critical user paths",
                "Edge cases and error scenarios not properly tested",
                "Performance degradation under realistic load conditions",
                "Security vulnerabilities in authentication and data handling",
                "Cross-browser and cross-device compatibility issues",
                "Data integrity and consistency in concurrent operations",
                "Regression testing gaps when new features are added",
                "Test environment differences from production setup",
                "Accessibility compliance testing coverage"
            ]

            recommendations = [
                "Develop comprehensive test automation suite with multiple test levels",
                "Create detailed test cases covering happy path, edge cases, and error scenarios",
                "Implement performance testing with realistic data volumes and user loads",
                "Set up security testing including penetration testing and vulnerability scans",
                "Establish cross-browser testing matrix with automated visual regression tests",
                "Create data-driven tests to validate business logic with various inputs",
                "Implement continuous integration with automated test execution",
                "Set up test data management and database seeding for consistent testing",
                "Create accessibility testing checklist and automated a11y tests",
                "Establish bug triage process and defect tracking workflows"
            ]

            effort = "3-5 days for testing setup"
            next_steps = ["Test plan creation", "Automation framework setup"]

        elif agent["id"] == "manager":
            analysis = f"For '{task_title}' with {task_priority} priority, I need to coordinate team efforts and manage timeline. "
            if task_priority == 'high' or task_priority == 'critical':
                analysis += "Given the high priority, we need dedicated resources and clear milestones. "
            if 'integration' in task_description.lower():
                analysis += "Cross-team coordination and dependency management are crucial. "

            concerns = [
                "Timeline slippage due to underestimated complexity",
                "Resource conflicts with other concurrent projects",
                "Scope creep from stakeholder requests during development",
                "Team communication gaps leading to misaligned expectations",
                "External dependencies causing project delays",
                "Quality vs. speed trade-offs under tight deadlines",
                "Risk management and contingency planning gaps",
                "Stakeholder availability for reviews and approvals",
                "Budget overruns from extended development time"
            ]

            recommendations = [
                "Create detailed project timeline with buffer time for unexpected issues",
                "Establish clear communication channels and regular check-in meetings",
                "Implement agile methodology with sprint planning and retrospectives",
                "Set up project tracking tools with real-time progress visibility",
                "Define clear roles and responsibilities for all team members",
                "Create risk register with mitigation strategies for identified risks",
                "Establish change management process for scope modifications",
                "Schedule regular stakeholder reviews and feedback sessions",
                "Set up automated reporting for project metrics and KPIs",
                "Plan for knowledge transfer and documentation handover"
            ]

            effort = "1-2 days for project planning"
            next_steps = ["Team coordination", "Progress tracking setup"]

        else:
            # Generic fallback
            analysis = f"Analysis for '{task_title}' from {agent['role']} perspective."
            concerns = ["General considerations"]
            recommendations = ["Standard approach"]
            effort = "TBD"
            next_steps = ["Further analysis needed"]

        return AgentResponse(
            agent_id=agent["id"],
            role=agent["role"],
            timestamp=datetime.now(),
            response=analysis,
            recommendations=recommendations,
            concerns=concerns,
            next_steps=next_steps,
            estimated_effort=effort
        )

# Make this importable by other modules
def create_sequential_pipeline(team_config_path: str = "ai_dev_team_config.json"):
    """Factory function to create a sequential pipeline instance"""
    return SequentialPipeline(team_config_path)

# Example usage
async def main():
    pipeline = SequentialPipeline()

    task = {
        "task_id": "STORY-123",
        "title": "User Authentication System",
        "description": "Implement secure user login and registration",
        "priority": "high"
    }

    print("🚀 Starting Sequential Pipeline Processing...")
    responses = await pipeline.process_task(task)

    print("\n📊 Pipeline Results:")
    for response in responses:
        print(f"\n{response.role}:")
        print(f"  Effort: {response.estimated_effort}")
        print(f"  Key Concerns: {', '.join(response.concerns)}")

if __name__ == "__main__":
    asyncio.run(main())
