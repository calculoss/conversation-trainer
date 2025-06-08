"""
Conversation Trainer Backend API - CLEAN VERSION
NSW Local Government Professional Development Tool

Version: 2.1 - Now with Custom Character Support!
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import uuid  # ADDED: Missing import
import requests  # ADDED: Missing import
from datetime import datetime
import sys

# Add our models to the path so we can import them
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our custom models and Claude integration
try:
    from models.personality import Personality, create_skeptical_councillor, create_frustrated_resident
    from models.conversation import Conversation, create_budget_cut_scenario, create_angry_resident_scenario
    from api.claude_integration import ClaudeAPIClient, ConversationOrchestrator, test_claude_integration

    print("✅ Successfully imported all custom modules")
except ImportError as e:
    print(f"⚠️  Import error: {e}")
    print("Some features may not work until all files are created")

# Create Flask application
app = Flask(__name__)
CORS(app)  # Allow frontend to talk to backend

# Configuration
app.config['DEBUG'] = True

# Initialize Claude integration
from config import get_config, check_environment

config = get_config()

# Check environment on startup
if not check_environment():
    print("❌ Configuration errors found. Please fix before continuing.")

# Initialize Claude integration with API key from config
claude_client = None
orchestrator = None

try:
    claude_client = ClaudeAPIClient(api_key=config.CLAUDE_API_KEY)
    orchestrator = ConversationOrchestrator(claude_client)
    print("✅ Claude integration initialized")
except Exception as e:
    print(f"⚠️  Claude integration error: {e}")


# ============================================
# CUSTOM CHARACTER FUNCTIONS (MOVED TO TOP LEVEL)
# ============================================

def create_custom_character_prompt(character_data, scenario_description, custom_scenario=None):
    """Create AI prompt for custom character with enhanced scenario support"""
    name = character_data.get('name', 'Custom Character')
    personality = character_data.get('personality', 'Professional colleague')
    motivations = character_data.get('motivations', 'Standard workplace goals')

    # Build enhanced context if we have a custom scenario
    if custom_scenario:
        scenario_context = f"""
MEETING CONTEXT:
- Title: {custom_scenario.get('title', 'Custom Meeting')}
- Background: {custom_scenario.get('context', 'Standard meeting context')}
- User's Objective: {custom_scenario.get('objective', 'General discussion')}
- Expected Challenges: {custom_scenario.get('challenges', 'Normal workplace dynamics')}
- Meeting Type: {custom_scenario.get('type', 'General meeting')}

SCENARIO DESCRIPTION: {scenario_description}"""
    else:
        scenario_context = f"SCENARIO: {scenario_description}"

    prompt = f"""You are roleplaying as {name} in a workplace conversation.

CHARACTER DETAILS:
- Name/Role: {name}
- Personality & Behavior: {personality}
- What they care about: {motivations}

{scenario_context}

ROLEPLAY INSTRUCTIONS:
1. Stay completely in character as {name}
2. Respond based on your personality and motivations
3. Be aware of the meeting context and react accordingly
4. Show realistic workplace behaviors based on your character traits
5. Challenge the user appropriately based on your character's nature and the scenario
6. Remember your agenda and priorities in this specific meeting context

Begin the meeting naturally, acknowledging the context and your role."""

    return prompt


def get_ai_opening_message(character_prompt):
    """Get opening message from Claude AI"""
    try:
        api_key = os.getenv('CLAUDE_API_KEY')
        if not api_key:
            return "Hello, I'm ready to begin our conversation."

        headers = {
            'x-api-key': api_key,
            'Content-Type': 'application/json'
        }

        request_data = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 200,
            "messages": [
                {
                    "role": "user",
                    "content": character_prompt
                }
            ]
        }

        response = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers=headers,
            json=request_data,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            return result['content'][0]['text']
        else:
            print(f"Claude API error: {response.status_code}")
            return "Hello, I'm ready to begin our conversation."

    except Exception as e:
        print(f"Error getting opening message: {e}")
        return "Hello, I'm ready to begin our conversation."


# ============================================
# BASIC HEALTH CHECK ROUTES
# ============================================

@app.route('/')
def home():
    """Main API information page"""
    return jsonify({
        'name': 'Conversation Trainer API',
        'version': '2.1',
        'description': 'AI conversation practice for NSW Local Government',
        'status': 'Production Ready',
        'features': [
            'AI personality conversations',
            'Custom character creation',  # ADDED
            'Local government scenarios',
            'Conversation history',
            'Performance analytics'
        ],
        'endpoints': {
            'health': '/health',
            'claude_test': '/test-claude',
            'personalities': '/api/personalities',
            'conversations': '/api/conversations',
            'start_conversation': '/api/conversations/start',
            'send_message': '/api/conversations/message'
        }
    })


@app.route('/health')
def health_check():
    """Detailed health check"""
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'components': {
            'flask_app': 'healthy',
            'personality_model': 'unknown',
            'conversation_model': 'unknown',
            'claude_integration': 'unknown'
        }
    }

    # Test our models
    try:
        test_personality = Personality("Test", "Test Role")
        health_status['components']['personality_model'] = 'healthy'
    except:
        health_status['components']['personality_model'] = 'error'

    try:
        test_conversation = Conversation("test_user", "test_scenario")
        health_status['components']['conversation_model'] = 'healthy'
    except:
        health_status['components']['conversation_model'] = 'error'

    # Test Claude connection
    if claude_client:
        try:
            claude_test = claude_client.test_connection()
            health_status['components']['claude_integration'] = 'healthy' if claude_test['success'] else 'error'
            health_status['claude_test_result'] = claude_test
        except:
            health_status['components']['claude_integration'] = 'error'

    return jsonify(health_status)


@app.route('/test-claude')
def test_claude_endpoint():
    """Test Claude API connection"""
    if not claude_client:
        return jsonify({
            'success': False,
            'message': 'Claude client not initialized'
        })

    result = claude_client.test_connection()
    return jsonify(result)


# ============================================
# PERSONALITY MANAGEMENT
# ============================================

# Replace the get_personalities function in your app.py with this updated version

@app.route('/api/personalities', methods=['GET'])
def get_personalities():
    """Get list of available personalities - Updated with DISC personalities"""
    try:
        personalities = [
            # NEW DISC-BASED NSW LOCAL GOVERNMENT PERSONALITIES
            {
                'id': 'infrastructure_engineer',
                'name': 'Terry Mitchell',
                'role': 'Senior Infrastructure Engineer',
                'description': 'Technical expert, detail-oriented, skeptical of quick fixes. Expects thorough engineering analysis.',
                'department': 'Engineering & Infrastructure',
                'difficulty': 'Hard',
                'disc_profile': {'D': 65, 'I': 25, 'S': 35, 'C': 85}
            },
            {
                'id': 'community_engagement',
                'name': 'Sarah Chen',
                'role': 'Community Engagement Officer',
                'description': 'People-focused, enthusiastic about community consultation. Diplomatic but can be overly optimistic.',
                'department': 'Community Services',
                'difficulty': 'Medium',
                'disc_profile': {'D': 35, 'I': 85, 'S': 70, 'C': 40}
            },
            {
                'id': 'budget_director',
                'name': 'David Walsh',
                'role': 'Budget & Finance Director',
                'description': 'Numbers-driven, direct about financial constraints. Challenges spending proposals with detailed questions.',
                'department': 'Finance',
                'difficulty': 'Hard',
                'disc_profile': {'D': 80, 'I': 20, 'S': 30, 'C': 90}
            },
            {
                'id': 'union_rep',
                'name': 'Maria Santos',
                'role': 'Union Representative',
                'description': 'Assertive advocate for workers\' rights. Direct communicator who challenges management decisions affecting staff.',
                'department': 'Employee Relations',
                'difficulty': 'Hard',
                'disc_profile': {'D': 85, 'I': 60, 'S': 45, 'C': 55}
            },
            {
                'id': 'councillor_thompson',
                'name': 'Robert Thompson',
                'role': 'Long-term Councillor',
                'description': 'Steady, consensus-building approach. Values tradition and established processes. Asks thoughtful questions.',
                'department': 'Council',
                'difficulty': 'Medium',
                'disc_profile': {'D': 40, 'I': 50, 'S': 85, 'C': 65}
            },
            {
                'id': 'strategic_planner',
                'name': 'Emily Kim',
                'role': 'Strategic Planner',
                'description': 'Analytical yet enthusiastic about new ideas. Balances data-driven decisions with stakeholder engagement.',
                'department': 'Strategy & Planning',
                'difficulty': 'Medium',
                'disc_profile': {'D': 50, 'I': 75, 'S': 45, 'C': 80}
            },

            # LEGACY PERSONALITIES (for backward compatibility)
            {
                'id': 'skeptical_councillor',
                'name': 'Councillor Margaret Stevens',
                'role': 'Budget-focused Councillor',
                'description': 'A skeptical councillor who focuses on budget implications and detailed justifications',
                'department': 'Council',
                'difficulty': 'Medium-Hard'
            },
            {
                'id': 'frustrated_resident',
                'name': 'Robert Chen',
                'role': 'Local Business Owner',
                'description': 'A frustrated community member concerned about service delivery and value for money',
                'department': 'Community',
                'difficulty': 'Medium'
            }
        ]

        return jsonify({
            'success': True,
            'personalities': personalities,
            'count': len(personalities),
            'disc_personalities': [p for p in personalities if 'disc_profile' in p],
            'legacy_personalities': [p for p in personalities if 'disc_profile' not in p]
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'personalities': []
        })


# ============================================
# CONVERSATION MANAGEMENT (UPDATED FOR CUSTOM CHARACTERS)
# ============================================

# Replace the start_conversation function in your app.py with this updated version

@app.route('/api/conversations/start', methods=['POST'])
def start_conversation():
    """Start conversation with custom character and scenario support + DISC personalities"""
    try:
        data = request.json
        print(f"📥 Start conversation request: {data}")

        user_name = data.get('user_name', 'user')
        personality_type = data.get('personality_type')
        scenario = data.get('scenario', 'Practice conversation')
        custom_character = data.get('custom_character')
        custom_scenario = data.get('custom_scenario')

        conversation_id = str(uuid.uuid4())

        # Handle custom characters vs preset characters
        if personality_type == 'custom_character' and custom_character:
            print(f"🎭 Creating custom character: {custom_character.get('name')}")
            personality_name = custom_character.get('name', 'Custom Character')
            character_prompt = create_custom_character_prompt(custom_character, scenario, custom_scenario)
        else:
            print(f"🎭 Using preset character: {personality_type}")

            # Enhanced preset characters with custom scenario support
            if custom_scenario:
                scenario_context = f"""
CUSTOM MEETING CONTEXT:
- {custom_scenario.get('title', 'Meeting')}
- Background: {custom_scenario.get('context', '')}
- User's Goal: {custom_scenario.get('objective', '')}
- Challenges: {custom_scenario.get('challenges', '')}

{scenario}"""
            else:
                scenario_context = scenario

            # COMPLETE DISC-BASED PERSONALITY MAPPING
            personalities = {
                # NEW: NSW Local Government DISC-Based Personalities
                'infrastructure_engineer': {
                    'name': 'Terry Mitchell',
                    'prompt': f"""You are Terry Mitchell, Senior Infrastructure Engineer at NSW Local Council.

DISC PROFILE: High C (85%), Moderate D (65%), Low I (25%), Low S (35%)
- Cautious, analytical, technically precise
- Skeptical of quick fixes and shortcuts
- Expects thorough engineering analysis and data
- Direct when technical standards are compromised
- Reserved in social interactions, prefers facts over feelings

PERSONALITY TRAITS:
- Technical expert who values precision and thoroughness
- Challenges proposals with detailed technical questions
- Skeptical of solutions that haven't been properly analysed
- Expects comprehensive engineering reports and data
- Can be blunt when technical standards are at risk

SCENARIO: {scenario_context}

Stay completely in character as Terry. Focus on technical details, proper engineering processes, and data-driven decisions.
Begin the conversation naturally, introducing yourself and your engineering perspective."""
                },

                'community_engagement': {
                    'name': 'Sarah Chen',
                    'prompt': f"""You are Sarah Chen, Community Engagement Officer at NSW Local Council.

DISC PROFILE: High I (85%), High S (70%), Moderate C (40%), Moderate D (35%)
- Enthusiastic, people-focused, optimistic about consultation
- Values community input and stakeholder relationships
- Sometimes overly idealistic about consensus-building
- Diplomatic but can be frustrated by purely technical approaches

PERSONALITY TRAITS:
- Passionate about community consultation and engagement
- Optimistic about finding solutions that work for everyone
- Values stakeholder relationships and collaborative processes
- Sometimes underestimates practical constraints
- Enthusiastic communicator who builds rapport easily

SCENARIO: {scenario_context}

Stay completely in character as Sarah. Focus on community impact, stakeholder engagement, and collaborative solutions.
Begin the conversation naturally, introducing yourself and your community perspective."""
                },

                'budget_director': {
                    'name': 'David Walsh',
                    'prompt': f"""You are David Walsh, Budget & Finance Director at NSW Local Council.

DISC PROFILE: High C (90%), High D (80%), Low I (20%), Low S (30%)
- Extremely analytical, data-driven, direct about financial constraints
- Results-oriented with little patience for unfunded proposals
- Challenges spending with detailed financial questions
- Can be blunt about budget realities

PERSONALITY TRAITS:
- Numbers-driven decision maker who demands financial justification
- Direct communicator about budget constraints and fiscal responsibility
- Challenges all spending proposals with detailed cost-benefit analysis
- Impatient with vague or poorly justified budget requests
- Focused on long-term financial sustainability

SCENARIO: {scenario_context}

Stay completely in character as David. Focus on budget implications, cost-benefit analysis, and fiscal responsibility.
Begin the conversation naturally, introducing yourself and your financial perspective."""
                },

                'union_rep': {
                    'name': 'Maria Santos',
                    'prompt': f"""You are Maria Santos, Union Representative for NSW Local Council employees.

DISC PROFILE: High D (85%), Moderate I (60%), Moderate C (55%), Moderate S (45%)
- Assertive advocate for workers' rights and workplace conditions
- Direct communicator who challenges management decisions affecting staff
- Strong negotiator who pushes for staff benefits and fair treatment
- Knowledgeable about workplace agreements and regulations

PERSONALITY TRAITS:
- Fierce advocate for employee rights and workplace conditions
- Challenges management decisions that impact staff welfare
- Negotiates firmly but professionally for better conditions
- Well-versed in awards, agreements, and workplace law
- Direct communicator who speaks up for employees

SCENARIO: {scenario_context}

Stay completely in character as Maria. Focus on staff impact, workplace conditions, and employee advocacy.
Begin the conversation naturally, introducing yourself and your union perspective."""
                },

                'councillor_thompson': {
                    'name': 'Robert Thompson',
                    'prompt': f"""You are Robert Thompson, long-term Councillor for NSW Local Council.

DISC PROFILE: High S (85%), Moderate C (65%), Moderate I (50%), Moderate D (40%)
- Steady, consensus-building approach to council decisions
- Values tradition, established processes, and community stability
- Thoughtful questioner who seeks collaborative solutions
- Cautious about rapid changes, prefers gradual implementation

PERSONALITY TRAITS:
- Experienced councillor who values stability and consensus
- Thoughtful decision-maker who considers long-term community impact
- Asks probing questions to understand all perspectives
- Prefers collaborative approaches and gradual change
- Respects established processes and community traditions

SCENARIO: {scenario_context}

Stay completely in character as Robert. Focus on community impact, consensus-building, and thoughtful decision-making.
Begin the conversation naturally, introducing yourself and your councillor perspective."""
                },

                'strategic_planner': {
                    'name': 'Emily Kim',
                    'prompt': f"""You are Emily Kim, Strategic Planner at NSW Local Council.

DISC PROFILE: High C (80%), High I (75%), Moderate D (50%), Moderate S (45%)
- Analytical yet enthusiastic about new ideas and innovation
- Balances data-driven decisions with stakeholder engagement
- Forward-thinking but methodical in planning approaches
- Values both research and community input in strategic decisions

PERSONALITY TRAITS:
- Strategic thinker who combines analysis with stakeholder engagement
- Enthusiastic about innovative approaches and long-term planning
- Balances data analysis with community consultation
- Forward-thinking but methodical in implementation
- Values both quantitative research and qualitative feedback

SCENARIO: {scenario_context}

Stay completely in character as Emily. Focus on strategic implications, long-term planning, and balanced decision-making.
Begin the conversation naturally, introducing yourself and your strategic perspective."""
                },

                # LEGACY PERSONALITIES (maintain backward compatibility)
                'skeptical_councillor': {
                    'name': 'Councillor Margaret Stevens',
                    'prompt': f"""You are Councillor Margaret Stevens, a budget-focused local councillor. 
                    You are skeptical, detail-oriented, and expect thorough justifications for spending.

                    SCENARIO: {scenario_context}

                    Stay in character and respond to the specific meeting context. Be particularly focused on budget implications and ratepayer value.
                    Introduce yourself and begin the conversation."""
                },
                'frustrated_resident': {
                    'name': 'Robert Chen',
                    'prompt': f"""You are Robert Chen, a local business owner frustrated with council services. 
                    You are articulate but frustrated, concerned about value for rates paid.

                    SCENARIO: {scenario_context}

                    Stay in character and respond to the specific meeting context. Focus on service delivery and value for money.
                    Introduce yourself and begin the conversation."""
                }
            }

            # Get personality data with logging
            if personality_type in personalities:
                personality_data = personalities[personality_type]
                print(f"✅ Found personality: {personality_type} -> {personality_data['name']}")
            else:
                print(f"⚠️ Unknown personality type: {personality_type}, defaulting to frustrated_resident")
                personality_data = personalities['frustrated_resident']

            personality_name = personality_data['name']
            character_prompt = personality_data['prompt']

        print(f"🤖 Getting opening message from Claude for {personality_name}...")
        opening_message = get_ai_opening_message(character_prompt)
        print(f"✅ Got opening message: {opening_message[:50]}...")

        # Store conversation data (include custom scenario info)
        conversation_data = {
            'personality': {
                'name': personality_name,
                'type': personality_type,
                'prompt': character_prompt,
                'custom_character': custom_character if personality_type == 'custom_character' else None
            },
            'scenario': scenario,
            'custom_scenario': custom_scenario,
            'created_at': datetime.now().isoformat()
        }

        result = {
            "success": True,
            "conversation_id": conversation_id,
            "conversation_data": conversation_data,
            "personality_name": personality_name,
            "opening_message": opening_message,
            "timestamp": datetime.now().isoformat()
        }

        # Log successful creation
        if custom_scenario:
            print(f"✅ Started custom scenario: {custom_scenario.get('title', 'Untitled')}")
        if custom_character:
            print(f"✅ Started with custom character: {custom_character.get('name', 'Unnamed')}")

        print(f"✅ Conversation started successfully with {personality_name}")
        return jsonify(result)

    except Exception as e:
        print(f"❌ Error starting conversation: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# REPLACE the conversation_message function in your app.py with this fixed version:

@app.route('/api/conversations/message', methods=['POST'])
def conversation_message():
    """Handle conversation messages - FIXED for Claude API"""
    try:
        data = request.json
        print(f"📥 Message request received")

        user_message = data.get('user_message')
        personality_data = data.get('personality_data')
        conversation_history = data.get('conversation_history', [])

        if not user_message or not personality_data:
            return jsonify({
                "success": False,
                "error": "Missing user_message or personality_data"
            }), 400

        print(f"💬 User message: {user_message}")
        print(f"🎭 Character: {personality_data.get('name', 'Unknown')}")

        # Get character info
        character_name = personality_data.get('name', 'AI Assistant')
        character_prompt = personality_data.get('prompt', '')

        # FIXED: Build conversation context properly for Claude
        # Start with character instructions
        system_prompt = f"""You are {character_name}. {character_prompt}

Continue this conversation naturally as {character_name}. Stay in character and respond based on your personality."""

        # Build message history for Claude API
        messages = []

        # Add conversation history (recent messages only)
        for msg in conversation_history[-4:]:  # Last 4 messages to avoid token limits
            if msg.get('sender_type') == 'ai_personality':
                messages.append({
                    "role": "assistant",
                    "content": msg.get('content', '')
                })
            elif msg.get('sender_type') == 'user':
                messages.append({
                    "role": "user",
                    "content": msg.get('content', '')
                })

        # Add the current user message
        messages.append({
            "role": "user",
            "content": user_message
        })

        print(f"🔗 Sending {len(messages)} messages to Claude")

        # Get AI response with FIXED request format
        api_key = os.getenv('CLAUDE_API_KEY')
        if not api_key:
            return jsonify({
                "success": False,
                "error": "Claude API key not configured"
            }), 500

        headers = {
            'x-api-key': api_key,
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01'  # ADDED: Required header
        }

        # FIXED: Proper Claude API request format
        request_data = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 300,
            "system": system_prompt,  # FIXED: Use system parameter instead of user message
            "messages": messages
        }

        print(f"🤖 Calling Claude API...")
        response = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers=headers,
            json=request_data,
            timeout=30
        )

        print(f"🤖 Claude API response status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            ai_response = result['content'][0]['text']
            print(f"✅ Got AI response: {ai_response[:50]}...")

            return jsonify({
                "success": True,
                "ai_response": ai_response,
                "timestamp": datetime.now().isoformat()
            })
        else:
            # Log the exact error for debugging
            error_text = response.text
            print(f"❌ Claude API error {response.status_code}: {error_text}")

            # Return a helpful error message
            return jsonify({
                "success": False,
                "error": f"AI service temporarily unavailable (error {response.status_code})"
            }), 500

    except requests.exceptions.Timeout:
        print(f"❌ Claude API timeout")
        return jsonify({
            "success": False,
            "error": "AI service timeout - please try again"
        }), 500

    except Exception as e:
        print(f"❌ Error in conversation message: {e}")
        return jsonify({
            "success": False,
            "error": "Conversation service error - please try again"
        }), 500


# ============================================
# SCENARIO MANAGEMENT
# ============================================

@app.route('/api/scenarios', methods=['GET'])
def get_scenarios():
    """Get available practice scenarios"""
    try:
        scenarios = [
            {
                'id': 'budget_cuts',
                'title': 'Budget Reduction Discussion',
                'description': 'Practice explaining budget cuts while maintaining team morale',
                'type': 'preset'
            },
            {
                'id': 'angry_resident',
                'title': 'Challenging Resident Interaction',
                'description': 'Handle frustrated ratepayer complaints about service levels',
                'type': 'preset'
            },
            {
                'id': 'custom_scenario',
                'title': 'Create Custom Scenario',
                'description': 'Design your specific meeting situation',
                'type': 'custom'
            }
        ]

        return jsonify({
            'success': True,
            'scenarios': scenarios,
            'count': len(scenarios)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'scenarios': []
        })


# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'available_endpoints': [
            '/',
            '/health',
            '/test-claude',
            '/api/personalities',
            '/api/scenarios',
            '/api/conversations/start',
            '/api/conversations/message'
        ]
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': 'Check server logs for details'
    }), 500


@app.route('/api/scenarios/custom', methods=['POST'])
def save_custom_scenario():
    """Save a custom scenario for reuse"""
    try:
        data = request.json
        scenario_data = data.get('scenario')

        if not scenario_data:
            return jsonify({
                'success': False,
                'error': 'No scenario data provided'
            }), 400

        # Add ID and timestamp
        scenario_data['id'] = str(uuid.uuid4())
        scenario_data['created_at'] = datetime.now().isoformat()

        # For now, just return success (later we'll add persistent storage)
        print(f"📋 Custom scenario saved: {scenario_data.get('title', 'Untitled')}")

        return jsonify({
            'success': True,
            'scenario_id': scenario_data['id'],
            'message': 'Custom scenario saved successfully'
        })

    except Exception as e:
        print(f"❌ Error saving custom scenario: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================
# RUN APPLICATION
# ============================================

if __name__ == '__main__':
    print("🚀 Starting Conversation Trainer Backend v2.1...")
    print("📍 Custom Character Support Added!")
    print("🧠 AI personality conversations enabled")
    print("🏛️ NSW Local Government scenarios loaded")
    print("🔗 Frontend can connect to this API")
    print()
    print("Test endpoints:")
    print("  GET  / - API information")
    print("  GET  /health - Health check")
    print("  GET  /test-claude - Test Claude connection")
    print("  GET  /api/personalities - Available personalities")
    print("  POST /api/conversations/start - Start conversation")
    print("  POST /api/conversations/message - Send message")
    print()

    # Run the Flask development server
    port = int(os.environ.get('PORT', 5000))  # Railway provides PORT variable
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False  # Disable debug in production
    )