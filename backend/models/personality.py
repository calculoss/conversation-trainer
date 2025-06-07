"""
Personality Model for Conversation Trainer
Defines how we store and manage AI personality data
"""

import json
from datetime import datetime
from typing import Dict, List, Optional

class Personality:
    """
    Represents an AI personality for conversation practice
    
    Think of this like a character profile for an actor:
    - What's their background?
    - How do they communicate?
    - What triggers them?
    - What are their goals?
    """
    
    def __init__(self, name: str, role: str):
        """Create a new personality"""
        self.id = self._generate_id()
        self.name = name
        self.role = role
        self.created_date = datetime.now().isoformat()
        
        # Core personality traits
        self.traits = []  # ['analytical', 'direct', 'skeptical']
        self.communication_style = ""  # 'formal', 'casual', 'aggressive'
        self.background = ""  # Their professional history
        self.objectives = []  # What they want from conversations
        
        # Conversation behavior
        self.triggers = []  # What makes them defensive/upset
        self.strengths = []  # What they're good at
        self.weaknesses = []  # What they struggle with
        
        # Local government specific
        self.department = ""  # Which department they represent
        self.seniority_level = ""  # 'junior', 'senior', 'executive'
        self.political_awareness = ""  # How politically savvy they are
        
    def _generate_id(self) -> str:
        """Generate a unique ID for this personality"""
        import uuid
        return str(uuid.uuid4())[:8]  # Short unique ID
    
    def to_dict(self) -> Dict:
        """Convert personality to dictionary for storage"""
        return {
            'id': self.id,
            'name': self.name,
            'role': self.role,
            'created_date': self.created_date,
            'traits': self.traits,
            'communication_style': self.communication_style,
            'background': self.background,
            'objectives': self.objectives,
            'triggers': self.triggers,
            'strengths': self.strengths,
            'weaknesses': self.weaknesses,
            'department': self.department,
            'seniority_level': self.seniority_level,
            'political_awareness': self.political_awareness
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Personality':
        """Create personality from dictionary (loading from storage)"""
        personality = cls(data['name'], data['role'])
        personality.id = data['id']
        personality.created_date = data['created_date']
        personality.traits = data.get('traits', [])
        personality.communication_style = data.get('communication_style', '')
        personality.background = data.get('background', '')
        personality.objectives = data.get('objectives', [])
        personality.triggers = data.get('triggers', [])
        personality.strengths = data.get('strengths', [])
        personality.weaknesses = data.get('weaknesses', [])
        personality.department = data.get('department', '')
        personality.seniority_level = data.get('seniority_level', '')
        personality.political_awareness = data.get('political_awareness', '')
        return personality
    
    def generate_claude_prompt(self, scenario: str) -> str:
        """
        Generate the prompt for Claude API to act as this personality
        This is the magic that makes Claude become this person!
        """
        prompt = f"""You are {self.name}, a {self.role} in NSW local government.

BACKGROUND: {self.background}

PERSONALITY TRAITS: {', '.join(self.traits)}
COMMUNICATION STYLE: {self.communication_style}
DEPARTMENT: {self.department}
SENIORITY LEVEL: {self.seniority_level}

YOUR OBJECTIVES IN CONVERSATIONS: {', '.join(self.objectives)}
WHAT TRIGGERS YOU: {', '.join(self.triggers)}
YOUR STRENGTHS: {', '.join(self.strengths)}

SCENARIO: {scenario}

Respond as {self.name} would in this situation. Stay in character throughout the conversation. Be realistic about local government constraints, politics, and pressures. Make the conversation challenging but fair, helping the other person practice handling difficult workplace situations.

Remember: You work in NSW local government, so consider community expectations, council politics, budget constraints, and public accountability in your responses."""

        return prompt

# ============================================
# PRE-BUILT PERSONALITY TEMPLATES
# ============================================

def create_skeptical_councillor() -> Personality:
    """Create a challenging councillor personality"""
    councillor = Personality("Councillor Margaret Stevens", "Elected Councillor")
    councillor.traits = ['skeptical', 'budget-focused', 'community-oriented', 'direct']
    councillor.communication_style = 'formal but challenging'
    councillor.background = "Former small business owner, elected 3 terms, represents ratepayer interests"
    councillor.objectives = ['Protect ratepayer money', 'Ensure transparency', 'Challenge spending']
    councillor.triggers = ['Vague answers', 'Cost overruns', 'Consultant fees']
    councillor.strengths = ['Financial scrutiny', 'Community connection']
    councillor.department = "Council"
    councillor.seniority_level = "elected official"
    councillor.political_awareness = "high"
    return councillor

def create_frustrated_resident() -> Personality:
    """Create an upset community member personality"""
    resident = Personality("Robert Chen", "Local Resident")
    resident.traits = ['frustrated', 'detail-oriented', 'persistent', 'taxpayer-focused']
    resident.communication_style = 'emotional but articulate'
    resident.background = "Local business owner, rates payer for 15 years, active in community"
    resident.objectives = ['Get problems fixed', 'Receive value for rates', 'Be heard and respected']
    resident.triggers = ['Bureaucratic responses', 'Delays', 'Being dismissed']
    resident.strengths = ['Knows local issues', 'Passionate about community']
    resident.department = "Community"
    resident.seniority_level = "ratepayer"
    resident.political_awareness = "medium"
    return resident
