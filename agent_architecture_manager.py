#!/usr/bin/env python3
"""
Agent Architecture Manager - Unified system for switching between different AI agent interaction patterns

This manager allows you to easily switch between:
1. Sequential Pipeline
2. Round-Table Discussion  
3. Event-Driven Reactive
4. Hierarchical Decision Tree (when implemented)

Usage:
    manager = AgentArchitectureManager()
    manager.set_architecture("sequential")  # or "round_table", "reactive", "hierarchical"
    results = await manager.process_task(task)
"""

import json
import asyncio
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

# Import the different architectures
from agent_architectures.sequential_pipeline import create_sequential_pipeline
from agent_architectures.round_table_discussion import create_round_table_discussion
from agent_architectures.event_driven_reactive import create_reactive_agent_system

class ArchitectureType(Enum):
    SEQUENTIAL = "sequential"
    ROUND_TABLE = "round_table"
    REACTIVE = "reactive"
    HIERARCHICAL = "hierarchical"  # For future implementation

@dataclass
class ProcessingResult:
    architecture_used: str
    task: Dict[str, Any]
    results: Any
    processing_time: float
    timestamp: datetime
    metadata: Dict[str, Any]

class AgentArchitectureManager:
    def __init__(self, team_config_path: str = "ai_dev_team_config.json"):
        self.team_config_path = team_config_path
        self.current_architecture = ArchitectureType.SEQUENTIAL  # Default
        self.architecture_instances = {}
        self.processing_history: List[ProcessingResult] = []
        
        # Load team configuration
        with open(team_config_path) as f:
            self.team_config = json.load(f)
    
    def set_architecture(self, architecture: str) -> bool:
        """Set the active architecture type"""
        try:
            arch_type = ArchitectureType(architecture.lower())
            self.current_architecture = arch_type
            print(f"🔄 Architecture set to: {arch_type.value}")
            return True
        except ValueError:
            available = [arch.value for arch in ArchitectureType]
            print(f"❌ Invalid architecture. Available: {', '.join(available)}")
            return False
    
    def get_current_architecture(self) -> str:
        """Get the currently active architecture"""
        return self.current_architecture.value
    
    def list_available_architectures(self) -> Dict[str, str]:
        """List all available architectures with descriptions"""
        return {
            "sequential": "Sequential Pipeline - Agents process task in order, building context",
            "round_table": "Round-Table Discussion - All agents participate in collaborative rounds",
            "reactive": "Event-Driven Reactive - Agents react to events and trigger others dynamically",
            "hierarchical": "Hierarchical Decision Tree - Bottom-up analysis, top-down decisions (Coming Soon)"
        }
    
    async def process_task(self, task: Dict[str, Any]) -> ProcessingResult:
        """Process a task using the currently selected architecture"""
        
        start_time = asyncio.get_event_loop().time()
        
        print(f"🚀 Processing task with {self.current_architecture.value} architecture")
        print(f"📋 Task: {task.get('title', 'Untitled')}")
        
        # Get or create architecture instance
        architecture_instance = await self._get_architecture_instance()
        
        # Process the task
        try:
            if self.current_architecture == ArchitectureType.SEQUENTIAL:
                results = await architecture_instance.process_task(task)
                
            elif self.current_architecture == ArchitectureType.ROUND_TABLE:
                results = await architecture_instance.facilitate_discussion(task)
                
            elif self.current_architecture == ArchitectureType.REACTIVE:
                results = await architecture_instance.process_task(task)
                
            elif self.current_architecture == ArchitectureType.HIERARCHICAL:
                # Future implementation
                raise NotImplementedError("Hierarchical architecture not yet implemented")
                
            else:
                raise ValueError(f"Unknown architecture: {self.current_architecture}")
                
        except Exception as e:
            print(f"❌ Error processing task: {str(e)}")
            raise
        
        end_time = asyncio.get_event_loop().time()
        processing_time = end_time - start_time
        
        # Create result object
        result = ProcessingResult(
            architecture_used=self.current_architecture.value,
            task=task,
            results=results,
            processing_time=processing_time,
            timestamp=datetime.now(),
            metadata=self._generate_metadata(results)
        )
        
        # Store in history
        self.processing_history.append(result)
        
        print(f"✅ Processing complete in {processing_time:.2f}s")
        return result
    
    async def _get_architecture_instance(self):
        """Get or create an instance of the current architecture"""
        
        arch_key = self.current_architecture.value
        
        if arch_key not in self.architecture_instances:
            if self.current_architecture == ArchitectureType.SEQUENTIAL:
                self.architecture_instances[arch_key] = create_sequential_pipeline(self.team_config_path)
                
            elif self.current_architecture == ArchitectureType.ROUND_TABLE:
                self.architecture_instances[arch_key] = create_round_table_discussion(self.team_config_path)
                
            elif self.current_architecture == ArchitectureType.REACTIVE:
                self.architecture_instances[arch_key] = create_reactive_agent_system(self.team_config_path)
                
            else:
                raise NotImplementedError(f"Architecture {arch_key} not implemented")
        
        return self.architecture_instances[arch_key]
    
    def _generate_metadata(self, results: Any) -> Dict[str, Any]:
        """Generate metadata about the processing results"""
        
        metadata = {
            "architecture": self.current_architecture.value,
            "team_size": len(self.team_config["members"])
        }
        
        # Architecture-specific metadata
        if self.current_architecture == ArchitectureType.SEQUENTIAL:
            metadata.update({
                "agents_involved": len(results) if isinstance(results, list) else 0,
                "pipeline_stages": len(results) if isinstance(results, list) else 0
            })
            
        elif self.current_architecture == ArchitectureType.ROUND_TABLE:
            metadata.update({
                "discussion_rounds": len(results) if isinstance(results, list) else 0,
                "total_contributions": sum(len(r.responses) for r in results) if isinstance(results, list) else 0
            })
            
        elif self.current_architecture == ArchitectureType.REACTIVE:
            metadata.update({
                "total_events": len(results) if isinstance(results, list) else 0,
                "event_types": list(set(e.event_type.value for e in results)) if isinstance(results, list) else []
            })
        
        return metadata
    
    def get_processing_history(self, limit: Optional[int] = None) -> List[ProcessingResult]:
        """Get processing history, optionally limited to recent entries"""
        history = self.processing_history
        if limit:
            history = history[-limit:]
        return history
    
    def compare_architectures_performance(self) -> Dict[str, Any]:
        """Compare performance metrics across different architectures"""
        
        if not self.processing_history:
            return {"message": "No processing history available"}
        
        performance_by_arch = {}
        
        for result in self.processing_history:
            arch = result.architecture_used
            if arch not in performance_by_arch:
                performance_by_arch[arch] = {
                    "count": 0,
                    "total_time": 0,
                    "avg_time": 0
                }
            
            performance_by_arch[arch]["count"] += 1
            performance_by_arch[arch]["total_time"] += result.processing_time
            performance_by_arch[arch]["avg_time"] = (
                performance_by_arch[arch]["total_time"] / performance_by_arch[arch]["count"]
            )
        
        return performance_by_arch
    
    def export_results(self, result: ProcessingResult, format: str = "json") -> str:
        """Export processing results in different formats"""
        
        if format.lower() == "json":
            return json.dumps({
                "architecture": result.architecture_used,
                "task": result.task,
                "processing_time": result.processing_time,
                "timestamp": result.timestamp.isoformat(),
                "metadata": result.metadata,
                "results_summary": self._summarize_results(result.results)
            }, indent=2)
        
        elif format.lower() == "markdown":
            return self._generate_markdown_report(result)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _summarize_results(self, results: Any) -> Dict[str, Any]:
        """Create a summary of results regardless of architecture"""
        
        if self.current_architecture == ArchitectureType.SEQUENTIAL:
            return {
                "type": "sequential_pipeline",
                "agents_participated": len(results) if isinstance(results, list) else 0,
                "key_insights": [r.response[:100] + "..." for r in results[:3]] if isinstance(results, list) else []
            }
        
        elif self.current_architecture == ArchitectureType.ROUND_TABLE:
            return {
                "type": "round_table_discussion",
                "rounds_completed": len(results) if isinstance(results, list) else 0,
                "consensus_items": results[-1].consensus_items if results and hasattr(results[-1], 'consensus_items') else []
            }
        
        elif self.current_architecture == ArchitectureType.REACTIVE:
            return {
                "type": "reactive_system",
                "events_processed": len(results) if isinstance(results, list) else 0,
                "event_types": list(set(e.event_type.value for e in results)) if isinstance(results, list) else []
            }
        
        return {"type": "unknown", "summary": "Results available"}
    
    def _generate_markdown_report(self, result: ProcessingResult) -> str:
        """Generate a markdown report of the processing results"""
        
        report = f"""# AI Agent Processing Report

## Task Information
- **Title**: {result.task.get('title', 'Untitled')}
- **ID**: {result.task.get('task_id', 'N/A')}
- **Priority**: {result.task.get('priority', 'N/A')}
- **Description**: {result.task.get('description', 'N/A')}

## Processing Details
- **Architecture Used**: {result.architecture_used}
- **Processing Time**: {result.processing_time:.2f} seconds
- **Timestamp**: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

## Results Summary
{json.dumps(self._summarize_results(result.results), indent=2)}

## Metadata
{json.dumps(result.metadata, indent=2)}
"""
        return report

# Integration with existing system
def integrate_with_existing_api():
    """Show how to integrate with the existing task_router_api.py"""
    
    integration_example = """
    # In your task_router_api.py, you can add:
    
    from agent_architecture_manager import AgentArchitectureManager
    
    # Initialize the manager
    architecture_manager = AgentArchitectureManager()
    
    @app.route('/set_architecture', methods=['POST'])
    def set_architecture():
        data = request.json
        architecture = data.get('architecture', 'sequential')
        
        if architecture_manager.set_architecture(architecture):
            return jsonify({"success": True, "architecture": architecture})
        else:
            return jsonify({"error": "Invalid architecture"}), 400
    
    @app.route('/process_with_agents', methods=['POST'])
    async def process_with_agents():
        task_data = request.json
        result = await architecture_manager.process_task(task_data)
        
        return jsonify({
            "success": True,
            "architecture_used": result.architecture_used,
            "processing_time": result.processing_time,
            "results_summary": architecture_manager._summarize_results(result.results)
        })
    """
    
    return integration_example

# Example usage and testing
async def main():
    manager = AgentArchitectureManager()
    
    # Show available architectures
    print("🏗️  Available Architectures:")
    for arch, desc in manager.list_available_architectures().items():
        print(f"  {arch}: {desc}")
    
    # Test task
    task = {
        "task_id": "DEMO-001",
        "title": "Multi-Architecture Demo",
        "description": "Demonstrate switching between different agent architectures",
        "priority": "medium"
    }
    
    # Test different architectures
    architectures_to_test = ["sequential", "round_table", "reactive"]
    
    for arch in architectures_to_test:
        print(f"\n{'='*60}")
        manager.set_architecture(arch)
        result = await manager.process_task(task)
        print(f"📊 {arch} completed in {result.processing_time:.2f}s")
    
    # Show performance comparison
    print(f"\n{'='*60}")
    print("📈 Performance Comparison:")
    performance = manager.compare_architectures_performance()
    for arch, metrics in performance.items():
        print(f"  {arch}: {metrics['count']} runs, avg {metrics['avg_time']:.2f}s")

if __name__ == "__main__":
    asyncio.run(main())
