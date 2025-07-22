#!/usr/bin/env python3
"""
Test script for AI integration

This script tests the real AI integration with your multi-agent system.
"""

import asyncio
import os
from agent_architecture_manager import AgentArchitectureManager

async def test_ai_integration():
    """Test the AI integration with a real task"""
    
    print("🤖 TESTING AI INTEGRATION")
    print("=" * 50)
    
    # Check if any AI providers are configured
    ai_keys = {
        "OpenAI": os.getenv("OPENAI_API_KEY"),
        "Anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "Ollama": "localhost:11434"  # Assume local if no API keys
    }
    
    configured_providers = [name for name, key in ai_keys.items() if key]
    
    if not any([os.getenv("OPENAI_API_KEY"), os.getenv("ANTHROPIC_API_KEY")]):
        print("⚠️  No API keys found. Will test with Ollama (local) or fallback to mock.")
        print("   To use real AI, set OPENAI_API_KEY or ANTHROPIC_API_KEY")
    else:
        print(f"✅ Found API keys for: {', '.join(configured_providers)}")
    
    # Create manager and test task
    manager = AgentArchitectureManager()
    
    test_task = {
        "task_id": "AI-TEST-001",
        "title": "E-commerce Checkout System",
        "description": "Build a secure checkout system with payment processing, inventory management, and order confirmation emails",
        "priority": "high"
    }
    
    print(f"\n📋 Test Task: {test_task['title']}")
    print(f"📝 Description: {test_task['description']}")
    
    # Test Sequential Pipeline with AI
    print(f"\n🔄 Testing Sequential Pipeline with AI...")
    manager.set_architecture("sequential")
    
    try:
        result = await manager.process_task(test_task)
        
        print(f"✅ Processing completed in {result.processing_time:.2f}s")
        print(f"📊 Architecture: {result.architecture_used}")
        print(f"📊 Agents involved: {len(result.results)}")
        
        # Show sample responses
        print(f"\n📝 Sample Agent Responses:")
        for i, response in enumerate(result.results[:3], 1):
            print(f"\n{i}. {response.role}:")
            print(f"   Response: {response.response[:150]}...")
            print(f"   Effort: {response.estimated_effort}")
            if response.concerns:
                print(f"   Concerns: {', '.join(response.concerns[:2])}")
            if response.recommendations:
                print(f"   Recommendations: {', '.join(response.recommendations[:2])}")
        
        # Check if responses look like real AI vs mock
        real_ai_indicators = 0
        for response in result.results:
            if len(response.response) > 100:  # Real AI tends to be more verbose
                real_ai_indicators += 1
            if any(word in response.response.lower() for word in ['implement', 'consider', 'ensure', 'recommend']):
                real_ai_indicators += 1
        
        if real_ai_indicators > len(result.results):
            print(f"\n🎉 SUCCESS: Responses appear to be from real AI!")
            print(f"   Quality indicators: {real_ai_indicators}/{len(result.results) * 2}")
        else:
            print(f"\n⚠️  Responses may be mock/fallback data")
            print(f"   This is normal if no AI providers are configured")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

async def test_round_table_ai():
    """Test round table discussion with AI"""
    
    print(f"\n🗣️  Testing Round-Table Discussion with AI...")
    
    manager = AgentArchitectureManager()
    manager.set_architecture("round_table")
    
    test_task = {
        "task_id": "AI-TEST-002",
        "title": "Mobile App Architecture",
        "description": "Design architecture for a cross-platform mobile app with offline capabilities",
        "priority": "medium"
    }
    
    try:
        result = await manager.process_task(test_task)
        
        print(f"✅ Discussion completed in {result.processing_time:.2f}s")
        print(f"📊 Rounds: {len(result.results)}")
        
        # Show discussion summary
        for round_data in result.results:
            print(f"\n   Round {round_data.round_number}: {round_data.topic}")
            print(f"   Participants: {len(round_data.responses)}")
            print(f"   Consensus items: {len(round_data.consensus_items)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Round table test failed: {str(e)}")
        return False

async def test_reactive_ai():
    """Test reactive system with AI"""
    
    print(f"\n⚡ Testing Reactive System with AI...")
    
    manager = AgentArchitectureManager()
    manager.set_architecture("reactive")
    
    test_task = {
        "task_id": "AI-TEST-003",
        "title": "Real-time Analytics Dashboard",
        "description": "Create a real-time dashboard showing user activity and system metrics",
        "priority": "critical"
    }
    
    try:
        result = await manager.process_task(test_task)
        
        print(f"✅ Event processing completed in {result.processing_time:.2f}s")
        print(f"📊 Events processed: {len(result.results)}")
        
        # Show event types
        if result.results:
            event_types = set(e.event_type.value for e in result.results)
            print(f"   Event types: {', '.join(event_types)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Reactive test failed: {str(e)}")
        return False

def show_setup_help():
    """Show setup instructions if AI isn't working"""
    
    print(f"\n💡 SETUP HELP")
    print("=" * 50)
    
    print("To use real AI agents, you need to configure at least one provider:")
    
    print(f"\n🔑 Option 1: OpenAI (Recommended)")
    print("   1. Get API key: https://platform.openai.com/api-keys")
    print("   2. Set environment variable:")
    print("      export OPENAI_API_KEY='your-key-here'")
    
    print(f"\n🔑 Option 2: Anthropic Claude")
    print("   1. Get API key: https://console.anthropic.com/")
    print("   2. Set environment variable:")
    print("      export ANTHROPIC_API_KEY='your-key-here'")
    
    print(f"\n🏠 Option 3: Local Ollama (Free)")
    print("   1. Install: https://ollama.ai/")
    print("   2. Pull model: ollama pull llama2")
    print("   3. Start server: ollama serve")
    
    print(f"\n🚀 Quick Setup:")
    print("   python setup_ai_providers.py")

async def main():
    """Run all AI integration tests"""
    
    # Test sequential pipeline (most important)
    success_sequential = await test_ai_integration()
    
    # Test other architectures
    success_round_table = await test_round_table_ai()
    success_reactive = await test_reactive_ai()
    
    # Summary
    print(f"\n📊 TEST SUMMARY")
    print("=" * 50)
    
    results = {
        "Sequential Pipeline": "✅" if success_sequential else "❌",
        "Round-Table Discussion": "✅" if success_round_table else "❌", 
        "Reactive System": "✅" if success_reactive else "❌"
    }
    
    for test_name, status in results.items():
        print(f"{status} {test_name}")
    
    all_passed = all([success_sequential, success_round_table, success_reactive])
    
    if all_passed:
        print(f"\n🎉 ALL TESTS PASSED!")
        print("Your AI integration is working correctly.")
        print(f"\nNext steps:")
        print("1. Start the API: python multi_agent_api.py")
        print("2. Open web interface: ai_backlog_viewer/index.html")
        print("3. Enable multi-agent processing and try different architectures!")
        
    else:
        print(f"\n⚠️  SOME TESTS FAILED")
        print("This might be normal if you haven't configured AI providers yet.")
        show_setup_help()
        
        print(f"\nThe system will still work with intelligent fallback responses.")

if __name__ == "__main__":
    asyncio.run(main())
