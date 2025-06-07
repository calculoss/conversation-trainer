"""
Conversation Trainer Backend API - FULL VERSION
NSW Local Government Professional Development Tool

Version: 2.0 - Now with working AI integration!
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import json
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
claude_client = None
orchestrator = None

try:
    claude_client = ClaudeAPIClient()
    orchestrator = ConversationOrchestrator(claude_client)
    print("✅ Claude integration initialized")
except Exception as e:
    print(f"⚠️  Claude integration error: {e}")

# ============================================
# BASIC HEALTH CHECK ROUTES
# ============================================

@app.route('/')
def home():
    """Main API information page"""
    return jsonify({
        'name': 'Conversation Trainer API',
        'version': '2.0',
        'description': 'AI conversation practice for NSW Local Government',
        'status': 'Production Ready',
        'features': [
            'AI personality conversations',
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

@app.route('/api/personalities', methods=['GET'])
def get_personalities():
    """Get list of available personalities"""
    try:
        # For now, return pre-built personalities
        personalities = []
        
        # Create sample personalities
        councillor = create_skeptical_councillor()
        resident = create_frustrated_resident()
        
        personalities.append({
            'id': councillor.id,
            'name': councillor.name,
            'role': councillor.role,
            'description': f"A {councillor.communication_style} {councillor.role.lower()} who focuses on {', '.join(councillor.objectives[:2])}",
            'department': councillor.department,
            'difficulty': 'Medium-Hard'
        })
        
        personalities.append({
            'id': resident.id,
            'name': resident.name,
            'role': resident.role,
            'description': f"A {resident.communication_style} community member concerned about {', '.join(resident.objectives[:2])}",
            'department': resident.department,
            'difficulty': 'Medium'
        })
        
        return jsonify({
            'success': True,
            'personalities': personalities,
            'count': len(personalities)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'personalities': []
        })

# ============================================
# CONVERSATION MANAGEMENT  
# ============================================

@app.route('/api/conversations/start', methods=['POST'])
def start_conversation():
    """Start a new conversation with an AI personality"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_name', 'personality_type', 'scenario']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                })
        
        # Create personality based on type
        if data['personality_type'] == 'skeptical_councillor':
            personality = create_skeptical_councillor()
        elif data['personality_type'] == 'frustrated_resident':
            personality = create_frustrated_resident()
        else:
            return jsonify({
                'success': False,
                'error': f'Unknown personality type: {data["personality_type"]}'
            })
        
        # Start conversation using orchestrator
        if not orchestrator:
            return jsonify({
                'success': False,
                'error': 'Conversation orchestrator not available'
            })
        
        result = orchestrator.start_conversation(
            personality,
            data['scenario'],
            data['user_name']
        )
        
        if result['success']:
            # Store conversation info for later (in production, save to database)
            conversation_data = {
                'conversation_id': result['conversation_id'],
                'personality': personality.to_dict(),
                'scenario': data['scenario'],
                'user_name': data['user_name'],
                'messages': [
                    {
                        'sender': personality.name,
                        'content': result['opening_message'],
                        'timestamp': result['timestamp'],
                        'sender_type': 'ai_personality'
                    }
                ]
            }
            
            return jsonify({
                'success': True,
                'conversation_id': result['conversation_id'],
                'personality_name': personality.name,
                'opening_message': result['opening_message'],
                'conversation_data': conversation_data
            })
        else:
            return jsonify(result)
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/conversations/message', methods=['POST'])
def send_message():
    """Send a message in an ongoing conversation"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['conversation_id', 'user_message', 'personality_data']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                })
        
        # Recreate personality from data
        personality = Personality.from_dict(data['personality_data'])
        
        # Build conversation history
        conversation_history = "CONVERSATION HISTORY:\n"
        for msg in data.get('conversation_history', []):
            if msg['sender_type'] == 'user':
                conversation_history += f"USER: {msg['content']}\n"
            else:
                conversation_history += f"{msg['sender']}: {msg['content']}\n"
        
        # Get AI response
        if not orchestrator:
            return jsonify({
                'success': False,
                'error': 'Conversation orchestrator not available'
            })
        
        result = orchestrator.continue_conversation(
            personality,
            conversation_history,
            data['user_message']
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'ai_response': result['response'],
                'timestamp': result['timestamp']
            })
        else:
            return jsonify(result)
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

# ============================================
# SCENARIO MANAGEMENT
# ============================================

@app.route('/api/scenarios', methods=['GET'])
def get_scenarios():
    """Get available practice scenarios"""
    try:
        scenarios = []
        
        # Add pre-built scenarios
        scenarios.append(create_budget_cut_scenario())
        scenarios.append(create_angry_resident_scenario())
        
        return jsonify({
            'success': True,
            'scenarios': scenarios,
            'count': len(scenarios)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': st
