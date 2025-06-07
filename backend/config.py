"""
Configuration management for Conversation Trainer
Handles environment variables and API key loading
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration"""
    
    # Claude API Configuration
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # App Settings
    MAX_CONVERSATION_HISTORY = 10  # Number of messages to send to Claude
    DEFAULT_MAX_TOKENS = 300       # Claude response length limit
    
    @classmethod
    def validate_config(cls):
        """Check if all required configuration is present"""
        issues = []
        
        if not cls.CLAUDE_API_KEY:
            issues.append("CLAUDE_API_KEY not found in environment variables")
        
        if not cls.CLAUDE_API_KEY or cls.CLAUDE_API_KEY == 'your_actual_claude_api_key_here':
            issues.append("CLAUDE_API_KEY needs to be set to your real API key")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }

def get_config():
    """Get configuration object"""
    return Config()

def check_environment():
    """Check if environment is properly configured"""
    config = get_config()
    validation = config.validate_config()
    
    print("🔧 Environment Configuration Check:")
    print(f"   Claude API Key: {'✅ Set' if config.CLAUDE_API_KEY and config.CLAUDE_API_KEY != 'your_actual_claude_api_key_here' else '❌ Missing'}")
    print(f"   Debug Mode: {'✅ Enabled' if config.DEBUG else '🔒 Disabled'}")
    
    if not validation['valid']:
        print("\n⚠️  Configuration Issues:")
        for issue in validation['issues']:
            print(f"   - {issue}")
        print("\nPlease fix these issues before running the application.")
    else:
        print("\n✅ All configuration looks good!")
    
    return validation['valid']

if __name__ == "__main__":
    """Test configuration"""
    check_environment()
