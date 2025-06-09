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


    def analyze_email_professional(self, email_content: str, email_subject: str, colleague_info: Dict = None) -> Dict:
        """
        Analyze email for professional communication standards and Lake Macquarie Code of Conduct

        Args:
            email_content: The email body text
            email_subject: The email subject line
            colleague_info: Information about the recipient colleague

        Returns:
            Dictionary with analysis results
        """

        # Build colleague context
        colleague_context = ""
        if colleague_info:
            colleague_name = colleague_info.get('name', 'colleague')
            colleague_role = colleague_info.get('role', 'team member')
            colleague_personality = colleague_info.get('personality', 'professional colleague')
            colleague_context = f"""
    RECIPIENT CONTEXT:
    - Name: {colleague_name}
    - Role: {colleague_role}  
    - Communication Style: {colleague_personality}
    """

        # System prompt for Lake Macquarie Code of Conduct
        analysis_prompt = f"""You are a professional communication advisor for Lake Macquarie City Council staff.
    
    CRITICAL: Assess this email against Lake Macquarie Council's Code of Conduct standards:
    - Must not bring Council into disrepute
    - Must not involve intimidation or verbal abuse
    - Must not constitute harassment or bullying behaviour  
    - Must be lawful and honest
    - Must consider issues consistently, promptly and fairly
    
    Core Values: Leading at all levels, Working together, Shaping our future
    
    {colleague_context}
    
    EMAIL TO ANALYZE:
    Subject: {email_subject}
    
    Content: {email_content}
    
    Please analyze and respond with a JSON object containing:
    {{
        "overall_score": (number 1-10),
        "overall_feedback": "brief assessment",
        "code_compliance": {{
            "status": "PASS" or "FAIL",
            "issues": ["list of any compliance issues"],
            "risk_level": "low" or "medium" or "high"
        }},
        "channel_recommendation": {{
            "current": "email",
            "recommended": "email" or "phone" or "in_person",
            "reasoning": "explanation for recommendation"
        }},
        "disc_scores": {{
            "D": (number 1-10),
            "I": (number 1-10), 
            "S": (number 1-10),
            "C": (number 1-10)
        }},
        "disc_feedback": {{
            "D": "feedback on directness/assertiveness",
            "I": "feedback on interpersonal/collaborative tone",
            "S": "feedback on supportiveness/patience", 
            "C": "feedback on detail/accuracy"
        }},
        "suggestions": ["specific improvement recommendations"],
        "quick_tips": ["practical communication tips"]
    }}
    
    If email contains inappropriate language, harassment, or unprofessional content, score 1-3 and mark code_compliance as "FAIL"."""

        try:
            # Call Claude API for analysis
            claude_response = self._make_claude_request(analysis_prompt, max_tokens=1000)

            # Try to parse JSON response
            try:
                import json
                analysis_result = json.loads(claude_response)
                analysis_result['claude_powered'] = True
                analysis_result['analysis_timestamp'] = datetime.now().isoformat()
                return analysis_result
            except json.JSONDecodeError:
                # Fallback if Claude doesn't return valid JSON
                return {
                    "overall_score": 5,
                    "overall_feedback": "Analysis completed - see detailed feedback",
                    "code_compliance": {"status": "UNKNOWN", "issues": [], "risk_level": "medium"},
                    "channel_recommendation": {"current": "email", "recommended": "email",
                                               "reasoning": "Standard email communication"},
                    "disc_scores": {"D": 5, "I": 5, "S": 5, "C": 5},
                    "disc_feedback": {"D": "Analysis completed", "I": "Analysis completed", "S": "Analysis completed",
                                      "C": "Analysis completed"},
                    "suggestions": ["Review for professional tone", "Ensure clear action items"],
                    "quick_tips": ["Keep communication respectful", "Be clear and concise"],
                    "analysis_text": claude_response,
                    "claude_powered": True,
                    "analysis_timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            # Error fallback
            return {
                "overall_score": 1,
                "overall_feedback": f"Analysis failed: {str(e)}",
                "code_compliance": {"status": "ERROR", "issues": [f"Analysis error: {str(e)}"], "risk_level": "high"},
                "channel_recommendation": {"current": "email", "recommended": "in_person",
                                           "reasoning": "Analysis unavailable - consider direct discussion"},
                "disc_scores": {"D": 1, "I": 1, "S": 1, "C": 1},
                "disc_feedback": {"D": "Analysis failed", "I": "Analysis failed", "S": "Analysis failed",
                                  "C": "Analysis failed"},
                "suggestions": ["Analysis service unavailable", "Please try again later"],
                "quick_tips": ["practical communication tips"]
}}

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
