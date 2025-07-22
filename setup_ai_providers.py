#!/usr/bin/env python3
"""
Setup script for AI providers

This script helps you configure AI providers for the multi-agent system.
It will guide you through setting up API keys and testing connections.
"""

import os
import asyncio
import json
from ai_providers import create_ai_provider_manager, AIProvider

def print_header():
    print("🤖 AI PROVIDERS SETUP")
    print("=" * 50)
    print("This script will help you set up AI providers for your multi-agent system.")
    print()

def check_environment_variables():
    """Check which AI provider environment variables are set"""
    
    print("🔍 Checking environment variables...")
    
    providers_status = {
        "OpenAI": {
            "env_var": "OPENAI_API_KEY",
            "value": os.getenv("OPENAI_API_KEY"),
            "status": "✅" if os.getenv("OPENAI_API_KEY") else "❌"
        },
        "Anthropic": {
            "env_var": "ANTHROPIC_API_KEY", 
            "value": os.getenv("ANTHROPIC_API_KEY"),
            "status": "✅" if os.getenv("ANTHROPIC_API_KEY") else "❌"
        },
        "Ollama": {
            "env_var": "OLLAMA_BASE_URL",
            "value": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            "status": "🔄" # Will test connection
        }
    }
    
    for provider, info in providers_status.items():
        if provider == "Ollama":
            print(f"{info['status']} {provider}: {info['value']} (will test connection)")
        else:
            status_text = "Set" if info['value'] else "Not set"
            print(f"{info['status']} {provider}: {status_text}")
    
    return providers_status

def show_setup_instructions():
    """Show instructions for setting up API keys"""
    
    print("\n📝 SETUP INSTRUCTIONS")
    print("=" * 50)
    
    print("\n🔑 OpenAI Setup:")
    print("1. Go to https://platform.openai.com/api-keys")
    print("2. Create a new API key")
    print("3. Set environment variable:")
    print("   export OPENAI_API_KEY='your-api-key-here'")
    
    print("\n🔑 Anthropic Setup:")
    print("1. Go to https://console.anthropic.com/")
    print("2. Create a new API key")
    print("3. Set environment variable:")
    print("   export ANTHROPIC_API_KEY='your-api-key-here'")
    
    print("\n🏠 Ollama Setup (Local):")
    print("1. Install Ollama: https://ollama.ai/")
    print("2. Pull a model: ollama pull llama2")
    print("3. Start Ollama: ollama serve")
    print("4. (Optional) Set custom URL:")
    print("   export OLLAMA_BASE_URL='http://localhost:11434'")

def create_env_file():
    """Create a .env file template"""
    
    env_content = """# AI Provider API Keys
# Uncomment and fill in your API keys

# OpenAI
# OPENAI_API_KEY=your-openai-api-key-here
# OPENAI_MODEL=gpt-4

# Anthropic Claude
# ANTHROPIC_API_KEY=your-anthropic-api-key-here
# ANTHROPIC_MODEL=claude-3-sonnet-20240229

# Ollama (Local)
# OLLAMA_BASE_URL=http://localhost:11434
# OLLAMA_MODEL=llama2

# Cost tracking (optional)
# AI_DAILY_LIMIT_USD=10.0
"""
    
    with open('.env.template', 'w') as f:
        f.write(env_content)
    
    print("📄 Created .env.template file")
    print("   Copy to .env and fill in your API keys")

async def test_providers():
    """Test available AI providers"""
    
    print("\n🧪 TESTING AI PROVIDERS")
    print("=" * 50)
    
    try:
        manager = create_ai_provider_manager()
        available = manager.get_available_providers()
        
        if not available:
            print("❌ No AI providers available!")
            print("   Please set up at least one provider using the instructions above.")
            return False
        
        print(f"🎯 Available providers: {', '.join(available)}")
        print(f"🔧 Primary provider: {manager.primary_provider.value}")
        
        # Test with a simple prompt
        test_prompt = """You are a software engineer. Respond with a JSON object containing:
{
  "analysis": "Brief analysis of implementing a user login system",
  "concerns": ["concern1", "concern2"],
  "recommendations": ["rec1", "rec2"],
  "effort_estimate": "X days",
  "next_steps": ["step1", "step2"]
}

Keep it concise and professional."""
        
        print("\n🔄 Testing AI response...")
        response = await manager.generate_response(test_prompt)
        
        print(f"✅ Success! Response from {response.provider} ({response.model})")
        print(f"📝 Response preview: {response.content[:100]}...")
        
        if response.tokens_used:
            print(f"🔢 Tokens used: {response.tokens_used}")
        if response.cost_estimate:
            print(f"💰 Estimated cost: ${response.cost_estimate:.4f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def show_usage_examples():
    """Show usage examples"""
    
    print("\n💡 USAGE EXAMPLES")
    print("=" * 50)
    
    print("\n🐍 Python Code:")
    print("""
from ai_providers import create_ai_provider_manager

# Create AI manager
ai_manager = create_ai_provider_manager()

# Generate response
response = await ai_manager.generate_response(
    "Analyze this task: Implement user authentication",
    agent_role="Tech Lead"
)

print(f"Response: {response.content}")
""")
    
    print("\n🌐 API Usage:")
    print("""
# Start the multi-agent API
python multi_agent_api.py

# Process task with real AI
curl -X POST http://localhost:5001/process_with_agents \\
  -H "Content-Type: application/json" \\
  -d '{
    "task_id": "AUTH-001",
    "title": "User Authentication",
    "description": "Implement secure login system",
    "priority": "high"
  }'
""")

def show_cost_information():
    """Show cost information for different providers"""
    
    print("\n💰 COST INFORMATION")
    print("=" * 50)
    
    print("📊 Approximate costs per 1K tokens (as of 2024):")
    print("   OpenAI GPT-4:        $0.03")
    print("   OpenAI GPT-4 Turbo:  $0.01")
    print("   OpenAI GPT-3.5:      $0.002")
    print("   Anthropic Claude:    $0.015")
    print("   Ollama (Local):      Free")
    
    print("\n💡 Cost-saving tips:")
    print("   • Use GPT-3.5 for simpler tasks")
    print("   • Set up Ollama for development/testing")
    print("   • Monitor usage with built-in tracking")
    print("   • Set daily limits in ai_config.json")

async def main():
    """Main setup flow"""
    
    print_header()
    
    # Check current status
    status = check_environment_variables()
    
    # Show setup instructions
    show_setup_instructions()
    
    # Create template file
    create_env_file()
    
    # Test providers
    print("\n" + "=" * 50)
    test_success = await test_providers()
    
    if test_success:
        print("\n🎉 SETUP COMPLETE!")
        print("Your AI providers are configured and working.")
        
        # Show usage examples
        show_usage_examples()
        
        print("\n🚀 Next steps:")
        print("1. Run: python demo_multi_agent_system.py")
        print("2. Start API: python multi_agent_api.py")
        print("3. Open web interface: ai_backlog_viewer/index.html")
        
    else:
        print("\n⚠️  SETUP INCOMPLETE")
        print("Please configure at least one AI provider and run this script again.")
        print("\nQuick start options:")
        print("1. Set OPENAI_API_KEY for best results")
        print("2. Install Ollama for free local AI")
        print("3. Set ANTHROPIC_API_KEY for Claude")
    
    # Show cost information
    show_cost_information()

if __name__ == "__main__":
    asyncio.run(main())
