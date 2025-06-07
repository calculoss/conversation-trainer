"""
Conversation Trainer Backend API
NSW Local Government Professional Development Tool

Version: 1.0
Created: [Today's Date]
Purpose: Flask API to handle AI personality conversations
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import json
from datetime import datetime

# Create Flask application
app = Flask(__name__)
CORS(app)  # Allow frontend to talk to backend

# Basic configuration
app.config['DEBUG'] = True

# ============================================
# BASIC ROUTES (Test endpoints)
# ============================================

@app.route('/')
def home():
    """Main API information page"""
    return jsonify({
        'name': 'Conversation Trainer API',
        'version': '1.0',
        'description': 'AI conversation practice for NSW Local Government',
        'status': 'Development',
        'endpoints': {
            'health': '/health',
            'personalities': '/api/personalities',
            'conversations': '/api/conversations'
        }
    })

@app.route('/health')
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'message': 'Backend API is running successfully'
    })

# ============================================
# API ENDPOINTS (Will build these next)
# ============================================

@app.route('/api/personalities', methods=['GET', 'POST'])
def handle_personalities():
    """Handle personality creation and retrieval"""
    if request.method == 'GET':
        # TODO: Return list of available personalities
        return jsonify({
            'personalities': [],
            'message': 'Personality management coming soon'
        })
    
    if request.method == 'POST':
        # TODO: Create new personality
        return jsonify({
            'success': True,
            'message': 'Personality creation coming soon'
        })

@app.route('/api/conversations', methods=['GET', 'POST'])
def handle_conversations():
    """Handle conversation starting and management"""
    if request.method == 'GET':
        # TODO: Return conversation history
        return jsonify({
            'conversations': [],
            'message': 'Conversation history coming soon'
        })
    
    if request.method == 'POST':
        # TODO: Start new conversation
        return jsonify({
            'success': True,
            'message': 'Conversation starting coming soon'
        })

# ============================================
# RUN APPLICATION
# ============================================

if __name__ == '__main__':
    print("🚀 Starting Conversation Trainer Backend...")
    print("📍 Local development server")
    print("🔗 Frontend should connect to this API")
    
    # Run the Flask development server
    app.run(
        host='0.0.0.0',  # Allow external connections
        port=5000,       # Standard Flask port
        debug=True       # Show detailed errors
    )
