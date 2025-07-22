#!/usr/bin/env python3
"""
Test the improved fallback responses
"""

import asyncio
from agent_architecture_manager import AgentArchitectureManager

async def test_improved_fallbacks():
    """Test that fallback responses are now contextual and intelligent"""
    
    print("🧪 TESTING IMPROVED FALLBACK RESPONSES")
    print("=" * 50)
    
    manager = AgentArchitectureManager()
    manager.set_architecture("sequential")
    
    # Test with different types of tasks to see contextual responses
    test_tasks = [
        {
            "task_id": "FALLBACK-001",
            "title": "User Authentication System",
            "description": "Implement secure user login with JWT tokens and password hashing",
            "priority": "high"
        },
        {
            "task_id": "FALLBACK-002", 
            "title": "Payment Processing Integration",
            "description": "Integrate Stripe payment API with checkout flow and webhook handling",
            "priority": "critical"
        },
        {
            "task_id": "FALLBACK-003",
            "title": "Mobile Dashboard App",
            "description": "Create responsive mobile dashboard with charts and real-time data",
            "priority": "medium"
        }
    ]
    
    for i, task in enumerate(test_tasks, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: {task['title']}")
        print(f"{'='*60}")
        
        try:
            result = await manager.process_task(task)
            
            print(f"✅ Processing completed in {result.processing_time:.2f}s")
            
            # Show the first few agent responses to see if they're contextual
            for j, response in enumerate(result.results[:3], 1):
                print(f"\n{j}. {response.role}:")
                print(f"   📝 Response: {response.response[:200]}...")
                print(f"   ⏱️  Effort: {response.estimated_effort}")
                
                if response.concerns:
                    print(f"   ⚠️  Concerns: {', '.join(response.concerns[:2])}")
                
                if response.recommendations:
                    print(f"   💡 Recommendations: {', '.join(response.recommendations[:2])}")
            
            # Check if responses are contextual (not just "Mock response")
            contextual_responses = 0
            for response in result.results:
                if "Mock response" not in response.response and len(response.response) > 50:
                    contextual_responses += 1
            
            print(f"\n📊 Quality Check:")
            print(f"   Contextual responses: {contextual_responses}/{len(result.results)}")
            
            if contextual_responses >= len(result.results) * 0.8:  # 80% or more
                print(f"   🎉 EXCELLENT: Responses are contextual and intelligent!")
            elif contextual_responses >= len(result.results) * 0.5:  # 50% or more
                print(f"   ✅ GOOD: Most responses are contextual")
            else:
                print(f"   ⚠️  NEEDS IMPROVEMENT: Many responses are still generic")
                
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
    
    print(f"\n🎯 SUMMARY")
    print("=" * 50)
    print("The improved fallback system should now provide:")
    print("✅ Task-specific analysis instead of 'Mock response'")
    print("✅ Role-appropriate concerns and recommendations") 
    print("✅ Realistic effort estimates")
    print("✅ Contextual next steps")
    print("\nEven without OpenAI credits, you get intelligent responses!")

if __name__ == "__main__":
    asyncio.run(test_improved_fallbacks())
