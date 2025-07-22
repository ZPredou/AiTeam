import json
import os

# Load team config
def load_team_config(path=None):
    if path is None:
        # Get the absolute path to the config file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        path = os.path.join(project_root, "config", "ai_dev_team_config.json")
    with open(path, "r") as f:
        return json.load(f)["members"]

# Load a task
def load_task(path=None, task_id=None):
    if path is None:
        # Get the absolute path to the config file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        path = os.path.join(project_root, "config", "tasks.json")
    with open(path, "r") as f:
        data = json.load(f)
    
    # Check if the file contains a tasks array
    if "tasks" in data:
        tasks = data["tasks"]
        if task_id:
            # Find specific task by ID
            task = next((t for t in tasks if t["task_id"] == task_id), None)
            if not task:
                print(f"No task found with ID: {task_id}")
                return None
            return task
        else:
            # Return the first task if no ID specified
            return tasks[0] if tasks else None
    else:
        # Handle the case where it's a single task
        return data

# Route task to appropriate agent
def route_task(team_config, task):
    assigned_id = task["assigned_to"]
    member = next((m for m in team_config if m["id"] == assigned_id), None)

    if not member:
        print(f"No team member found with ID: {assigned_id}")
        return

    print(f"\n👤 Assigned Role: {member['role']} ({member['id']})")
    print(f"🧠 Personality Prompt:\n{member['personality_prompt']}")
    print(f"\n📌 Task: {task['title']}")
    print(f"📄 Description:\n{task['description']}")
    if "context_files" in task:
        print(f"\n📎 Context Files: {', '.join(task['context_files'])}")
    print("\n🔁 Ready to send this to AugmentCode or an LLM agent.\n")

# Entry point
if __name__ == "__main__":
    team = load_team_config()
    # You can specify a task_id or leave it empty to get the first task
    task = load_task(task_id="T-1001")  # Optionally specify which task to load
    if task:
        route_task(team, task)
