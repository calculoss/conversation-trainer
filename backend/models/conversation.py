"""
Conversation Model for Conversation Trainer
Manages chat sessions between users and AI personalities
"""

import json
from datetime import datetime
from typing import Dict, List, Optional

class ConversationMessage:
    """
    A single message in a conversation
    Like one text message in a chat thread
    """
    
    def __init__(self, sender: str, content: str, sender_type: str = 'user'):
        """
        Create a new message
        
        sender: Who sent it ('user' or personality name like 'Councillor Stevens')
        content: What they said
        sender_type: 'user' or 'ai_personality'
        """
        self.timestamp = datetime.now().isoformat()
        self.sender = sender
        self.content = content
        self.sender_type = sender_type  # 'user' or 'ai_personality'
        
    def to_dict(self) -> Dict:
        """Convert message to dictionary for storage"""
        return {
            'timestamp': self.timestamp,
            'sender': self.sender,
            'content': self.content,
            'sender_type': self.sender_type
        }

class Conversation:
    """
    A complete conversation session
    Like an entire text message thread
    """
    
    def __init__(self, user_name: str, scenario_title: str):
        """Start a new conversation"""
        self.id = self._generate_id()
        self.user_name = user_name
        self.scenario_title = scenario_title
        self.created_date = datetime.now().isoformat()
        self.last_activity = datetime.now().isoformat()
        self.status = 'active'  # 'active', 'completed', 'paused'
        
        # Conversation data
        self.messages: List[ConversationMessage] = []
        self.personalities_involved = []  # List of personality IDs in this conversation
        self.scenario_context = ""  # Description of the situation being practiced
        
        # Analytics data
        self.total_messages = 0
        self.duration_minutes = 0
        self.user_satisfaction = None  # Rating from 1-5
        self.learning_notes = ""  # User's notes about what they learned
        
    def _generate_id(self) -> str:
        """Generate unique conversation ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def add_message(self, sender: str, content: str, sender_type: str = 'user'):
        """Add a new message to the conversation"""
        message = ConversationMessage(sender, content, sender_type)
        self.messages.append(message)
        self.total_messages += 1
        self.last_activity = datetime.now().isoformat()
        
        # Update duration (rough calculation)
        if len(self.messages) > 1:
            start_time = datetime.fromisoformat(self.created_date)
            current_time = datetime.now()
            self.duration_minutes = (current_time - start_time).total_seconds() / 60
    
    def get_conversation_history_for_claude(self) -> str:
        """
        Format conversation history for Claude API
        This helps Claude understand the context of previous messages
        """
        if not self.messages:
            return f"SCENARIO: {self.scenario_context}\n\nThis is the start of the conversation."
        
        history = f"SCENARIO: {self.scenario_context}\n\nCONVERSATION HISTORY:\n"
        
        for msg in self.messages[-10:]:  # Only send last 10 messages to avoid token limits
            if msg.sender_type == 'user':
                history += f"USER: {msg.content}\n"
            else:
                history += f"{msg.sender}: {msg.content}\n"
        
        history += "\nRespond as your character would to continue this conversation:"
        return history
    
    def add_personality(self, personality_id: str):
        """Add a personality to this conversation"""
        if personality_id not in self.personalities_involved:
            self.personalities_involved.append(personality_id)
    
    def complete_conversation(self, satisfaction_rating: int = None, notes: str = ""):
        """Mark conversation as completed"""
        self.status = 'completed'
        self.last_activity = datetime.now().isoformat()
        if satisfaction_rating:
            self.user_satisfaction = satisfaction_rating
        if notes:
            self.learning_notes = notes
    
    def to_dict(self) -> Dict:
        """Convert conversation to dictionary for storage"""
        return {
            'id': self.id,
            'user_name': self.user_name,
            'scenario_title': self.scenario_title,
            'created_date': self.created_date,
            'last_activity': self.last_activity,
            'status': self.status,
            'messages': [msg.to_dict() for msg in self.messages],
            'personalities_involved': self.personalities_involved,
            'scenario_context': self.scenario_context,
            'total_messages': self.total_messages,
            'duration_minutes': self.duration_minutes,
            'user_satisfaction': self.user_satisfaction,
            'learning_notes': self.learning_notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Conversation':
        """Create conversation from dictionary (loading from storage)"""
        conversation = cls(data['user_name'], data['scenario_title'])
        conversation.id = data['id']
        conversation.created_date = data['created_date']
        conversation.last_activity = data['last_activity']
        conversation.status = data['status']
        conversation.personalities_involved = data.get('personalities_involved', [])
        conversation.scenario_context = data.get('scenario_context', '')
        conversation.total_messages = data.get('total_messages', 0)
        conversation.duration_minutes = data.get('duration_minutes', 0)
        conversation.user_satisfaction = data.get('user_satisfaction')
        conversation.learning_notes = data.get('learning_notes', '')
        
        # Recreate messages
        conversation.messages = []
        for msg_data in data.get('messages', []):
            msg = ConversationMessage(
                msg_data['sender'], 
                msg_data['content'], 
                msg_data['sender_type']
            )
            msg.timestamp = msg_data['timestamp']  # Preserve original timestamp
            conversation.messages.append(msg)
        
        return conversation

# ============================================
# CONVERSATION SCENARIOS FOR LOCAL GOVERNMENT
# ============================================

def create_budget_cut_scenario() -> Dict:
    """Scenario: Director explaining budget cuts to department manager"""
    return {
        'title': 'Budget Cut Discussion',
        'context': """You are a Director who needs to inform a Department Manager that their budget is being cut by 15% due to reduced state funding. The manager's team is already stretched thin and morale is low. You need to:
        - Deliver the bad news clearly but compassionately
        - Help them find ways to maintain service levels
        - Address their concerns about staff workload
        - Maintain their trust and motivation
        
        The manager may be defensive, frustrated, or worried about their team.""",
        'user_role': 'Director',
        'ai_personalities': ['frustrated_manager'],
        'learning_objectives': [
            'Deliver difficult news with empathy',
            'Guide problem-solving without being directive',
            'Maintain relationships during tough conversations',
            'Balance organizational needs with team concerns'
        ]
    }

def create_angry_resident_scenario() -> Dict:
    """Scenario: Customer service handling upset ratepayer"""
    return {
        'title': 'Angry Resident Call',
        'context': """A longtime resident is calling about their rates notice, which has increased significantly. They're upset about the increase while complaining that local roads have potholes and the library hours were reduced. They feel they're not getting value for money and are threatening to complain to the mayor and local media.
        
        You need to:
        - Listen to their concerns respectfully
        - Explain the rates increase clearly
        - Address their service complaints appropriately
        - De-escalate their anger
        - Leave them feeling heard, even if not fully satisfied""",
        'user_role': 'Customer Service Officer',
        'ai_personalities': ['angry_resident'],
        'learning_objectives': [
            'De-escalate emotional situations',
            'Explain complex policy in simple terms',
            'Show empathy while maintaining boundaries',
            'Turn complaints into constructive dialogue'
        ]
    }
