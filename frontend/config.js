// ============================================
// CONFIGURATION FILE FOR CONVERSATION TRAINER
// ============================================

// Google Cloud Text-to-Speech API Configuration
const CONFIG = {
    // TODO: Replace with your actual Google Cloud API key
    // IMPORTANT: This is for development only.
    // In production, use environment variables or secure key management
    GOOGLE_TTS_API_KEY: 'AIzaSyBEgz77N8_rbFqFgT-WpN9T6H7dP1yBEd8',

    // Google Cloud TTS API endpoint
    GOOGLE_TTS_ENDPOINT: 'https://texttospeech.googleapis.com/v1/text:synthesize',

    // Voice mapping for DISC personalities
    DISC_VOICES: {
        // Dominance - Confident, direct Australian male
        'infrastructure_engineer': {
            name: 'en-AU-Neural2-B',
            languageCode: 'en-AU',
            description: 'Confident Australian Male'
        },
        'budget_director': {
            name: 'en-AU-Neural2-B',
            languageCode: 'en-AU',
            description: 'Direct Australian Male'
        },

        // Influence - Warm, engaging Australian female
        'community_engagement': {
            name: 'en-AU-Neural2-A',
            languageCode: 'en-AU',
            description: 'Warm Australian Female'
        },
        'strategic_planner': {
            name: 'en-AU-Neural2-A',
            languageCode: 'en-AU',
            description: 'Enthusiastic Australian Female'
        },

        // Steadiness - Calm, patient Australian voices
        'councillor_thompson': {
            name: 'en-AU-Neural2-C',
            languageCode: 'en-AU',
            description: 'Patient Australian Female'
        },

        // Conscientiousness - Precise, analytical voices
        'union_rep': {
            name: 'en-GB-Neural2-B',
            languageCode: 'en-GB',
            description: 'Assertive British Male'
        },

        // Custom character fallback
        'custom_character': {
            name: 'en-AU-Neural2-D',
            languageCode: 'en-AU',
            description: 'Professional Australian Voice'
        }
    },

    // Audio configuration
    AUDIO_CONFIG: {
        audioEncoding: 'MP3',
        speakingRate: 1.0,
        pitch: 0.0,
        volumeGainDb: 0.0
    },

    // Feature flags
    FEATURES: {
        useGoogleTTS: true,          // Enable Google Cloud TTS
        fallbackToBrowserTTS: true,  // Fallback to browser if Google fails
        enableVoiceControls: true,   // Show voice control options
        debugMode: true              // Console logging for development
    }
};

// Export for use in main application
window.CONFIG = CONFIG;

// Development helper functions
window.debugConfig = function() {
    console.log('🔧 Configuration Debug:', CONFIG);
    console.log('🎭 Available DISC voices:', Object.keys(CONFIG.DISC_VOICES));
    console.log('🔑 API key configured:', CONFIG.GOOGLE_TTS_API_KEY !== 'AIzaSyBEgz77N8_rbFqFgT-WpN9T6H7dP1yBEd8E');
};

// Quick API key setter for development
window.setApiKey = function(apiKey) {
    CONFIG.GOOGLE_TTS_API_KEY = apiKey;
    console.log('✅ API key updated');
};

console.log('🔧 Configuration loaded. Use debugConfig() to view settings.');