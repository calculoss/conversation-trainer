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
    # EMAIL ANALYSIS EXTENSION FOR ClaudeAPIClient
    # Add this method to your existing ClaudeAPIClient class
    # ============================================

    def analyze_email(self, email_data: Dict) -> Dict:
        """
        Analyze email content for professional effectiveness and compliance

        Args:
            email_data: Dictionary containing:
                - subject: Email subject line
                - content: Email body content
                - colleague: Optional colleague info (name, role, personality)
                - analysis_type: 'outgoing' or 'incoming'
                - context: Additional context

        Returns:
            Dictionary with analysis results or error info
        """
        try:
            # Build the analysis prompt
            system_prompt = self._build_email_system_prompt(email_data)
            user_prompt = self._build_email_user_prompt(email_data)

            # Combine prompts for Claude
            full_prompt = f"""{system_prompt}

    {user_prompt}"""

            # Call Claude with longer response limit for detailed analysis
            claude_response = self._make_claude_request(full_prompt, max_tokens=2000)

            # Parse the JSON response from Claude
            analysis_result = self._parse_email_analysis_response(claude_response, email_data)

            return {
                'success': True,
                'analysis': analysis_result,
                'timestamp': datetime.now().isoformat(),
                'claude_powered': True
            }

        except Exception as e:
            # Fallback to pattern analysis if Claude fails
            try:
                fallback_result = self._generate_fallback_email_analysis(email_data)
                return {
                    'success': True,
                    'analysis': fallback_result,
                    'timestamp': datetime.now().isoformat(),
                    'claude_powered': False,
                    'fallback_used': True,
                    'error_message': f'Claude API error: {str(e)}'
                }
            except Exception as fallback_error:
                return {
                    'success': False,
                    'error': f'Analysis failed: {str(e)}. Fallback also failed: {str(fallback_error)}',
                    'timestamp': datetime.now().isoformat()
                }

    def _build_email_system_prompt(self, email_data: Dict) -> str:
        """Build system prompt for email analysis"""
        colleague = email_data.get('colleague', {})
        analysis_type = email_data.get('analysis_type', 'outgoing')

        return f"""You are an expert communication analyst for NSW Local Government, specifically trained in professional workplace email assessment. Your role is to analyze {analysis_type} emails for effectiveness, appropriateness, and compliance with professional standards.

    CONTEXT:
    - Organization: Lake Macquarie City Council
    - Core Values: Leading at all levels, Working together, Shaping our future
    - Communication Standards: Professional, respectful, ethical, and effective

    COLLEAGUE CONTEXT:
    {f'''- Name: {colleague.get('name', 'Unknown')}
    - Role: {colleague.get('role', 'Unknown')}
    - Personality: {colleague.get('personality', 'Professional colleague')}''' if colleague else 'No specific colleague context provided'}

    ANALYSIS REQUIREMENTS:
    1. CODE OF CONDUCT COMPLIANCE: Check for any language or tone that could be considered:
       - Harassment or intimidation
       - Discriminatory or offensive  
       - Unprofessional or inappropriate
       - Bullying or threatening

    2. PROFESSIONAL EFFECTIVENESS: Assess:
       - Clarity and conciseness
       - Professional tone and respect
       - Action clarity and deadlines
       - Appropriate level of formality

    3. COMMUNICATION CHANNEL ASSESSMENT: Determine if email is the most appropriate channel

    4. {'RESPONSE STRATEGY: Recommend appropriate response approach and tone' if analysis_type == 'incoming' else 'IMPROVEMENT RECOMMENDATIONS: Suggest specific improvements'}

    Provide structured JSON analysis with scores, specific feedback, and actionable recommendations."""

    def _build_email_user_prompt(self, email_data: Dict) -> str:
        """Build user prompt with email content"""
        subject = email_data.get('subject', '[No Subject]')
        content = email_data.get('content', '')
        colleague = email_data.get('colleague', {})
        analysis_type = email_data.get('analysis_type', 'outgoing')

        if analysis_type == 'incoming':
            return f"""Please analyze this INCOMING email and provide response guidance:

    SUBJECT: {subject}

    EMAIL CONTENT:
    {content}

    FROM: {colleague.get('name', 'Colleague')} ({colleague.get('role', 'Unknown role')})

    Provide analysis in this JSON format:
    {{
        "overall_assessment": {{
            "appropriateness_score": [1-10],
            "professional_tone": "[appropriate/concerning/inappropriate]",
            "urgency_level": "[low/normal/high/urgent]",
            "main_intent": "[brief description]"
        }},
        "code_of_conduct_compliance": {{
            "overall_compliance": "[compliant/concerning/violation]",
            "specific_issues": ["list any problems"],
            "risk_level": "[low/medium/high]"
        }},
        "response_strategy": {{
            "recommended_channel": "[email/phone/meeting/no_response]",
            "response_tone": "[formal/collaborative/direct/supportive]",
            "key_points_to_address": ["list main points"],
            "suggested_approach": "[detailed guidance]"
        }},
        "recommendations": [
            {{
                "category": "[response_strategy/tone/channel/urgency]",
                "suggestion": "[specific recommendation]",
                "rationale": "[why this is important]"
            }}
        ]
    }}"""
        else:
            return f"""Please analyze this OUTGOING email for professional effectiveness:

    TO: {colleague.get('name', 'Colleague')} ({colleague.get('role', 'Unknown role')})
    SUBJECT: {subject}

    EMAIL CONTENT:
    {content}

    Provide analysis in this JSON format:
    {{
        "overall_assessment": {{
            "effectiveness_score": [1-10],
            "professional_tone": "[excellent/good/concerning/poor]",
            "clarity_score": [1-10],
            "appropriateness": "[appropriate/needs_improvement/inappropriate]"
        }},
        "code_of_conduct_compliance": {{
            "compliance_status": "[compliant/concerning/violation]",
            "specific_issues": ["list any problems"],
            "harassment_check": "[pass/concern/fail]",
            "respect_level": "[high/adequate/concerning/low]"
        }},
        "communication_channel": {{
            "email_appropriate": [true/false],
            "recommended_channel": "[email/phone/meeting]",
            "rationale": "[explanation]",
            "urgency_assessment": "[low/normal/high]"
        }},
        "improvements": [
            {{
                "category": "[tone/structure/compliance/channel]",
                "current_issue": "[what needs fixing]",
                "suggestion": "[specific improvement]",
                "example": "[how to rewrite if applicable]",
                "priority": "[high/medium/low]"
            }}
        ],
        "strengths": [
            "[list what's working well]"
        ]
    }}"""

    def _parse_email_analysis_response(self, claude_response: str, email_data: Dict) -> Dict:
        """Parse Claude's JSON response into structured format"""
        import re
        import json

        try:
            # Extract JSON from Claude's response
            json_match = re.search(r'\{[\s\S]*\}', claude_response)
            if not json_match:
                raise ValueError("No JSON found in Claude response")

            claude_data = json.loads(json_match.group())

            # Format for frontend based on analysis type
            if email_data.get('analysis_type') == 'incoming':
                return self._format_incoming_analysis(claude_data, email_data)
            else:
                return self._format_outgoing_analysis(claude_data, email_data)

        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"📄 Raw Claude response: {claude_response}")
            raise ValueError(f"Could not parse Claude response as JSON: {e}")

    def _format_outgoing_analysis(self, claude_data: Dict, email_data: Dict) -> Dict:
        """Format analysis for outgoing emails"""
        overall = claude_data.get('overall_assessment', {})
        compliance = claude_data.get('code_of_conduct_compliance', {})
        channel = claude_data.get('communication_channel', {})

        return {
            'overall_score': overall.get('effectiveness_score', 5),
            'overall_feedback': self._generate_overall_feedback(overall, compliance),

            'code_compliance': {
                'status': compliance.get('compliance_status', 'compliant'),
                'issues': compliance.get('specific_issues', []),
                'risk_level': compliance.get('respect_level', 'adequate')
            },

            'channel_assessment': {
                'email_appropriate': channel.get('email_appropriate', True),
                'recommended': channel.get('recommended_channel', 'email'),
                'rationale': channel.get('rationale', 'Email is appropriate for this communication')
            },

            'suggestions': self._format_suggestions(claude_data.get('improvements', [])),
            'strengths': claude_data.get('strengths', []),

            'analysis_type': 'outgoing'
        }

    def _format_incoming_analysis(self, claude_data: Dict, email_data: Dict) -> Dict:
        """Format analysis for incoming emails"""
        overall = claude_data.get('overall_assessment', {})
        compliance = claude_data.get('code_of_conduct_compliance', {})
        response = claude_data.get('response_strategy', {})

        return {
            'overall_score': overall.get('appropriateness_score', 5),
            'overall_feedback': f"Received email analysis: {overall.get('main_intent', 'General communication')}",

            'sender_assessment': {
                'tone': overall.get('professional_tone', 'appropriate'),
                'urgency': overall.get('urgency_level', 'normal'),
                'intent': overall.get('main_intent', 'Unknown')
            },

            'code_compliance': {
                'status': compliance.get('overall_compliance', 'compliant'),
                'issues': compliance.get('specific_issues', []),
                'risk_level': compliance.get('risk_level', 'low')
            },

            'response_strategy': {
                'recommended_channel': response.get('recommended_channel', 'email'),
                'tone': response.get('response_tone', 'professional'),
                'approach': response.get('suggested_approach', 'Standard professional response'),
                'key_points': response.get('key_points_to_address', [])
            },

            'suggestions': self._format_suggestions(claude_data.get('recommendations', [])),

            'analysis_type': 'incoming'
        }

    def _format_suggestions(self, improvements: List[Dict]) -> List[Dict]:
        """Format suggestions for frontend display"""
        return [
            {
                'type': 'critical' if imp.get('priority') == 'high' else 'improvement',
                'category': imp.get('category', 'General'),
                'text': imp.get('suggestion', ''),
                'impact': imp.get('priority', 'medium').title(),
                'reason': imp.get('rationale', '')
            }
            for imp in improvements if imp.get('suggestion')
        ]

    def _generate_overall_feedback(self, overall_data: Dict, compliance_data: Dict) -> str:
        """Generate overall feedback message"""
        score = overall_data.get('effectiveness_score', 5)
        compliance = compliance_data.get('compliance_status', 'compliant')

        if compliance == 'violation':
            return 'This email contains content that violates professional standards and should be revised before sending.'
        elif compliance == 'concerning':
            return 'This email has some concerning elements that should be addressed to ensure professional standards.'
        elif score >= 8:
            return 'Excellent professional communication that effectively conveys your message.'
        elif score >= 6:
            return 'Good communication with room for some improvements to enhance effectiveness.'
        else:
            return 'This email would benefit from significant improvements before sending.'

    def _generate_fallback_email_analysis(self, email_data: Dict) -> Dict:
        """Generate fallback analysis when Claude is unavailable"""
        import re

        content = email_data.get('content', '')
        subject = email_data.get('subject', '')

        # Basic pattern analysis
        has_greeting = bool(re.search(r'\b(hi|hello|dear|good morning|good afternoon)\b', content, re.IGNORECASE))
        has_closing = bool(re.search(r'\b(regards|thanks|sincerely|best|cheers)\b', content, re.IGNORECASE))
        has_politeness = bool(re.search(r'\b(please|thank you|would you|could you)\b', content, re.IGNORECASE))

        # Check for concerning patterns
        concerning_patterns = [
            r'\b(stupid|idiot|moron|pathetic|ridiculous)\b',
            r'[A-Z]{4,}',  # ALL CAPS sections
            r'!{2,}'  # Multiple exclamation marks
        ]

        has_concerns = any(re.search(pattern, content, re.IGNORECASE) for pattern in concerning_patterns)

        # Calculate realistic score
        base_score = 5
        if has_greeting: base_score += 0.5
        if has_closing: base_score += 0.5
        if has_politeness: base_score += 1
        if len(content) > 50 and len(content) < 300: base_score += 0.5
        if subject and len(subject) > 5: base_score += 0.5
        if has_concerns: base_score -= 3  # Significant penalty for concerning language

        score = max(1, min(10, base_score))

        suggestions = []
        if has_concerns:
            suggestions.append({
                'type': 'critical',
                'category': 'Professional Standards',
                'text': 'Review language for professional appropriateness - some phrases may be inappropriate for workplace communication',
                'impact': 'High',
                'reason': 'Professional communication standards require respectful language'
            })

        if not has_greeting:
            suggestions.append({
                'type': 'improvement',
                'category': 'Structure',
                'text': 'Consider adding a professional greeting',
                'impact': 'Medium',
                'reason': 'Greetings help establish a respectful tone'
            })

        if not has_closing:
            suggestions.append({
                'type': 'improvement',
                'category': 'Structure',
                'text': 'Add a professional closing',
                'impact': 'Medium',
                'reason': 'Professional closings complete the communication appropriately'
            })

        return {
            'overall_score': round(score, 1),
            'overall_feedback': f'{"This email contains concerning language that should be reviewed." if has_concerns else "Basic email structure analysis completed."}',
            'code_compliance': {
                'status': 'concerning' if has_concerns else 'compliant',
                'issues': ['Potentially inappropriate language detected'] if has_concerns else [],
                'risk_level': 'high' if has_concerns else 'low'
            },
            'suggestions': suggestions,
            'analysis_type': email_data.get('analysis_type', 'outgoing'),
            'fallback_analysis': True
        }

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
