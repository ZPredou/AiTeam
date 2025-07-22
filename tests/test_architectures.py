#!/usr/bin/env python3
"""
Simple test script for the multi-agent architectures
"""

import asyncio
from agent_architecture_manager import AgentArchitectureManager

async def test_sequential():
    """Test the sequential pipeline"""
    print("🔄 Testing Sequential Pipeline...")
    
    manager = AgentArchitectureManager()
    manager.set_architecture("sequential")
    
    task = {
        "task_id": "TEST-001",
        "title": "User Login System",
        "description": "Create secure user authentication with JWT tokens",
        "priority": "high"
    }
    
    result = await manager.process_task(task)
    
    print(f"✅ Completed in {result.processing_time:.2f}s")
    print(f"📊 {len(result.results)} agents responded")
    
    # Show first few responses
    for i, response in enumerate(result.results[:3], 1):
        print(f"  {i}. {response.role}: {response.response[:100]}...")
    
    return result

async def test_round_table():
    """Test the round table discussion"""
    print("\n🗣️ Testing Round Table Discussion...")
    
    manager = AgentArchitectureManager()
    manager.set_architecture("round_table")
    
    task = {
        "task_id": "TEST-002", 
        "title": "API Rate Limiting",
        "description": "Implement Redis-based rate limiting for REST endpoints",
        "priority": "medium"
    }
    
    result = await manager.process_task(task)
    
    print(f"✅ Completed in {result.processing_time:.2f}s")
    print(f"📊 {len(result.results)} discussion rounds")
    
    # Show round summaries
    for round_data in result.results:
        print(f"  Round {round_data.round_number}: {round_data.topic}")
        print(f"    Consensus: {len(round_data.consensus_items)} items")
    
    return result

async def test_reactive():
    """Test the reactive system"""
    print("\n⚡ Testing Reactive System...")
    
    manager = AgentArchitectureManager()
    manager.set_architecture("reactive")
    
    task = {
        "task_id": "TEST-003",
        "title": "Payment Integration", 
        "description": "Add Stripe payment processing with webhooks",
        "priority": "critical"
    }
    
    result = await manager.process_task(task)
    
    print(f"✅ Completed in {result.processing_time:.2f}s")
    print(f"📊 {len(result.results)} events processed")
    
    # Show event types
    event_types = set(e.event_type.value for e in result.results)
    print(f"  Event types: {', '.join(event_types)}")
    
    return result

async def test_architecture_switching():
    """Test switching between architectures"""
    print("\n🔄 Testing Architecture Switching...")
    
    manager = AgentArchitectureManager()
    
    # Test switching
    architectures = ["sequential", "round_table", "reactive"]
    
    for arch in architectures:
        success = manager.set_architecture(arch)
        current = manager.get_current_architecture()
        print(f"  {arch}: {'✅' if success and current == arch else '❌'}")
    
    return True

async def main():
    """Run all tests"""
    print("🧪 TESTING MULTI-AGENT ARCHITECTURES")
    print("=" * 50)
    
    try:
        # Test individual architectures
        seq_result = await test_sequential()
        rt_result = await test_round_table()
        reactive_result = await test_reactive()
        
        # Test switching
        await test_architecture_switching()
        
        print("\n📈 PERFORMANCE SUMMARY")
        print("=" * 50)
        print(f"Sequential:  {seq_result.processing_time:.2f}s")
        print(f"Round Table: {rt_result.processing_time:.2f}s") 
        print(f"Reactive:    {reactive_result.processing_time:.2f}s")
        
        print("\n🎉 ALL TESTS PASSED!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
