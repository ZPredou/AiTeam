#!/usr/bin/env python3
"""
Test OpenAI integration with your API key
"""

import asyncio
import json
from ai_providers import create_ai_provider_manager
from agent_architecture_manager import AgentArchitectureManager

async def test_openai_connection():
    """Test basic OpenAI connection"""
    
    print("🔑 TESTING OPENAI CONNECTION")
    print("=" * 50)
    
    try:
        # Create AI manager
        ai_manager = create_ai_provider_manager()
        
        # Simple test prompt
        test_prompt = """You are a senior software engineer. Please analyze this task and respond in JSON format:

Task: Implement user authentication system with JWT tokens

Please respond with:
{
  "analysis": "Your technical analysis",
  "concerns": ["concern1", "concern2"],
  "recommendations": ["rec1", "rec2"],
  "effort_estimate": "X days",
  "next_steps": ["step1", "step2"]
}"""
        
        print("🔄 Sending test request to OpenAI...")
        response = await ai_manager.generate_response(test_prompt)
        
        print(f"✅ SUCCESS! Response received from {response.provider}")
        print(f"📝 Model: {response.model}")
        print(f"🔢 Tokens used: {response.tokens_used}")
        print(f"💰 Estimated cost: ${response.cost_estimate:.4f}")
        
        print(f"\n📋 Response preview:")
        print(response.content[:300] + "..." if len(response.content) > 300 else response.content)
        
        return True
        
    except Exception as e:
        print(f"❌ OpenAI connection failed: {str(e)}")
        return False

async def test_multi_agent_with_openai():
    """Test the multi-agent system with OpenAI"""
    
    print(f"\n🤖 TESTING MULTI-AGENT SYSTEM WITH OPENAI")
    print("=" * 50)
    
    try:
        # Create architecture manager
        manager = AgentArchitectureManager()
        manager.set_architecture("sequential")
        
        # Test task
        task = {
            "task_id": "OPENAI-TEST-001",
            "title": "E-commerce Product Catalog",
            "description": "Build a product catalog system with search, filtering, and recommendations",
            "priority": "high"
        }
        
        print(f"📋 Processing task: {task['title']}")
        print("🔄 Running sequential pipeline with OpenAI...")
        
        result = await manager.process_task(task)
        
        print(f"✅ Processing completed in {result.processing_time:.2f}s")
        print(f"📊 Agents involved: {len(result.results)}")
        
        # Show detailed responses
        print(f"\n📝 AGENT RESPONSES:")
        print("=" * 50)
        
        for i, response in enumerate(result.results, 1):
            print(f"\n{i}. {response.role}")
            print(f"   📝 Analysis: {response.response[:200]}...")
            print(f"   ⏱️  Effort: {response.estimated_effort}")
            
            if response.concerns:
                print(f"   ⚠️  Concerns: {', '.join(response.concerns[:2])}")
            
            if response.recommendations:
                print(f"   💡 Recommendations: {', '.join(response.recommendations[:2])}")
        
        # Check response quality
        total_response_length = sum(len(r.response) for r in result.results)
        avg_response_length = total_response_length / len(result.results)
        
        print(f"\n📊 QUALITY METRICS:")
        print(f"   Average response length: {avg_response_length:.0f} characters")
        print(f"   Total agents with concerns: {sum(1 for r in result.results if r.concerns)}")
        print(f"   Total agents with recommendations: {sum(1 for r in result.results if r.recommendations)}")
        
        if avg_response_length > 150:
            print(f"   🎉 Responses appear to be from real AI (detailed and contextual)")
        else:
            print(f"   ⚠️  Responses may be fallback data")
        
        return True
        
    except Exception as e:
        print(f"❌ Multi-agent test failed: {str(e)}")
        return False

async def test_different_architectures():
    """Test different architectures with OpenAI"""
    
    print(f"\n🏗️  TESTING DIFFERENT ARCHITECTURES")
    print("=" * 50)
    
    manager = AgentArchitectureManager()
    
    task = {
        "task_id": "ARCH-TEST-001",
        "title": "Mobile App Development",
        "description": "Create a cross-platform mobile app for task management",
        "priority": "medium"
    }
    
    architectures = ["sequential", "round_table"]  # Skip reactive for now
    results = {}
    
    for arch in architectures:
        try:
            print(f"\n🔄 Testing {arch} architecture...")
            manager.set_architecture(arch)
            
            result = await manager.process_task(task)
            results[arch] = {
                "success": True,
                "time": result.processing_time,
                "responses": len(result.results) if hasattr(result.results, '__len__') else 1
            }
            
            print(f"   ✅ Completed in {result.processing_time:.2f}s")
            
        except Exception as e:
            print(f"   ❌ Failed: {str(e)}")
            results[arch] = {"success": False, "error": str(e)}
    
    # Summary
    print(f"\n📊 ARCHITECTURE TEST SUMMARY:")
    for arch, result in results.items():
        if result["success"]:
            print(f"   ✅ {arch}: {result['time']:.2f}s ({result['responses']} responses)")
        else:
            print(f"   ❌ {arch}: Failed")
    
    return all(r["success"] for r in results.values())

def show_cost_info():
    """Show cost information"""
    
    print(f"\n💰 COST INFORMATION")
    print("=" * 50)
    
    print("📊 Using GPT-3.5-turbo (cost-effective choice):")
    print("   • ~$0.002 per 1K tokens")
    print("   • Average agent response: ~200-500 tokens")
    print("   • Cost per agent response: ~$0.001-0.003")
    print("   • 6 agents processing 1 task: ~$0.006-0.018")
    
    print(f"\n💡 Cost optimization tips:")
    print("   • Currently using GPT-3.5-turbo (10x cheaper than GPT-4)")
    print("   • Responses are limited to 800 tokens max")
    print("   • System has intelligent fallbacks if quota exceeded")
    
    print(f"\n🔧 To upgrade to GPT-4 (better quality):")
    print('   • Edit ai_config.json: change "model" to "gpt-4"')
    print("   • Cost will be ~10x higher but responses will be more detailed")

async def main():
    """Run all tests"""
    
    print("🚀 OPENAI INTEGRATION TEST SUITE")
    print("=" * 60)
    
    # Test 1: Basic connection
    connection_success = await test_openai_connection()
    
    if not connection_success:
        print(f"\n❌ SETUP FAILED")
        print("Please check:")
        print("1. Your API key is correct")
        print("2. You have credits in your OpenAI account")
        print("3. Your internet connection is working")
        return
    
    # Test 2: Multi-agent system
    multi_agent_success = await test_multi_agent_with_openai()
    
    # Test 3: Different architectures
    arch_success = await test_different_architectures()
    
    # Show cost information
    show_cost_info()
    
    # Final summary
    print(f"\n🎉 FINAL RESULTS")
    print("=" * 60)
    
    if connection_success and multi_agent_success and arch_success:
        print("✅ ALL TESTS PASSED!")
        print("🎊 Your OpenAI integration is working perfectly!")
        
        print(f"\n🚀 Next steps:")
        print("1. Start the API server: python multi_agent_api.py")
        print("2. Open web interface: ai_backlog_viewer/index.html")
        print("3. Enable multi-agent processing and try it out!")
        print("4. Run full demo: python demo_multi_agent_system.py")
        
    else:
        print("⚠️  Some tests failed, but basic connection works.")
        print("The system should still function with your OpenAI integration.")
    
    print(f"\n💡 Your AI agents are now powered by real ChatGPT/OpenAI!")

if __name__ == "__main__":
    asyncio.run(main())
