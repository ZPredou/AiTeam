// Team members list - loaded from configuration
const teamMembers = [
  'Project Manager',
  'Product Owner',
  'Tech Lead',
  'QA Engineer',
  'Software Developer (Frontend)',
  'Software Developer (Backend)'
];

// Store assignments in memory (in a real app, this would be persisted)
let assignments = {};

// Team member configurations loaded from ai_dev_team_config.json
let teamConfig = null;
let currentArchitecture = 'sequential';
let availableArchitectures = {};

// Load team configuration
async function loadTeamConfig() {
  try {
    const response = await fetch('../ai_dev_team_config.json');
    teamConfig = await response.json();

    // Load available architectures
    await loadArchitectures();
  } catch (error) {
    console.error('Failed to load team configuration:', error);
  }
}

async function loadArchitectures() {
  try {
    const response = await fetch('http://localhost:5001/architectures');
    const data = await response.json();

    if (data.success) {
      availableArchitectures = data.available_architectures;
      currentArchitecture = data.current_architecture;
      console.log('Architectures loaded:', availableArchitectures);

      // Update UI with architecture selector
      updateArchitectureSelector();
    }
  } catch (error) {
    console.error('Error loading architectures:', error);
    // Fallback to single architecture mode
    availableArchitectures = {
      'sequential': 'Sequential Pipeline - Default single-agent mode'
    };
  }
}

function getStatusClass(status) {
  return 'status-' + status.toLowerCase().replace(/\s+/g, '');
}

function getPriorityClass(priority) {
  return 'priority-' + priority.toLowerCase();
}

async function runStoryPrompt(storyId, teamMember) {
  // Check if multi-agent processing is enabled
  const useMultiAgent = document.getElementById('multiAgentToggle')?.checked || false;

  if (useMultiAgent) {
    // Use multi-agent processing (teamMember can be null)
    await processWithMultipleAgents(storyId);
  } else if (teamMember && teamMember !== '') {
    // Generate and display the single AugmentCode prompt
    await generateAugmentCodePrompt(storyId, teamMember);
  }
}

async function processWithMultipleAgents(storyId) {
  const story = findStoryById(storyId);
  if (!story) {
    console.error('Story not found:', storyId);
    return;
  }

  const task = {
    story_id: story.id,
    title: story.title,
    description: story.description,
    priority: story.priority,
    status: story.status
  };

  try {
    console.log(`Processing with ${currentArchitecture} architecture...`);

    const response = await fetch('http://localhost:5001/process_with_agents', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(task)
    });

    const result = await response.json();

    if (result.success) {
      displayMultiAgentResults(result, story.title);
    } else {
      console.error('Multi-agent processing failed:', result.error);
      alert('Multi-agent processing failed: ' + result.error);
    }
  } catch (error) {
    console.error('Error in multi-agent processing:', error);
    alert('Error connecting to multi-agent API. Make sure the server is running on port 5001.');
  }
}

async function generateAugmentCodePrompt(storyId, teamMemberRole) {
  if (!teamConfig) {
    console.error('Team configuration not loaded');
    return;
  }

  // Find the team member configuration
  const memberConfig = teamConfig.members.find(member => member.role === teamMemberRole);
  if (!memberConfig) {
    console.error('Team member configuration not found for role:', teamMemberRole);
    return;
  }

  // Find the story details (we'll need to get this from the current data)
  const story = findStoryById(storyId);
  if (!story) {
    console.error('Story not found:', storyId);
    return;
  }

  // Generate the prompt
  const prompt = `${memberConfig.personality_prompt}

**Task Assignment:**
- **Story ID:** ${story.id}
- **Title:** ${story.title}
- **Description:** ${story.description}
- **Priority:** ${story.priority}
- **Status:** ${story.status}

**Your Role:** ${memberConfig.role}
**Your Capabilities:** ${memberConfig.capabilities.join(', ')}

**Instructions:**
Please analyze this task and provide your perspective as a ${memberConfig.role}. Consider:
1. How you would approach this task given your role and capabilities
2. Any dependencies or blockers you foresee
3. Estimated effort and timeline
4. Any questions or clarifications needed
5. Next steps you would recommend

Please provide a detailed response based on your expertise and role responsibilities.`;

  // Display the prompt in a modal or copy to clipboard
  displayPrompt(prompt, teamMemberRole, story.title);
}



function findStoryById(storyId) {
  // This will be populated when we load the backlog
  if (window.currentBacklogData) {
    for (const epic of window.currentBacklogData.epics) {
      const story = epic.stories.find(s => s.id === storyId);
      if (story) return story;
    }
  }
  return null;
}

function displayPrompt(prompt, role, storyTitle) {
  // Create a modal to display the prompt
  const modal = document.createElement('div');
  modal.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.6);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  `;

  const modalContent = document.createElement('div');
  modalContent.style.cssText = `
    background: white;
    padding: 2em;
    border-radius: 12px;
    max-width: 90%;
    max-height: 90%;
    overflow-y: auto;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    border: 1px solid #e1e8ed;
  `;

  modalContent.innerHTML = `
    <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 1.5em;">
      <div>
        <h2 style="margin: 0; color: #2c3e50;">🤖 AugmentCode Prompt Ready</h2>
        <p style="margin: 0.5em 0 0 0; color: #7f8c8d;"><strong>Role:</strong> ${role} | <strong>Story:</strong> ${storyTitle}</p>
      </div>
    </div>
    <div style="position: relative;">
      <textarea readonly id="promptText" style="
        width: 100%;
        height: 400px;
        margin: 0 0 1.5em 0;
        padding: 1.5em;
        border: 2px solid #e1e8ed;
        border-radius: 8px;
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        font-size: 13px;
        line-height: 1.5;
        background: #f8f9fa;
        resize: vertical;
        box-sizing: border-box;
      ">${prompt}</textarea>
    </div>
    <div style="display: flex; gap: 1em; justify-content: space-between; align-items: center;">
      <div style="color: #7f8c8d; font-size: 0.9em;">
        💡 Click "Copy Prompt" then paste into AugmentCode
      </div>
      <div style="display: flex; gap: 1em;">
        <button id="copyPrompt" style="
          padding: 0.8em 1.5em;
          background: #27ae60;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-weight: bold;
          font-size: 14px;
          transition: background 0.3s ease;
        ">📋 Copy Prompt</button>
        <button id="closeModal" style="
          padding: 0.8em 1.5em;
          background: #95a5a6;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-size: 14px;
          transition: background 0.3s ease;
        ">Close</button>
      </div>
    </div>
  `;

  modal.appendChild(modalContent);
  document.body.appendChild(modal);

  // Auto-select the text for easy copying
  const textArea = document.getElementById('promptText');
  textArea.focus();
  textArea.select();

  // Add event listeners
  const copyButton = document.getElementById('copyPrompt');
  copyButton.onclick = () => {
    navigator.clipboard.writeText(prompt).then(() => {
      // Visual feedback for successful copy
      copyButton.style.background = '#2ecc71';
      copyButton.textContent = '✅ Copied!';
      setTimeout(() => {
        copyButton.style.background = '#27ae60';
        copyButton.textContent = '📋 Copy Prompt';
      }, 2000);
    }).catch(() => {
      // Fallback for older browsers
      textArea.select();
      document.execCommand('copy');
      copyButton.style.background = '#2ecc71';
      copyButton.textContent = '✅ Copied!';
      setTimeout(() => {
        copyButton.style.background = '#27ae60';
        copyButton.textContent = '📋 Copy Prompt';
      }, 2000);
    });
  };

  // Hover effects
  copyButton.onmouseover = () => {
    if (copyButton.textContent === '📋 Copy Prompt') {
      copyButton.style.background = '#229954';
    }
  };
  copyButton.onmouseout = () => {
    if (copyButton.textContent === '📋 Copy Prompt') {
      copyButton.style.background = '#27ae60';
    }
  };

  document.getElementById('closeModal').onclick = () => {
    document.body.removeChild(modal);
  };

  // Close modal when clicking outside
  modal.onclick = (e) => {
    if (e.target === modal) {
      document.body.removeChild(modal);
    }
  };

  // Close modal with Escape key
  const handleEscape = (e) => {
    if (e.key === 'Escape') {
      document.body.removeChild(modal);
      document.removeEventListener('keydown', handleEscape);
    }
  };
  document.addEventListener('keydown', handleEscape);
}

function createAssignmentSection(story) {
  const assignmentDiv = document.createElement('div');
  assignmentDiv.className = 'assignment-section';

  // Show run controls (always visible, no assignment tracking)
  const select = document.createElement('select');
  select.className = 'assign-select';

  const defaultOption = document.createElement('option');
  defaultOption.value = '';
  defaultOption.textContent = 'Select team member...';
  select.appendChild(defaultOption);

  teamMembers.forEach(member => {
    const option = document.createElement('option');
    option.value = member;
    option.textContent = member;
    select.appendChild(option);
  });

  const runBtn = document.createElement('button');
  runBtn.className = 'run-btn';
  runBtn.textContent = 'Run';
  runBtn.disabled = true;

  // Function to update visibility based on multi-agent toggle
  function updateAssignmentVisibility() {
    const multiAgentToggle = document.getElementById('multiAgentToggle');
    const isMultiAgentEnabled = multiAgentToggle && multiAgentToggle.checked;

    if (isMultiAgentEnabled) {
      // Hide team selection, enable run button
      select.style.display = 'none';
      runBtn.disabled = false;
      runBtn.textContent = 'Run Multi-Agent';
    } else {
      // Show team selection, disable run button until selection made
      select.style.display = 'inline-block';
      runBtn.disabled = select.value === '';
      runBtn.textContent = 'Run';
    }
  }

  select.onchange = () => {
    const multiAgentToggle = document.getElementById('multiAgentToggle');
    const isMultiAgentEnabled = multiAgentToggle && multiAgentToggle.checked;

    if (!isMultiAgentEnabled) {
      runBtn.disabled = select.value === '';
    }
  };

  runBtn.onclick = () => {
    const multiAgentToggle = document.getElementById('multiAgentToggle');
    const isMultiAgentEnabled = multiAgentToggle && multiAgentToggle.checked;

    if (isMultiAgentEnabled) {
      // Multi-agent processing - no team member selection needed
      runStoryPrompt(story.id, null);
    } else if (select.value) {
      // Single agent processing - need team member selection
      runStoryPrompt(story.id, select.value);
    }
  };

  // Store reference to update function for later use
  assignmentDiv.updateVisibility = updateAssignmentVisibility;

  assignmentDiv.appendChild(select);
  assignmentDiv.appendChild(runBtn);

  // Initial visibility update
  setTimeout(updateAssignmentVisibility, 100); // Small delay to ensure toggle exists

  return assignmentDiv;
}

async function loadBacklog() {
  const response = await fetch('backlog.json');
  const data = await response.json();

  // Store the data globally so we can access it for prompt generation
  window.currentBacklogData = data;

  const backlogDiv = document.getElementById('backlog');

  // Clear existing content
  backlogDiv.innerHTML = '';

  data.epics.forEach(epic => {
    const epicDiv = document.createElement('div');
    epicDiv.className = 'epic';

    const epicTitle = document.createElement('h2');
    epicTitle.textContent = '📦 ' + epic.title;
    epicDiv.appendChild(epicTitle);

    const epicDesc = document.createElement('p');
    epicDesc.textContent = epic.description;
    epicDiv.appendChild(epicDesc);

    epic.stories.forEach(story => {
      const storyDiv = document.createElement('div');
      storyDiv.className = 'story';

      const title = document.createElement('strong');
      title.textContent = story.title;
      storyDiv.appendChild(title);

      const desc = document.createElement('p');
      desc.textContent = story.description;
      storyDiv.appendChild(desc);

      const meta = document.createElement('div');
      meta.className = 'meta';

      const idSpan = document.createElement('span');
      idSpan.textContent = `ID: ${story.id}`;
      meta.appendChild(idSpan);

      const prioritySpan = document.createElement('span');
      prioritySpan.className = getPriorityClass(story.priority);
      prioritySpan.textContent = `Priority: ${story.priority}`;
      meta.appendChild(prioritySpan);

      const statusSpan = document.createElement('span');
      statusSpan.className = `status-badge ${getStatusClass(story.status)}`;
      statusSpan.textContent = story.status;
      meta.appendChild(statusSpan);

      storyDiv.appendChild(meta);

      // Add run section
      const runSection = createAssignmentSection(story);
      storyDiv.appendChild(runSection);

      epicDiv.appendChild(storyDiv);
    });

    backlogDiv.appendChild(epicDiv);
  });
}

// Multi-agent processing functions
function displayMultiAgentResults(result, storyTitle) {
  // Create a modal to display multi-agent results
  const modal = document.createElement('div');
  modal.className = 'multi-agent-modal';
  modal.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.6);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  `;

  const modalContent = document.createElement('div');
  modalContent.style.cssText = `
    background: white;
    padding: 2em;
    border-radius: 12px;
    max-width: 95%;
    max-height: 95%;
    overflow-y: auto;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    border: 1px solid #e1e8ed;
  `;

  let resultsHtml = `
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5em;">
      <div>
        <h2 style="margin: 0; color: #2c3e50;">🤖 Multi-Agent Processing Results</h2>
        <p style="margin: 0.5em 0 0 0; color: #7f8c8d;">
          <strong>Architecture:</strong> ${result.architecture_used} |
          <strong>Story:</strong> ${storyTitle} |
          <strong>Processing Time:</strong> ${result.processing_time.toFixed(2)}s
        </p>
      </div>
    </div>
  `;

  // Display results based on architecture type
  if (result.architecture_used === 'sequential' && result.agent_responses) {
    resultsHtml += '<h3>🔄 Sequential Agent Responses:</h3>';
    result.agent_responses.forEach((response, index) => {
      resultsHtml += `
        <div style="margin-bottom: 1.5em; padding: 1em; border: 1px solid #e1e8ed; border-radius: 8px;">
          <h4 style="margin: 0 0 0.5em 0; color: #3498db;">
            ${index + 1}. ${response.role}
          </h4>
          <p><strong>Response:</strong> ${response.response}</p>
          <p><strong>Estimated Effort:</strong> ${response.estimated_effort}</p>
          ${response.concerns.length > 0 ? `<p><strong>Concerns:</strong> ${response.concerns.join(', ')}</p>` : ''}
          ${response.recommendations.length > 0 ? `<p><strong>Recommendations:</strong> ${response.recommendations.join(', ')}</p>` : ''}
        </div>
      `;
    });
  }

  resultsHtml += `
    <div style="margin-top: 2em; text-align: center;">
      <button onclick="document.querySelector('.multi-agent-modal').remove()" style="
        background: #3498db;
        color: white;
        border: none;
        padding: 0.8em 2em;
        border-radius: 6px;
        cursor: pointer;
        font-size: 1em;
      ">Close</button>
    </div>
  `;

  modalContent.innerHTML = resultsHtml;
  modal.appendChild(modalContent);

  // Close modal when clicking outside
  modal.onclick = (e) => {
    if (e.target === modal) {
      modal.remove();
    }
  };

  document.body.appendChild(modal);
}

function updateArchitectureSelector() {
  // Add architecture selector to the page header
  const header = document.querySelector('h1');
  if (header && !document.getElementById('architectureControls')) {
    const controlsDiv = document.createElement('div');
    controlsDiv.id = 'architectureControls';
    controlsDiv.style.cssText = `
      margin-top: 1em;
      padding: 1em;
      background: #f8f9fa;
      border-radius: 8px;
      border: 1px solid #e1e8ed;
    `;

    let controlsHtml = `
      <div style="display: flex; align-items: center; gap: 1em; flex-wrap: wrap;">
        <label style="font-weight: bold; color: #2c3e50;">
          🏗️ Agent Architecture:
        </label>
        <select id="architectureSelect" style="
          padding: 0.5em;
          border: 1px solid #ddd;
          border-radius: 4px;
          background: white;
        ">
    `;

    for (const [key, description] of Object.entries(availableArchitectures)) {
      const selected = key === currentArchitecture ? 'selected' : '';
      controlsHtml += `<option value="${key}" ${selected}>${key.charAt(0).toUpperCase() + key.slice(1)}</option>`;
    }

    controlsHtml += `
        </select>
        <label style="display: flex; align-items: center; gap: 0.5em;">
          <input type="checkbox" id="multiAgentToggle" style="transform: scale(1.2);">
          <span style="font-weight: bold; color: #27ae60;">Enable Multi-Agent Processing</span>
        </label>
      </div>
    `;

    controlsDiv.innerHTML = controlsHtml;
    header.parentNode.insertBefore(controlsDiv, header.nextSibling);

    // Add event listeners
    const architectureSelect = document.getElementById('architectureSelect');

    architectureSelect.onchange = async () => {
      const newArchitecture = architectureSelect.value;

      try {
        const response = await fetch('http://localhost:5001/set_architecture', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ architecture: newArchitecture })
        });

        const result = await response.json();

        if (result.success) {
          currentArchitecture = newArchitecture;
          console.log(`Architecture changed to: ${newArchitecture}`);
        } else {
          console.error('Failed to change architecture:', result.error);
          architectureSelect.value = currentArchitecture; // Revert selection
        }
      } catch (error) {
        console.error('Error changing architecture:', error);
        architectureSelect.value = currentArchitecture; // Revert selection
      }
    };

    // Add event listener for multi-agent toggle
    const multiAgentToggle = document.getElementById('multiAgentToggle');
    if (multiAgentToggle) {
      multiAgentToggle.onchange = () => {
        // Update all assignment sections when toggle changes
        const assignmentSections = document.querySelectorAll('.assignment-section');
        assignmentSections.forEach(section => {
          if (section.updateVisibility) {
            section.updateVisibility();
          }
        });
      };
    }
  }
}

// Initialize the app when the DOM is loaded
document.addEventListener('DOMContentLoaded', async function() {
  await loadTeamConfig();
  loadBacklog();
});
