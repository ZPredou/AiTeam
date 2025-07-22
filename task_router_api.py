#!/usr/bin/env python3
"""
Task Router API - Provides HTTP endpoints for routing tasks to team members
"""
import json
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from task_router import load_team_config, route_task

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/route_task', methods=['POST'])
def route_task_endpoint():
    """
    Route a task to a team member and generate AugmentCode prompt
    
    Expected JSON payload:
    {
        "story_id": "story-1",
        "title": "Task title",
        "description": "Task description", 
        "priority": "high",
        "status": "ready",
        "assigned_to": "tech_lead"
    }
    """
    try:
        # Get task data from request
        task_data = request.json
        
        if not task_data:
            return jsonify({"error": "No task data provided"}), 400
            
        # Load team configuration
        team_config = load_team_config()
        
        # Find the assigned team member
        assigned_role = task_data.get("assigned_to")
        if not assigned_role:
            return jsonify({"error": "No assigned_to field provided"}), 400
            
        # Map role name to member ID
        role_to_id_map = {
            "Project Manager": "manager",
            "Product Owner": "product_owner", 
            "Tech Lead": "tech_lead",
            "QA Engineer": "qa_engineer",
            "Software Developer (Frontend)": "developer_1",
            "Software Developer (Backend)": "developer_2"
        }
        
        member_id = role_to_id_map.get(assigned_role)
        if not member_id:
            return jsonify({"error": f"Unknown role: {assigned_role}"}), 400
            
        # Find the team member
        member = next((m for m in team_config if m["id"] == member_id), None)
        if not member:
            return jsonify({"error": f"No team member found with ID: {member_id}"}), 400
        
        # Create task object in the format expected by route_task
        task = {
            "task_id": task_data.get("story_id", "unknown"),
            "title": task_data.get("title", ""),
            "description": task_data.get("description", ""),
            "priority": task_data.get("priority", "medium"),
            "status": task_data.get("status", "ready"),
            "assigned_to": member_id
        }
        
        # Generate the prompt
        prompt = generate_augment_prompt(member, task)
        
        # Print to console (this will appear in your Python server terminal)
        print("\n" + "="*60)
        print("🚀 TASK ROUTED TO AUGMENTCODE")
        print("="*60)
        route_task(team_config, task)
        print("="*60)
        print("📋 AUGMENTCODE PROMPT:")
        print("="*60)
        print(prompt)
        print("="*60 + "\n")
        
        return jsonify({
            "success": True,
            "message": f"Task routed to {member['role']}",
            "prompt": prompt,
            "member": {
                "id": member["id"],
                "role": member["role"],
                "capabilities": member["capabilities"]
            }
        })
        
    except Exception as e:
        print(f"Error routing task: {str(e)}")
        return jsonify({"error": str(e)}), 500

def generate_augment_prompt(member, task):
    """Generate a detailed prompt for AugmentCode"""
    prompt = f"""{member['personality_prompt']}

**Task Assignment:**
- **Story ID:** {task['task_id']}
- **Title:** {task['title']}
- **Description:** {task['description']}
- **Priority:** {task['priority']}
- **Status:** {task['status']}

**Your Role:** {member['role']}
**Your Capabilities:** {', '.join(member['capabilities'])}

**Instructions:**
Please analyze this task and provide your perspective as a {member['role']}. Consider:
1. How you would approach this task given your role and capabilities
2. Any dependencies or blockers you foresee
3. Estimated effort and timeline
4. Any questions or clarifications needed
5. Next steps you would recommend

Please provide a detailed response based on your expertise and role responsibilities."""
    
    return prompt

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "Task Router API is running"})

if __name__ == '__main__':
    print("🚀 Starting Task Router API...")
    print("📡 API will be available at: http://localhost:5000")
    print("🔗 Use POST /route_task to route tasks")
    print("💡 Use GET /health for health check")
    app.run(debug=True, port=5000)
