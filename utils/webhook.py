"""
Discord Webhook Integration for Real-time Notifications

Features:
- Async/background notification sending (non-blocking)
- Configurable event triggers
- Rich Discord embeds
- Error handling and retry logic
"""

import aiohttp
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
import logging

from models.schemas import WebhookConfig, WebhookMessage, WebhookEventType

logger = logging.getLogger(__name__)


class WebhookNotifier:
    """
    Discord Webhook Notifier
    
    Sends real-time notifications about system execution to Discord.
    All notifications are async and non-blocking.
    """
    
    def __init__(self, max_retries: int = 3, timeout: int = 10):
        self.max_retries = max_retries
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        return self.session
    
    async def _send_webhook(self, webhook_url: str, message: Dict[str, Any]) -> bool:
        """
        Send webhook message to Discord
        
        Args:
            webhook_url: Discord webhook URL
            message: Message payload
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            session = await self._get_session()
            
            async with session.post(
                webhook_url,
                json=message,
                headers={'Content-Type': 'application/json'}
            ) as response:
                if response.status == 204:
                    logger.info(f"Webhook sent successfully to {webhook_url[:50]}...")
                    return True
                else:
                    logger.warning(f"Webhook failed with status {response.status}")
                    return False
                    
        except aiohttp.ClientError as e:
            logger.error(f"Webhook client error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Webhook unexpected error: {str(e)}")
            return False
    
    async def _send_with_retry(self, webhook_url: str, message: Dict[str, Any]) -> bool:
        """Send webhook with retry logic"""
        for attempt in range(self.max_retries):
            if await self._send_webhook(webhook_url, message):
                return True
            
            if attempt < self.max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                logger.info(f"Retrying webhook in {wait_time}s (attempt {attempt + 2}/{self.max_retries})")
                await asyncio.sleep(wait_time)
        
        logger.error(f"Webhook failed after {self.max_retries} attempts")
        return False
    
    def _create_message(
        self,
        event_type: WebhookEventType,
        session_id: str,
        status: str,
        details: Optional[Dict[str, Any]] = None
    ) -> WebhookMessage:
        """Create a webhook message"""
        return WebhookMessage(
            project_id=session_id,
            phase=event_type.value,
            status=status,
            timestamp=datetime.now().isoformat(),
            details=details or {}
        )
    
    def _get_event_color(self, event_type: WebhookEventType) -> int:
        """Get Discord embed color for event type"""
        color_map = {
            # Upload events - Blue
            WebhookEventType.VIDEO_UPLOAD_STARTED: 0x3498db,
            WebhookEventType.VIDEO_UPLOAD_COMPLETED: 0x2ecc71,
            
            # Transcription - Purple
            WebhookEventType.AUDIO_TRANSCRIPTION_STARTED: 0x9b59b6,
            WebhookEventType.AUDIO_TRANSCRIPTION_COMPLETED: 0x2ecc71,
            
            # Visual analysis - Orange
            WebhookEventType.VISUAL_ANALYSIS_STARTED: 0xe67e22,
            WebhookEventType.VISUAL_ANALYSIS_COMPLETED: 0x2ecc71,
            
            # Phase 1 - Cyan
            WebhookEventType.PROMPT_REFINEMENT_STARTED: 0x1abc9c,
            WebhookEventType.PROMPT_REFINEMENT_IMPROVED: 0x3498db,
            WebhookEventType.PROMPT_REFINEMENT_APPROVED: 0x2ecc71,
            WebhookEventType.PROMPT_REFINEMENT_REVISION: 0xf39c12,
            
            # Phase 2 - Yellow
            WebhookEventType.INTELLIGENT_QUESTIONING_STARTED: 0xf1c40f,
            WebhookEventType.INTELLIGENT_QUESTIONING_COMPLETED: 0x2ecc71,
            
            # Phase 3 - Pink
            WebhookEventType.NARRATIVE_REASONING_STARTED: 0xff9ff3,
            WebhookEventType.NARRATIVE_REASONING_COMPLETED: 0x2ecc71,
            
            # Phase 4 - Red
            WebhookEventType.SCENE_PLANNING_STARTED: 0xe74c3c,
            WebhookEventType.SCENE_PLANNING_COMPLETED: 0x2ecc71,
            
            # Execution - Green variations
            WebhookEventType.VIDEO_CUT_CREATION: 0x27ae60,
            WebhookEventType.VOICE_OVER_GENERATION: 0x27ae60,
            WebhookEventType.SUBTITLE_GENERATION: 0x27ae60,
            WebhookEventType.FINAL_RENDER_STARTED: 0xe74c3c,
            WebhookEventType.FINAL_RENDER_COMPLETED: 0x2ecc71,
            
            # System - Gray/Red
            WebhookEventType.WEBHOOK_TEST: 0x95a5a6,
            WebhookEventType.ERROR: 0xe74c3c,
            WebhookEventType.WARNING: 0xf39c12,
        }
        
        return color_map.get(event_type, 0x95a5a6)  # Default gray
    
    def _get_event_emoji(self, event_type: WebhookEventType) -> str:
        """Get emoji for event type"""
        emoji_map = {
            WebhookEventType.VIDEO_UPLOAD_STARTED: "📤",
            WebhookEventType.VIDEO_UPLOAD_COMPLETED: "✅",
            WebhookEventType.AUDIO_TRANSCRIPTION_STARTED: "🎤",
            WebhookEventType.AUDIO_TRANSCRIPTION_COMPLETED: "📝",
            WebhookEventType.VISUAL_ANALYSIS_STARTED: "👁️",
            WebhookEventType.VISUAL_ANALYSIS_COMPLETED: "🎨",
            WebhookEventType.PROMPT_REFINEMENT_STARTED: "✏️",
            WebhookEventType.PROMPT_REFINEMENT_IMPROVED: "💡",
            WebhookEventType.PROMPT_REFINEMENT_APPROVED: "👍",
            WebhookEventType.PROMPT_REFINEMENT_REVISION: "🔄",
            WebhookEventType.INTELLIGENT_QUESTIONING_STARTED: "❓",
            WebhookEventType.INTELLIGENT_QUESTIONING_COMPLETED: "📋",
            WebhookEventType.NARRATIVE_REASONING_STARTED: "🧠",
            WebhookEventType.NARRATIVE_REASONING_COMPLETED: "📖",
            WebhookEventType.SCENE_PLANNING_STARTED: "🎬",
            WebhookEventType.SCENE_PLANNING_COMPLETED: "🎞️",
            WebhookEventType.VIDEO_CUT_CREATION: "✂️",
            WebhookEventType.VOICE_OVER_GENERATION: "🗣️",
            WebhookEventType.SUBTITLE_GENERATION: "💬",
            WebhookEventType.FINAL_RENDER_STARTED: "🚀",
            WebhookEventType.FINAL_RENDER_COMPLETED: "🎉",
            WebhookEventType.WEBHOOK_TEST: "🔔",
            WebhookEventType.ERROR: "❌",
            WebhookEventType.WARNING: "⚠️",
        }
        
        return emoji_map.get(event_type, "📢")
    
    def _build_discord_embed(
        self,
        event_type: WebhookEventType,
        session_id: str,
        status: str,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Build Discord embed message"""
        emoji = self._get_event_emoji(event_type)
        color = self._get_event_color(event_type)
        
        # Format event name for display
        event_name = event_type.value.replace('_', ' ').title()
        
        # Build fields from details
        fields = []
        if details:
            for key, value in details.items():
                # Skip complex objects, keep simple values
                if isinstance(value, (str, int, float, bool)):
                    fields.append({
                        'name': key.replace('_', ' ').title(),
                        'value': str(value)[:1000],  # Discord limit
                        'inline': True
                    })
        
        # Add project ID field
        fields.insert(0, {
            'name': 'Project ID',
            'value': session_id[:8] + '...',
            'inline': True
        })
        
        # Add timestamp
        fields.insert(1, {
            'name': 'Time',
            'value': datetime.now().strftime('%H:%M:%S'),
            'inline': True
        })
        
        embed = {
            'title': f"{emoji} {event_name}",
            'description': status,
            'color': color,
            'fields': fields,
            'footer': {
                'text': '🎬 AI Cinematic Video Editor Pro',
                'icon_url': 'https://cdn.discordapp.com/embed/avatars/0.png'
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return {'embeds': [embed]}
    
    async def notify(
        self,
        config: Dict[str, Any],
        event_type_str: str,
        session_id: str,
        status: str,
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send notification if enabled for this event type
        
        Args:
            config: WebhookConfig dict
            event_type_str: Event type as string
            session_id: Project/session ID
            status: Status message
            details: Additional details
            
        Returns:
            bool: True if sent or not needed, False if failed
        """
        try:
            # Parse config
            webhook_config = WebhookConfig(**config)
            
            # Check if webhooks enabled
            if not webhook_config.enabled:
                return True
            
            # Check if webhook URL configured
            if not webhook_config.webhook_url:
                return True
            
            # Parse event type
            try:
                event_type = WebhookEventType(event_type_str)
            except ValueError:
                logger.warning(f"Unknown event type: {event_type_str}")
                event_type = WebhookEventType.WARNING
            
            # Check if this event type is enabled
            if not webhook_config.is_event_enabled(event_type):
                logger.debug(f"Event {event_type.value} disabled, skipping notification")
                return True
            
            # Build message
            message = self._build_discord_embed(event_type, session_id, status, details)
            
            # Send with retry
            success = await self._send_with_retry(webhook_config.webhook_url, message)
            
            if not success:
                logger.error(f"Failed to send webhook for {event_type.value}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error in notify: {str(e)}")
            # Don't raise - webhooks should never block main functionality
            return False
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()


# Synchronous wrapper for convenience
def send_notification_sync(
    webhook_url: str,
    event_type: str,
    session_id: str,
    status: str,
    details: Optional[Dict[str, Any]] = None
):
    """
    Synchronous wrapper for sending notifications.
    Use this when you can't use async/await.
    """
    notifier = WebhookNotifier()
    
    config = {
        'webhook_url': webhook_url,
        'enabled': True,
        'events': {event: True for event in WebhookEventType}
    }
    
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If already in async context, create task
            asyncio.create_task(notifier.notify(config, event_type, session_id, status, details))
        else:
            # Run synchronously
            loop.run_until_complete(notifier.notify(config, event_type, session_id, status, details))
    except RuntimeError:
        # No event loop, create new one
        asyncio.run(notifier.notify(config, event_type, session_id, status, details))


# Example usage
if __name__ == "__main__":
    import os
    
    async def test():
        notifier = WebhookNotifier()
        
        # Test configuration
        test_config = {
            'webhook_url': os.getenv('DISCORD_WEBHOOK_URL', ''),
            'enabled': True,
            'events': {
                'VIDEO_UPLOAD_STARTED': True,
                'VIDEO_UPLOAD_COMPLETED': True,
                'ERROR': True
            }
        }
        
        if not test_config['webhook_url']:
            print("Set DISCORD_WEBHOOK_URL environment variable to test")
            return
        
        # Test notifications
        await notifier.notify(
            test_config,
            'VIDEO_UPLOAD_STARTED',
            'test-session-123',
            'Video upload has started',
            {'filename': 'test_video.mp4', 'size_mb': 150}
        )
        
        await asyncio.sleep(1)
        
        await notifier.notify(
            test_config,
            'VIDEO_UPLOAD_COMPLETED',
            'test-session-123',
            'Video uploaded successfully',
            {'duration': 120, 'resolution': '1920x1080'}
        )
        
        await notifier.close()
        print("Test completed!")
    
    # Run test
    asyncio.run(test())
