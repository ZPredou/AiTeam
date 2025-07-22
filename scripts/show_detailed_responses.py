#!/usr/bin/env python3
"""
Show detailed agent responses with full concerns and recommendations
"""

import asyncio
from agent_architecture_manager import AgentArchitectureManager

async def show_detailed_responses():
    """Show the full detailed responses from each agent"""
    
    print("🔍 DETAILED AGENT RESPONSES")
    print("=" * 80)
    
    manager = AgentArchitectureManager()
    manager.set_architecture("sequential")
    
    task = {
        "task_id": "DETAIL-001",
        "title": "E-commerce Payment Integration",
        "description": "Integrate Stripe payment API with user authentication, mobile checkout flow, and real-time dashboard analytics",
        "priority": "critical"
    }
    
    print(f"📋 Task: {task['title']}")
    print(f"📝 Description: {task['description']}")
    print(f"🚨 Priority: {task['priority']}")
    print("\n" + "=" * 80)
    
    result = await manager.process_task(task)
    
    for i, response in enumerate(result.results, 1):
        print(f"\n{i}. {response.role.upper()}")
        print("=" * 60)
        
        print(f"📝 ANALYSIS:")
        print(f"   {response.response}")
        
        print(f"\n⏱️  ESTIMATED EFFORT:")
        print(f"   {response.estimated_effort}")
        
        print(f"\n⚠️  CONCERNS ({len(response.concerns)} items):")
        for j, concern in enumerate(response.concerns, 1):
            print(f"   {j}. {concern}")
        
        print(f"\n💡 RECOMMENDATIONS ({len(response.recommendations)} items):")
        for j, rec in enumerate(response.recommendations, 1):
            print(f"   {j}. {rec}")
        
        print(f"\n🎯 NEXT STEPS:")
        for j, step in enumerate(response.next_steps, 1):
            print(f"   {j}. {step}")
        
        print("\n" + "-" * 60)
    
    print(f"\n🎉 SUMMARY")
    print("=" * 80)
    print(f"✅ Total agents: {len(result.results)}")
    print(f"✅ Total concerns: {sum(len(r.concerns) for r in result.results)}")
    print(f"✅ Total recommendations: {sum(len(r.recommendations) for r in result.results)}")
    print(f"✅ Processing time: {result.processing_time:.2f}s")
    
    print(f"\n💡 Each agent now provides:")
    print("   • Contextual analysis based on the specific task")
    print("   • 7-9 detailed concerns relevant to their role")
    print("   • 8-10 actionable recommendations")
    print("   • Professional effort estimates")
    print("   • Clear next steps")

if __name__ == "__main__":
    asyncio.run(show_detailed_responses())
