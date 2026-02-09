"""
PHASE 4 - CINEMATIC SCENE PLANNING

SYSTEM PROMPT - DIRECTOR LLM (EXACT, IMMUTABLE)
ERES UN EDITOR DE CINE DE ELITE GANADOR DEL OSCAR. Tienes acceso a la transcripcion completa de una pelicula y a un analisis visual de sus escenas.

TU OBJETIVO:
Crear una secuencia de video (edicion) basada estrictamente en la solicitud del usuario, combinando los mejores momentos visuales con los dialogos mas relevantes.

INPUTS QUE RECIBIRAS:
1. [SOLICITUD]
2. [TRANSCRIPCION]
3. [VISUALES]

INSTRUCCIONES:
- Piensa como un director profesional
- Manten coherencia emocional
- Prioriza impacto narrativo
- Planifica cada escena cuidadosamente

FORMATO DE SALIDA:
JSON ESTRICTO, sin texto adicional.
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from models.schemas import ScenePlanningOutput, Scene, VoiceOver, Subtitles, VideoFormat


class ScenePlanning:
    """Phase 4: Cinematic scene planning with Director LLM"""

    def __init__(self):
        self.director_system_prompt = """ERES UN EDITOR DE CINE DE ELITE GANADOR DEL OSCAR. Tienes acceso a la transcripcion completa de una pelicula y a un analisis visual de sus escenas.

TU OBJETIVO:
Crear una secuencia de video (edicion) basada estrictamente en la solicitud del usuario, combinando los mejores momentos visuales con los dialogos mas relevantes.

INPUTS QUE RECIBIRAS:
1. [SOLICITUD] - La peticion del usuario con todos los parametros
2. [TRANSCRIPCION] - Texto y dialogos del video
3. [VISUALES] - Analisis visual de escenas
4. [NARRATIVA] - Analisis de arco narrativo y progresion emocional

INSTRUCCIONES:
- Piensa como un director profesional
- Manten coherencia emocional
- Prioriza impacto narrativo
- Planifica cada escena cuidadosamente
- Respeta el ritmo y tono especificados
- Usa transiciones apropiadas para el estilo

REGLAS ESTRICTAS:
- NO inventes contenido que no existe en el material fuente
- NO cambies la intencion del usuario
- SIEMPRE usa timestamps reales basados en la transcripcion
- SIEMPRE justifica la eleccion de cada escena

FORMATO DE SALIDA - JSON ESTRICTO:
{
  "title": "Titulo cinematografico",
  "theme": "Tema central",
  "style": "Estilo visual y narrativo",
  "format": "16:9 | 9:16 | 1:1",
  "voice_over": {
    "enabled": true/false,
    "voices": [
      {
        "gender": "male/female/non-binary",
        "language": "es/en/etc",
        "age": "young/adult/middle/senior",
        "text": "Texto del voice-over para esta escena"
      }
    ]
  },
  "subtitles": {
    "enabled": true/false,
    "type": "burned | srt",
    "style": "cinematic/social_media/minimal"
  },
  "scenes": [
    {
      "scene_id": 1,
      "goal": "Objetivo emocional y narrativo",
      "start": "00:00:00",
      "end": "00:00:05",
      "visual": "Descripcion visual",
      "audio": "dialogue/music/voice_over/ambient",
      "voice_over_text": "Texto si aplica",
      "subtitle_usage": true/false,
      "transition": "cut/fade/dissolve/wipe/match_cut"
    }
  ]
}

IMPORTANTE: Responde UNICAMENTE con el JSON valido. Sin texto adicional antes o despues."""

    def _seconds_to_timestamp(self, seconds: int) -> str:
        """Convert seconds to HH:MM:SS or MM:SS format"""
        if seconds >= 3600:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes:02d}:{secs:02d}"
    
    def _parse_duration(self, duration_answer: str) -> int:
        """Parse duration answer to seconds"""
        if '15-30' in duration_answer:
            return 25
        elif '30-60' in duration_answer:
            return 45
        elif '1-3' in duration_answer:
            return 120  # 2 minutes average
        elif '3-10' in duration_answer:
            return 360  # 6 minutes average
        elif '10-30' in duration_answer:
            return 1200  # 20 minutes average
        else:
            return 180  # Default 3 minutes

    def _determine_format(self, platform: str) -> VideoFormat:
        """Determine video format from platform"""
        platform_lower = platform.lower()
        if 'tiktok' in platform_lower or 'reels' in platform_lower or 'stories' in platform_lower:
            return VideoFormat.FORMAT_9_16
        elif 'instagram' in platform_lower and 'feed' in platform_lower:
            return VideoFormat.FORMAT_1_1
        else:
            return VideoFormat.FORMAT_16_9

    def _generate_voice_over_config(self, answers: Dict[str, Any]) -> VoiceOver:
        """Generate voice-over configuration from answers"""
        voice_needed = answers.get('voice_over_needed', 'No voice-over needed')
        
        if 'Yes' in voice_needed:
            voices = []
            if 'single' in voice_needed.lower():
                voices.append({
                    'gender': answers.get('voice_gender', 'No preference').lower().replace(' ', '_'),
                    'language': answers.get('voice_language', 'English').lower(),
                    'age': answers.get('voice_age', 'Adult').lower().replace('(', '').replace(')', '').replace('-', '_'),
                    'text': ''  # To be filled per scene
                })
            else:  # Multiple voices
                voices.append({
                    'gender': 'male',
                    'language': answers.get('voice_language', 'English').lower(),
                    'age': 'adult',
                    'text': ''
                })
                voices.append({
                    'gender': 'female',
                    'language': answers.get('voice_language', 'English').lower(),
                    'age': 'adult',
                    'text': ''
                })
            
            return VoiceOver(enabled=True, voices=voices)
        
        return VoiceOver(enabled=False)

    def _generate_subtitle_config(self, answers: Dict[str, Any]) -> Subtitles:
        """Generate subtitle configuration from answers"""
        subs = answers.get('subtitles_enabled', 'No subtitles needed')
        
        if 'Yes' in subs:
            sub_type = 'burned' if 'burned' in subs.lower() else 'srt'
            style = answers.get('subtitle_style', 'Professional').lower().replace(' ', '_')
            return Subtitles(enabled=True, type=sub_type, style=style)
        
        return Subtitles(enabled=False)

    def _calculate_scene_durations(self, total_duration: int, num_scenes: int, 
                                    rhythm: str) -> List[int]:
        """Calculate duration for each scene based on rhythm"""
        base_duration = total_duration // num_scenes
        
        # Adjust based on rhythm
        if 'slow' in rhythm.lower():
            # Longer scenes for slow rhythm
            durations = [int(base_duration * 1.2) for _ in range(num_scenes)]
        elif 'fast' in rhythm.lower():
            # Shorter scenes for fast rhythm
            durations = [int(base_duration * 0.8) for _ in range(num_scenes)]
        else:
            durations = [base_duration for _ in range(num_scenes)]
        
        # Adjust to match total duration
        current_total = sum(durations)
        if current_total != total_duration:
            # Add/subtract from last scene
            durations[-1] += (total_duration - current_total)
        
        return durations

    def _generate_scenes(self, inputs: Dict[str, Any], total_duration: int,
                         scene_durations: List[int]) -> List[Scene]:
        """Generate scene plan based on narrative analysis"""
        answers = inputs.get('answers', {})
        narrative = inputs.get('narrative', {})
        transcription = inputs.get('transcripcion', {})
        visual_analysis = inputs.get('visuales', {})
        
        rhythm = answers.get('editing_rhythm', 'Medium')
        tone = answers.get('emotional_tone', 'neutral')
        ending = answers.get('ending_style', 'Closed ending')
        
        # Get emotional progression from narrative
        emotional_progression = narrative.get('emotional_progression', [])
        
        scenes = []
        current_time = 0
        
        # Standard narrative structure: Hook -> Setup -> Rising -> Climax -> Resolution
        scene_types = ['hook', 'setup', 'rising_action', 'climax', 'resolution']
        
        # If we have more scenes than types, add more rising action scenes
        while len(scene_durations) > len(scene_types):
            scene_types.insert(2, 'rising_action')  # Add before climax
        
        for i, duration in enumerate(scene_durations):
            scene_type = scene_types[i] if i < len(scene_types) else 'development'
            
            # Get emotional beat for this scene
            emotional_beat = emotional_progression[i] if i < len(emotional_progression) else {
                'emotion': tone.lower(),
                'intensity': 0.5
            }
            
            # Determine visual and audio based on scene type
            if scene_type == 'hook':
                visual = "Impactful opening shot that establishes tone and grabs attention"
                audio = "music" if 'voice' not in answers.get('voice_over_needed', '') else "voice_over"
                transition = "cut"
                
            elif scene_type == 'setup':
                visual = "Establishing context and introducing key elements"
                audio = "dialogue" if transcription else "ambient"
                transition = "fade" if 'slow' in rhythm.lower() else "cut"
                
            elif scene_type == 'rising_action':
                visual = f"Building tension with {emotional_beat['emotion']} energy"
                audio = "music" if emotional_beat['intensity'] > 0.6 else "dialogue"
                transition = "match_cut" if i < len(scene_durations) - 1 else "cut"
                
            elif scene_type == 'climax':
                visual = f"Peak emotional moment: {emotional_beat['emotion']} at maximum intensity"
                audio = "music"
                transition = "fade"
                
            else:  # resolution
                if 'open' in ending.lower():
                    visual = "Thought-provoking final image that lingers"
                elif 'cliffhanger' in ending.lower():
                    visual = "Suspenseful final moment that hints at continuation"
                else:
                    visual = "Satisfying conclusion that resolves the narrative"
                audio = "ambient" if 'open' in ending.lower() else "music"
                transition = "fade"  # Final scene, transition is less relevant
            
            # Generate voice-over text if enabled
            voice_text = ""
            if answers.get('voice_over_needed', '').startswith('Yes'):
                if scene_type == 'hook':
                    voice_text = "[Opening hook - introduce the journey]"
                elif scene_type == 'setup':
                    voice_text = "[Context setting - establish the story]"
                elif scene_type == 'climax':
                    voice_text = f"[Emotional peak - {emotional_beat['emotion']}]"
                elif scene_type == 'resolution':
                    voice_text = "[Closing reflection - leave the audience with the message]"
            
            # Determine subtitle usage
            use_subs = 'Yes' in answers.get('subtitles_enabled', '')
            
            scene = Scene(
                scene_id=i + 1,
                goal=f"{scene_type.replace('_', ' ').title()}: {emotional_beat['emotion']} ({emotional_beat['intensity']:.0%} intensity)",
                start=self._seconds_to_timestamp(current_time),
                end=self._seconds_to_timestamp(current_time + duration),
                visual=visual,
                audio=audio,
                voice_over_text=voice_text if voice_text else None,
                subtitle_usage=use_subs,
                transition=transition
            )
            
            scenes.append(scene)
            current_time += duration
        
        return scenes

    def generate_plan(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main scene planning method.
        
        Returns strict JSON matching ScenePlanningOutput schema.
        """
        answers = inputs.get('answers', {})
        narrative = inputs.get('narrative', {})
        
        # Extract key parameters
        platform = answers.get('target_platform', 'YouTube')
        duration_answer = answers.get('target_duration', '1-3 minutes')
        rhythm = answers.get('editing_rhythm', 'Medium')
        tone = answers.get('emotional_tone', 'neutral')
        
        # Calculate total duration in seconds
        total_duration = self._parse_duration(duration_answer)
        
        # Determine format
        video_format = self._determine_format(platform)
        
        # Generate title and theme
        solicitud = inputs.get('solicitud', 'Cinematic Edit')
        title = self._generate_title(solicitud, tone)
        theme = self._generate_theme(solicitud, narrative)
        style = self._generate_style(answers)
        
        # Generate voice-over config
        voice_over = self._generate_voice_over_config(answers)
        
        # Generate subtitle config
        subtitles = self._generate_subtitle_config(answers)
        
        # Determine number of scenes based on duration and rhythm
        cuts_per_minute = {
            'slow': 8,
            'medium': 15,
            'fast': 30
        }.get(rhythm.lower().split()[0], 15)
        
        num_scenes = max(3, min(8, int((total_duration / 60) * cuts_per_minute / 4)))
        
        # Calculate scene durations
        scene_durations = self._calculate_scene_durations(total_duration, num_scenes, rhythm)
        
        # Generate scenes
        scenes = self._generate_scenes(inputs, total_duration, scene_durations)
        
        # Build final output
        output = {
            'title': title,
            'theme': theme,
            'style': style,
            'format': video_format.value,
            'voice_over': voice_over.dict(),
            'subtitles': subtitles.dict(),
            'scenes': [scene.dict() for scene in scenes]
        }
        
        return output

    def _generate_title(self, solicitud: str, tone: str) -> str:
        """Generate cinematic title based on request and tone"""
        # Extract key words from request
        words = solicitud.lower().split()
        
        # Common cinematic title patterns
        if 'interview' in words:
            return "Voices: A Personal Story"
        elif 'wedding' in words:
            return "Forever Begins"
        elif 'travel' in words or 'vacation' in words or 'trip' in words:
            return "Wanderlust: A Journey Captured"
        elif 'documentary' in words:
            return "The Untold Story"
        elif 'product' in words or 'commercial' in words:
            return "Innovation Revealed"
        elif 'event' in words:
            return "The Moment"
        else:
            # Generic cinematic title based on tone
            tone_titles = {
                'joyful': "Radiance",
                'melancholic': "Echoes of Yesterday",
                'suspenseful': "The Edge",
                'romantic': "Two Hearts",
                'inspirational': "Rise",
                'nostalgic': "Time Remembered",
                'energetic': "Momentum",
                'calm': "Serenity",
                'dramatic': "The Turning Point"
            }
            
            for key, title in tone_titles.items():
                if key in tone.lower():
                    return title
            
            return "The Edit"

    def _generate_theme(self, solicitud: str, narrative: Dict) -> str:
        """Generate theme description"""
        arc = narrative.get('narrative_arc', 'documentary')
        
        themes = {
            'hero_journey': 'Personal transformation through challenge and triumph',
            'transformation': 'Internal change and self-discovery',
            'love_story': 'Connection and relationship development',
            'tragedy': 'Loss, reflection, and emotional truth',
            'comedy': 'Joy, humor, and lighthearted moments',
            'mystery': 'Discovery and revelation',
            'documentary': 'Authentic human experience and truth',
            'montage': 'Time, memory, and progression',
            'interview': 'Personal narrative and intimate perspective',
            'event_coverage': 'Celebration and shared experience'
        }
        
        return themes.get(arc, 'Human experience captured through cinematic lens')

    def _generate_style(self, answers: Dict[str, Any]) -> str:
        """Generate style description"""
        rhythm = answers.get('editing_rhythm', 'Medium')
        tone = answers.get('emotional_tone', 'neutral')
        color = answers.get('color_grade', 'Natural')
        
        style_parts = []
        
        # Rhythm descriptor
        if 'slow' in rhythm.lower():
            style_parts.append("Contemplative pacing with deliberate, measured cuts")
        elif 'fast' in rhythm.lower():
            style_parts.append("Dynamic, energetic editing with rapid cuts")
        else:
            style_parts.append("Balanced rhythm with natural flow")
        
        # Tone descriptor
        style_parts.append(f"{tone.lower()} emotional tone")
        
        # Color descriptor
        style_parts.append(f"{color.lower()} color palette")
        
        return "; ".join(style_parts)


# Example usage
if __name__ == "__main__":
    planning = ScenePlanning()
    
    # Test inputs
    test_inputs = {
        'solicitud': 'Create a cinematic edit of my interview about overcoming challenges',
        'transcripcion': {},
        'visuales': {},
        'narrative': {
            'narrative_arc': 'interview',
            'emotional_progression': [
                {'emotion': 'curiosity', 'intensity': 0.3},
                {'emotion': 'empathy', 'intensity': 0.5},
                {'emotion': 'struggle', 'intensity': 0.7},
                {'emotion': 'triumph', 'intensity': 0.9},
                {'emotion': 'inspiration', 'intensity': 0.6}
            ]
        },
        'answers': {
            'target_platform': 'YouTube (long-form, 16:9)',
            'target_duration': '3-10 minutes (Long YouTube)',
            'editing_rhythm': 'Medium (balanced, standard pacing)',
            'emotional_tone': 'Inspirational / Motivational',
            'voice_over_needed': 'Yes, single voice',
            'voice_gender': 'Male',
            'voice_language': 'English',
            'voice_age': 'Adult (25-40)',
            'subtitles_enabled': 'Yes, burned-in (permanent on video)',
            'subtitle_style': 'Cinematic (elegant, minimal)',
            'ending_style': 'Emotional peak (strong feeling)',
            'color_grade': 'Warm / Golden'
        }
    }
    
    result = planning.generate_plan(test_inputs)
    
    print("SCENE PLANNING OUTPUT")
    print("=" * 60)
    print(json.dumps(result, indent=2, ensure_ascii=False))
