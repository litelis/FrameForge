"""
Pydantic models for strict JSON validation
All outputs must conform to these schemas
"""
from __future__ import annotations
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Literal
from enum import Enum

# ==================== ENUMS ====================

class VideoFormat(str, Enum):
    FORMAT_16_9 = "16:9"
    FORMAT_9_16 = "9:16"
    FORMAT_1_1 = "1:1"

class SubtitleType(str, Enum):
    BURNED = "burned"
    SRT = "srt"

class TransitionStyle(str, Enum):
    CUT = "cut"
    FADE = "fade"
    DISSOLVE = "dissolve"
    WIPE = "wipe"
    MATCH_CUT = "match_cut"

class AudioType(str, Enum):
    DIALOGUE = "dialogue"
    MUSIC = "music"
    VOICE_OVER = "voice_over"
    AMBIENT = "ambient"
    SILENCE = "silence"

class WebhookEventType(str, Enum):
    # Upload events
    VIDEO_UPLOAD_STARTED = "VIDEO_UPLOAD_STARTED"
    VIDEO_UPLOAD_COMPLETED = "VIDEO_UPLOAD_COMPLETED"
    
    # Transcription events
    AUDIO_TRANSCRIPTION_STARTED = "AUDIO_TRANSCRIPTION_STARTED"
    AUDIO_TRANSCRIPTION_COMPLETED = "AUDIO_TRANSCRIPTION_COMPLETED"
    
    # Visual analysis events
    VISUAL_ANALYSIS_STARTED = "VISUAL_ANALYSIS_STARTED"
    VISUAL_ANALYSIS_COMPLETED = "VISUAL_ANALYSIS_COMPLETED"
    
    # Phase 1 events
    PROMPT_REFINEMENT_STARTED = "PROMPT_REFINEMENT_STARTED"
    PROMPT_REFINEMENT_IMPROVED = "PROMPT_REFINEMENT_IMPROVED"
    PROMPT_REFINEMENT_APPROVED = "PROMPT_REFINEMENT_APPROVED"
    PROMPT_REFINEMENT_REVISION = "PROMPT_REFINEMENT_REVISION"
    
    # Phase 2 events
    INTELLIGENT_QUESTIONING_STARTED = "INTELLIGENT_QUESTIONING_STARTED"
    INTELLIGENT_QUESTIONING_COMPLETED = "INTELLIGENT_QUESTIONING_COMPLETED"
    
    # Phase 3 events
    NARRATIVE_REASONING_STARTED = "NARRATIVE_REASONING_STARTED"
    NARRATIVE_REASONING_COMPLETED = "NARRATIVE_REASONING_COMPLETED"
    
    # Phase 4 events
    SCENE_PLANNING_STARTED = "SCENE_PLANNING_STARTED"
    SCENE_PLANNING_COMPLETED = "SCENE_PLANNING_COMPLETED"
    
    # Execution events
    VIDEO_CUT_CREATION = "VIDEO_CUT_CREATION"
    VOICE_OVER_GENERATION = "VOICE_OVER_GENERATION"
    SUBTITLE_GENERATION = "SUBTITLE_GENERATION"
    FINAL_RENDER_STARTED = "FINAL_RENDER_STARTED"
    FINAL_RENDER_COMPLETED = "FINAL_RENDER_COMPLETED"
    
    # System events
    WEBHOOK_TEST = "WEBHOOK_TEST"
    ERROR = "ERROR"
    WARNING = "WARNING"

# ==================== PHASE 1: PROMPT REFINEMENT ====================

class PromptRefinementOutput(BaseModel):
    """
    STRICT JSON OUTPUT for Phase 1: Prompt Refinement
    
    {
      "original_prompt": "",
      "improved_prompt": "",
      "issues_detected": [],
      "improvements_made": [],
      "user_action_required": "accept | revise"
    }
    """
    original_prompt: str = Field(default=..., description="The user's original prompt, unchanged")
    improved_prompt: str = Field(default=..., description="Improved version with same intent, better clarity")
    issues_detected: List[str] = Field(default_factory=list, description="List of ambiguities, missing constraints, or vague language found")
    improvements_made: List[str] = Field(default_factory=list, description="List of specific improvements applied")
    user_action_required: Literal["accept", "revise"] = Field(default=..., description="Whether user should accept or request revision")
    
    @validator('improved_prompt')
    def improved_not_empty(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Improved prompt cannot be empty')
        return v
    
    @validator('user_action_required')
    def valid_action(cls, v):
        if v not in ['accept', 'revise']:
            raise ValueError('user_action_required must be "accept" or "revise"')
        return v

# ==================== PHASE 2: INTELLIGENT QUESTIONING ====================

class Question(BaseModel):
    """Single question structure"""
    id: str = Field(default=..., description="Unique question identifier")
    category: str = Field(default=..., description="Category: format, platform, duration, rhythm, tone, music, voice_over, subtitles, ending")
    question: str = Field(default=..., description="The question text")
    type: Literal["single_choice", "multiple_choice", "text", "number"] = Field(default=..., description="Type of answer expected")
    options: Optional[List[str]] = Field(default=None, description="Options for choice-based questions")
    required: bool = Field(default=True, description="Whether this question must be answered")
    help_text: Optional[str] = Field(default=None, description="Additional context or examples")

class QuestioningOutput(BaseModel):
    """
    Output for Phase 2: Intelligent Questioning
    """
    questions: List[Question] = Field(
        default_factory=list,
        description="List of generated questions"
    )
    total_questions: int = Field(
        ..., 
        description="Total number of questions"
    )
    required_answers: int = Field(
        ..., 
        description="Number of required answers"
    )
    can_proceed: bool = Field(
        ..., 
        description="Whether enough information is collected to proceed"
    )

# ==================== PHASE 3: NARRATIVE REASONING (Hidden) ====================

class NarrativeAnalysis(BaseModel):
    """
    Internal model for Phase 3: Deep Narrative Reasoning
    This is NOT exposed to the user directly
    """
    narrative_arc: str = Field(
        ..., 
        description="Identified narrative arc structure"
    )
    emotional_progression: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Emotional beats and their progression"
    )
    dominant_tone: str = Field(
        ..., 
        description="Primary emotional tone of the piece"
    )
    pacing_recommendation: str = Field(
        ..., 
        description="Recommended pacing based on narrative analysis"
    )
    scene_contrasts: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Identified contrasts between scenes"
    )
    symbolism_notes: Optional[str] = Field(
        default=None,
        description="Notable symbolic elements detected"
    )
    
    class Config:
        # This model is for internal use
        extra = "allow"

# ==================== PHASE 4: SCENE PLANNING ====================

class VoiceOver(BaseModel):
    """Voice-over configuration for a scene or project"""
    enabled: bool = Field(default=False)
    voices: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of voice configurations"
    )
    
    @validator('voices')
    def validate_voices(cls, v, values):
        if values.get('enabled') and not v:
            raise ValueError('At least one voice required when voice-over enabled')
        return v

class Subtitles(BaseModel):
    """Subtitle configuration"""
    enabled: bool = Field(default=False)
    type: Optional[SubtitleType] = Field(default=None)
    style: Optional[str] = Field(
        default=None,
        description="cinematic, social_media, minimal, etc."
    )
    
    @validator('type')
    def validate_type(cls, v, values):
        if values.get('enabled') and not v:
            raise ValueError('Subtitle type required when subtitles enabled')
        return v

class Scene(BaseModel):
    """
    Individual scene in the cinematic plan
    
    {
      "scene_id": 1,
      "goal": "",
      "start": "00:00:00",
      "end": "00:00:05",
      "visual": "",
      "audio": "",
      "transition": ""
    }
    """
    scene_id: int = Field(default=..., description="Sequential scene identifier")
    goal: str = Field(
        ..., 
        description="Emotional + narrative goal of this scene"
    )
    start: str = Field(
        ..., 
        description="Start timestamp (HH:MM:SS or MM:SS)"
    )
    end: str = Field(
        ..., 
        description="End timestamp (HH:MM:SS or MM:SS)"
    )
    visual: str = Field(
        ..., 
        description="Visual description or type"
    )
    audio: str = Field(
        ..., 
        description="Audio type: dialogue, music, voice_over, etc."
    )
    voice_over_text: Optional[str] = Field(
        default=None,
        description="Voice-over script if applicable"
    )
    subtitle_usage: bool = Field(
        default=False,
        description="Whether subtitles appear in this scene"
    )
    transition: str = Field(
        ..., 
        description="Transition style to next scene"
    )
    
    @validator('start', 'end')
    def validate_timestamp(cls, v):
        # Basic timestamp validation
        parts = v.split(':')
        if len(parts) not in [2, 3]:
            raise ValueError('Timestamp must be in MM:SS or HH:MM:SS format')
        return v

class ScenePlanningOutput(BaseModel):
    """
    STRICT JSON OUTPUT for Phase 4: Scene Planning
    
    {
      "title": "",
      "theme": "",
      "style": "",
      "format": "16:9 | 9:16 | 1:1",
      "voice_over": {...},
      "subtitles": {...},
      "scenes": [...]
    }
    """
    title: str = Field(
        ..., 
        description="Cinematic title of the edit"
    )
    theme: str = Field(
        ..., 
        description="Central theme or concept"
    )
    style: str = Field(
        ..., 
        description="Cinematic style description"
    )
    format: VideoFormat = Field(
        ..., 
        description="Video aspect ratio"
    )
    voice_over: VoiceOver = Field(
        default_factory=lambda: VoiceOver(enabled=False)
    )
    subtitles: Subtitles = Field(
        default_factory=lambda: Subtitles(enabled=False)
    )
    scenes: List[Scene] = Field(
        ..., 
        description="Sequential list of planned scenes",
        min_items=1
    )
    
    @validator('scenes')
    def validate_scenes(cls, v):
        if not v:
            raise ValueError('At least one scene required')
        # Check scene_id sequence
        ids = [s.scene_id for s in v]
        if ids != list(range(1, len(v) + 1)):
            raise ValueError('Scene IDs must be sequential starting from 1')
        return v

# ==================== WEBHOOK CONFIGURATION ====================

class WebhookConfig(BaseModel):
    """
    Discord webhook configuration
    
    User can paste webhook URL and enable/disable events
    """
    webhook_url: Optional[str] = Field(
        default=None,
        description="Discord webhook URL"
    )
    enabled: bool = Field(
        default=False,
        description="Master enable/disable switch"
    )
    events: Dict[str, bool] = Field(
        default_factory=lambda: {event.value: True for event in WebhookEventType},
        description="Map of event type to enabled status"
    )
    
    @validator('webhook_url')
    def validate_webhook_url(cls, v):
        if v and not v.startswith('https://discord.com/api/webhooks/'):
            raise ValueError('Invalid Discord webhook URL format')
        return v
    
    def is_event_enabled(self, event_type: WebhookEventType) -> bool:
        """Check if a specific event type is enabled"""
        if not self.enabled:
            return False
        return self.events.get(event_type.value, False)

# ==================== WEBHOOK MESSAGE ====================

class WebhookMessage(BaseModel):
    """
    Structure for Discord webhook messages
    """
    project_id: str = Field(default=..., description="Project/session identifier")
    phase: str = Field(default=..., description="Current phase")
    status: str = Field(default=..., description="Short status description")
    timestamp: str = Field(default=..., description="ISO timestamp")
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional event-specific details"
    )
    
    def to_discord_embed(self) -> Dict[str, Any]:
        """Convert to Discord embed format"""
        color_map = {
            'VIDEO_UPLOAD_STARTED': 0x3498db,  # Blue
            'VIDEO_UPLOAD_COMPLETED': 0x2ecc71,  # Green
            'ERROR': 0xe74c3c,  # Red
            'WARNING': 0xf39c12,  # Orange
        }
        
        return {
            'embeds': [{
                'title': f'🎬 {self.phase}',
                'description': self.status,
                'color': color_map.get(self.phase, 0x95a5a6),
                'fields': [
                    {
                        'name': 'Project ID',
                        'value': self.project_id[:8] + '...',
                        'inline': True
                    },
                    {
                        'name': 'Timestamp',
                        'value': self.timestamp,
                        'inline': True
                    }
                ],
                'footer': {
                    'text': 'AI Cinematic Video Editor'
                }
            }]
        }

# ==================== API RESPONSE MODELS ====================

class APIResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool
    session_id: str
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Update forward references for Python 3.12 compatibility in Pydantic v1
PromptRefinementOutput.update_forward_refs()
Question.update_forward_refs()
QuestioningOutput.update_forward_refs()
NarrativeAnalysis.update_forward_refs()
VoiceOver.update_forward_refs()
Subtitles.update_forward_refs()
Scene.update_forward_refs()
ScenePlanningOutput.update_forward_refs()
WebhookConfig.update_forward_refs()
WebhookMessage.update_forward_refs()
APIResponse.update_forward_refs()
