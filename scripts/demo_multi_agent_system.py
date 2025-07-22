#!/usr/bin/env python3
"""
Demo script to test the Multi-Agent System

This script demonstrates how to use the different agent architectures
and shows the results of processing tasks with different approaches.
"""

import asyncio
import json
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.agent_architecture_manager import AgentArchitectureManager

async def demo_sequential_pipeline():
    """Demo the sequential pipeline architecture"""
    print("\n" + "="*60)
    print("🔄 SEQUENTIAL PIPELINE DEMO")
    print("="*60)
    
    manager = AgentArchitectureManager()
    manager.set_architecture("sequential")
    
    task = {
        "task_id": "DEMO-SEQ-001",
        "title": "User Authentication System",
        "description": "Implement secure user login with JWT tokens and password hashing",
        "priority": "high"
    }
    
    result = await manager.process_task(task)
    
    print(f"✅ Processing completed in {result.processing_time:.2f}s")
    print(f"📊 Agents involved: {result.metadata.get('agents_involved', 0)}")
    
    if hasattr(result.results, '__iter__'):
        for i, response in enumerate(result.results, 1):
            print(f"\n{i}. {response.role}:")
            print(f"   Effort: {response.estimated_effort}")
            print(f"   Key concerns: {', '.join(response.concerns[:2])}")

async def demo_round_table_discussion():
    """Demo the round table discussion architecture"""
    print("\n" + "="*60)
    print("🗣️  ROUND TABLE DISCUSSION DEMO")
    print("="*60)
    
    manager = AgentArchitectureManager()
    manager.set_architecture("round_table")
    
    task = {
        "task_id": "DEMO-RT-001", 
        "title": "Real-time Chat Feature",
        "description": "Add WebSocket-based real-time messaging with message history",
        "priority": "medium"
    }
    
    result = await manager.process_task(task)
    
    print(f"✅ Discussion completed in {result.processing_time:.2f}s")
    print(f"📊 Rounds: {result.metadata.get('discussion_rounds', 0)}")
    print(f"📊 Total contributions: {result.metadata.get('total_contributions', 0)}")
    
    if hasattr(result.results, '__iter__'):
        for round_data in result.results:
            print(f"\nRound {round_data.round_number}: {round_data.topic}")
            print(f"   Consensus: {len(round_data.consensus_items)} items")
            print(f"   Unresolved: {len(round_data.unresolved_items)} items")

async def demo_reactive_system():
    """Demo the reactive event-driven architecture"""
    print("\n" + "="*60)
    print("⚡ REACTIVE SYSTEM DEMO")
    print("="*60)
    
    manager = AgentArchitectureManager()
    manager.set_architecture("reactive")
    
    task = {
        "task_id": "DEMO-REACT-001",
        "title": "Payment Processing Integration", 
        "description": "Integrate Stripe payment API with webhook handling",
        "priority": "critical"
    }
    
    result = await manager.process_task(task)
    
    print(f"✅ Event processing completed in {result.processing_time:.2f}s")
    print(f"📊 Total events: {result.metadata.get('total_events', 0)}")
    print(f"📊 Event types: {', '.join(result.metadata.get('event_types', []))}")

async def demo_architecture_comparison():
    """Compare performance across different architectures"""
    print("\n" + "="*60)
    print("📈 ARCHITECTURE COMPARISON")
    print("="*60)
    
    manager = AgentArchitectureManager()
    
    # Test task
    task = {
        "task_id": "DEMO-COMP-001",
        "title": "API Rate Limiting System",
        "description": "Implement Redis-based rate limiting for REST API endpoints",
        "priority": "medium"
    }
    
    architectures = ["sequential", "round_table", "reactive"]
    results = {}
    
    for arch in architectures:
        print(f"\n🔄 Testing {arch} architecture...")
        manager.set_architecture(arch)
        result = await manager.process_task(task)
        results[arch] = result.processing_time
        print(f"   Completed in {result.processing_time:.2f}s")
    
    # Show comparison
    print(f"\n📊 Performance Comparison:")
    for arch, time in results.items():
        print(f"   {arch:12}: {time:.2f}s")
    
    # Show detailed performance data
    performance_data = manager.compare_architectures_performance()
    print(f"\n📈 Detailed Performance Data:")
    for arch, metrics in performance_data.items():
        print(f"   {arch:12}: {metrics['count']} runs, avg {metrics['avg_time']:.2f}s")

async def demo_export_functionality():
    """Demo the export functionality"""
    print("\n" + "="*60)
    print("📄 EXPORT FUNCTIONALITY DEMO")
    print("="*60)
    
    manager = AgentArchitectureManager()
    manager.set_architecture("sequential")
    
    task = {
        "task_id": "DEMO-EXPORT-001",
        "title": "Database Migration Tool",
        "description": "Create tool to migrate data between PostgreSQL versions",
        "priority": "low"
    }
    
    result = await manager.process_task(task)
    
    # Export as JSON
    json_export = manager.export_results(result, "json")
    print("📄 JSON Export (first 200 chars):")
    print(json_export[:200] + "...")
    
    # Export as Markdown
    markdown_export = manager.export_results(result, "markdown")
    print("\n📄 Markdown Export (first 300 chars):")
    print(markdown_export[:300] + "...")

def show_system_info():
    """Show information about the multi-agent system"""
    print("🤖 AI MULTI-AGENT SYSTEM DEMO")
    print("="*60)
    
    manager = AgentArchitectureManager()
    
    print("🏗️  Available Architectures:")
    for arch, desc in manager.list_available_architectures().items():
        print(f"   {arch:12}: {desc}")
    
    print(f"\n👥 Team Configuration:")
    print(f"   Team: {manager.team_config['team_name']}")
    print(f"   Members: {len(manager.team_config['members'])}")
    
    for member in manager.team_config['members']:
        print(f"   - {member['role']} ({member['id']})")

async def interactive_demo():
    """Interactive demo allowing user to choose architecture and task"""
    print("\n" + "="*60)
    print("🎮 INTERACTIVE DEMO")
    print("="*60)
    
    manager = AgentArchitectureManager()
    
    # Show available architectures
    architectures = list(manager.list_available_architectures().keys())
    print("Available architectures:")
    for i, arch in enumerate(architectures, 1):
        print(f"   {i}. {arch}")
    
    # Get user choice (simulated for demo)
    choice = 1  # Default to sequential
    selected_arch = architectures[choice - 1]
    
    print(f"\n🔄 Selected: {selected_arch}")
    manager.set_architecture(selected_arch)
    
    # Sample tasks
    tasks = [
        {
            "task_id": "INT-001",
            "title": "User Profile Management",
            "description": "CRUD operations for user profiles with image upload",
            "priority": "medium"
        },
        {
            "task_id": "INT-002", 
            "title": "Email Notification System",
            "description": "Async email sending with templates and queuing",
            "priority": "high"
        }
    ]
    
    for task in tasks:
        print(f"\n📋 Processing: {task['title']}")
        result = await manager.process_task(task)
        print(f"   ✅ Completed in {result.processing_time:.2f}s")

async def main():
    """Run all demos"""
    show_system_info()
    
    # Run individual architecture demos
    await demo_sequential_pipeline()
    await demo_round_table_discussion() 
    await demo_reactive_system()
    
    # Run comparison and export demos
    await demo_architecture_comparison()
    await demo_export_functionality()
    
    # Interactive demo
    await interactive_demo()
    
    print("\n" + "="*60)
    print("🎉 DEMO COMPLETE!")
    print("="*60)
    print("Next steps:")
    print("1. Start the multi-agent API: python multi_agent_api.py")
    print("2. Open the web interface: ai_backlog_viewer/index.html")
    print("3. Try different architectures with your own tasks!")

if __name__ == "__main__":
    asyncio.run(main())
