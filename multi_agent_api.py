#!/usr/bin/env python3
"""
Multi-Agent API - Enhanced API that integrates with the Agent Architecture Manager

This API extends your existing task_router_api.py with multi-agent processing capabilities.
You can easily switch between different agent interaction architectures.
"""

import json
import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS
from agent_architecture_manager import AgentArchitectureManager
from task_router import load_team_config

app = Flask(__name__)
CORS(app)

# Initialize the architecture manager
architecture_manager = AgentArchitectureManager()

@app.route('/architectures', methods=['GET'])
def get_available_architectures():
    """Get list of available agent architectures"""
    architectures = architecture_manager.list_available_architectures()
    current = architecture_manager.get_current_architecture()
    
    return jsonify({
        "current_architecture": current,
        "available_architectures": architectures,
        "success": True
    })

@app.route('/set_architecture', methods=['POST'])
def set_architecture():
    """Set the active agent architecture"""
    try:
        data = request.json
        architecture = data.get('architecture')
        
        if not architecture:
            return jsonify({"error": "Architecture parameter required"}), 400
        
        success = architecture_manager.set_architecture(architecture)
        
        if success:
            return jsonify({
                "success": True,
                "architecture": architecture_manager.get_current_architecture(),
                "message": f"Architecture set to {architecture}"
            })
        else:
            available = list(architecture_manager.list_available_architectures().keys())
            return jsonify({
                "error": f"Invalid architecture. Available: {', '.join(available)}"
            }), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/process_with_agents', methods=['POST'])
def process_with_agents():
    """Process a task using the selected agent architecture"""
    try:
        task_data = request.json
        
        if not task_data:
            return jsonify({"error": "No task data provided"}), 400
        
        # Ensure required fields
        task = {
            "task_id": task_data.get("story_id", task_data.get("task_id", "unknown")),
            "title": task_data.get("title", ""),
            "description": task_data.get("description", ""),
            "priority": task_data.get("priority", "medium"),
            "status": task_data.get("status", "ready")
        }
        
        # Run the async processing in a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(architecture_manager.process_task(task))
        finally:
            loop.close()
        
        # Generate response based on architecture
        response_data = {
            "success": True,
            "task": task,
            "architecture_used": result.architecture_used,
            "processing_time": result.processing_time,
            "timestamp": result.timestamp.isoformat(),
            "metadata": result.metadata
        }
        
        # Add architecture-specific results
        if result.architecture_used == "sequential":
            response_data["agent_responses"] = [
                {
                    "agent_id": r.agent_id,
                    "role": r.role,
                    "response": r.response,
                    "estimated_effort": r.estimated_effort,
                    "concerns": r.concerns,
                    "recommendations": r.recommendations
                } for r in result.results
            ]
            
        elif result.architecture_used == "round_table":
            response_data["discussion_rounds"] = [
                {
                    "round": r.round_number,
                    "topic": r.topic,
                    "consensus_items": r.consensus_items,
                    "unresolved_items": r.unresolved_items,
                    "participant_count": len(r.responses)
                } for r in result.results
            ]
            
        elif result.architecture_used == "reactive":
            response_data["events"] = [
                {
                    "event_type": e.event_type.value,
                    "source_agent": e.source_agent,
                    "timestamp": e.timestamp.isoformat(),
                    "data": e.data
                } for e in result.results[-10:]  # Last 10 events
            ]
            response_data["total_events"] = len(result.results)
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error processing with agents: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/export_results/<result_id>', methods=['GET'])
def export_results(result_id):
    """Export processing results in different formats"""
    try:
        format_type = request.args.get('format', 'json')
        
        # Get result from history (simplified - in production you'd use proper storage)
        history = architecture_manager.get_processing_history()
        
        if not history:
            return jsonify({"error": "No processing history available"}), 404
        
        # For demo, return the latest result
        latest_result = history[-1]
        
        if format_type.lower() == 'markdown':
            exported = architecture_manager.export_results(latest_result, 'markdown')
            return exported, 200, {'Content-Type': 'text/markdown'}
        else:
            exported = architecture_manager.export_results(latest_result, 'json')
            return exported, 200, {'Content-Type': 'application/json'}
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/performance_comparison', methods=['GET'])
def get_performance_comparison():
    """Get performance comparison across different architectures"""
    try:
        comparison = architecture_manager.compare_architectures_performance()
        return jsonify({
            "success": True,
            "performance_data": comparison,
            "total_runs": sum(arch_data["count"] for arch_data in comparison.values())
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/processing_history', methods=['GET'])
def get_processing_history():
    """Get recent processing history"""
    try:
        limit = request.args.get('limit', 10, type=int)
        history = architecture_manager.get_processing_history(limit)
        
        history_data = [
            {
                "architecture": result.architecture_used,
                "task_title": result.task.get("title", "Untitled"),
                "task_id": result.task.get("task_id", "N/A"),
                "processing_time": result.processing_time,
                "timestamp": result.timestamp.isoformat(),
                "metadata": result.metadata
            } for result in history
        ]
        
        return jsonify({
            "success": True,
            "history": history_data,
            "total_entries": len(history)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Legacy endpoint compatibility - enhanced version of your existing route_task
@app.route('/route_task', methods=['POST'])
def route_task_enhanced():
    """Enhanced version of the original route_task endpoint with multi-agent support"""
    try:
        task_data = request.json
        
        if not task_data:
            return jsonify({"error": "No task data provided"}), 400
        
        # Check if multi-agent processing is requested
        use_multi_agent = task_data.get("use_multi_agent", False)
        
        if use_multi_agent:
            # Use the new multi-agent processing
            return process_with_agents()
        else:
            # Fall back to original single-agent routing
            from task_router_api import route_task_endpoint
            return route_task_endpoint()
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Multi-Agent API is running",
        "current_architecture": architecture_manager.get_current_architecture(),
        "available_architectures": list(architecture_manager.list_available_architectures().keys())
    })

# WebSocket support for real-time updates (optional enhancement)
@app.route('/stream_processing', methods=['POST'])
def stream_processing():
    """Stream processing updates in real-time (placeholder for WebSocket implementation)"""
    return jsonify({
        "message": "Real-time streaming not implemented yet",
        "suggestion": "Use polling on /processing_history for now"
    })

if __name__ == '__main__':
    print("🚀 Starting Multi-Agent API...")
    print("📡 API available at: http://localhost:5001")
    print("🏗️  Available endpoints:")
    print("   GET  /architectures - List available architectures")
    print("   POST /set_architecture - Set active architecture")
    print("   POST /process_with_agents - Process task with agents")
    print("   GET  /performance_comparison - Compare architecture performance")
    print("   GET  /processing_history - Get processing history")
    print("   POST /route_task - Enhanced legacy endpoint")
    print("   GET  /health - Health check")
    
    # Show current configuration
    print(f"\n🔧 Current Configuration:")
    print(f"   Architecture: {architecture_manager.get_current_architecture()}")
    print(f"   Team Members: {len(architecture_manager.team_config['members'])}")
    
    app.run(debug=True, port=5001)
