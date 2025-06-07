"""
Claude API Integration for Conversation Trainer
This is the magic that makes AI personalities come alive!
"""

import requests
import json
import os
from typing import Dict, List, Optional
from datetime import datetime

class ClaudeAPIClient:
    """
    Handles all communication with Claude API
    Think of this as the phone system that calls Claude
    """
    
    def __init__(self, api_key: str = None):
        """Initialize Claude API client"""
        self.api_key = api_key or os.getenv('CLAUDE_API_KEY')
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.model = "claude-3-sonnet-20240229"  # Using Claude 3 Sonnet
        
        if not self.api_key:
            print("⚠️  WARNING: No Claude API key found!")
            print("   Set CLAUDE_API_KEY environment variable")
    
    def test_connection(self) -> Dict:
        """Test if we can connect to Claude API"""
        try:
            response = self._make_claude_request(
                "Hello! Please respond with 'API connection successful' if you can see this message.",
                max_tokens=50
            )
            return {
                'success': True,
                'message': 'Claude API connection working',
                'response': response
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Claude API connection failed: {str(e)}',
                'response': None
            }
    
    def get_personality_response(self, personality_prompt: str, conversation_history: str, user_message: str) -> Dict:
        """
        Get Claude to respond as a specific personality
        This is where the magic happens!
        
        Args:
            personality_prompt: The full personality description for Claude
            conversation_history: Previous messages for context
            user_message: What the user just said
            
        Returns:
            Dictionary with Claude's response or error info
        """
        
        # Build the complete prompt for Claude
        full_prompt = f"""{personality_prompt}

{conversation_history}

USER: {user_message}

Respond in character. Keep your response natural and conversational (2-4 sentences typically). Stay true to your personality traits, background, and the local government context."""

        try:
            # Call Claude API
            claude_response = self._make_claude_request(full_prompt, max_tokens=300)
            
            return {
                'success': True,
                'response': claude_response,
                'timestamp': datetime.now().isoformat(),
                'prompt_used': full_prompt  # For debugging
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': None,
                'timestamp': datetime.now().isoformat()
            }
    
    def _make_claude_request(self, prompt: str, max_tokens: int = 300) -> str:
        """
        Make the actual HTTP request to Claude API
        This is the technical plumbing
        """
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key,
            'anthropic-version': '2023-06-01'
        }
        
        data = {
            'model': self.model,
            'max_tokens': max_tokens,
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
        }
        
        response = requests.post(
            self.base_url,
            headers=headers,
            json=data,
            timeout=30  # 30 second timeout
        )
        
        if response.status_code != 200:
            raise Exception(f"Claude API error: {response.status_code} - {response.text}")
        
        response_data = response.json()
        return response_data['content'][0]['text']

# ============================================
# CONVERSATION ORCHESTRATOR
# ============================================

class ConversationOrchestrator:
    """
    Manages the flow of conversations between users and AI personalities
    Think of this as the conversation coordinator
    """
    
    def __init__(self, claude_client: ClaudeAPIClient):
        """Initialize with Claude API client"""
        self.claude = claude_client
        self.active_conversations = {}  # Store active conversation state
    
    def start_conversation(self, personality, scenario_context: str, user_name: str) -> Dict:
        """
        Start a new conversation with an AI personality
        
        Args:
            personality: Personality object
            scenario_context: Description of the practice scenario
            user_name: Name of the user practicing
            
        Returns:
            Dictionary with conversation start info and first AI message
        """
        try:
            # Create personality prompt
            personality_prompt = personality.generate_claude_prompt(scenario_context)
            
            # Create opening message from AI personality
            opening_prompt = f"""{personality_prompt}

SCENARIO: {scenario_context}

You are starting a conversation. Introduce yourself briefly and set the scene based on the scenario. Keep it natural and in character. This is the opening of the practice conversation."""

            # Get Claude's opening response
            claude_response = self.claude._make_claude_request(opening_prompt, max_tokens=200)
            
            return {
                'success': True,
                'conversation_id': f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'personality_name': personality.name,
                'scenario': scenario_context,
                'opening_message': claude_response,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'conversation_id': None
            }
    
    def continue_conversation(self, personality, conversation_history: str, user_message: str) -> Dict:
        """
        Continue an existing conversation
        
        Args:
            personality: Personality object  
            conversation_history: Previous messages
            user_message: User's new message
            
        Returns:
            Dictionary with AI personality's response
        """
        
        # Generate personality prompt
        personality_prompt = personality.generate_claude_prompt("Continue this conversation")
        
        # Get Claude's response
        return self.claude.get_personality_response(
            personality_prompt,
            conversation_history,
            user_message
        )

# ============================================
# HELPER FUNCTIONS
# ============================================

def create_claude_client() -> ClaudeAPIClient:
    """Create and return a Claude API client"""
    return ClaudeAPIClient()

def test_claude_integration() -> Dict:
    """Test the Claude integration setup"""
    client = create_claude_client()
    return client.test_connection()

# ============================================
# EXAMPLE USAGE (for testing)
# ============================================

if __name__ == "__main__":
    """
    Test script - run this file directly to test Claude integration
    Usage: python claude_integration.py
    """
    print("🧪 Testing Claude Integration...")
    
    # Test connection
    result = test_claude_integration()
    print(f"Connection test: {result}")
    
    if result['success']:
        print("✅ Claude API is working!")
        print(f"Response: {result['response']}")
    else:
        print("❌ Claude API connection failed")
        print("Make sure CLAUDE_API_KEY environment variable is set")
