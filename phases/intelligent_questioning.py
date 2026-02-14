"""
PHASE 2 — INTELLIGENT QUESTIONING (MANDATORY)

Before editing, ask only high-quality, relevant questions if information is missing.

Possible topics:
- Video format (16:9, 9:16, 1:1)
- Target platform (YouTube, TikTok, Instagram, Film)
- Desired duration
- Editing rhythm (slow / medium / fast)
- Emotional tone
- Music style
- Voice-over: Language, Gender, Age range, One or multiple voices
- Subtitles: Burned-in or SRT, Style (cinematic, social media, minimal)
- Ending style (open / closed)

Do NOT continue until enough answers are collected.
"""

import json
import ollama
from typing import List, Dict, Any, Optional
from models.schemas import Question, QuestioningOutput


class IntelligentQuestioning:
    """Phase 2: Generate intelligent questions to gather missing information"""

    def __init__(self, model_name: str = "llama3"):
        self.model_name = model_name
        self.question_templates = {
            'format': {
                'id': 'video_format',
                'category': 'format',
                'question': 'What video format do you need?',
                'type': 'single_choice',
                'options': ['16:9 (Landscape - YouTube, Film, TV)', '9:16 (Portrait - TikTok, Instagram Reels, Stories)', '1:1 (Square - Instagram Feed, Facebook)'],
                'required': True,
                'help_text': 'This determines the aspect ratio and framing of your video'
            },
            'platform': {
                'id': 'target_platform',
                'category': 'platform',
                'question': 'Which platform is this video for?',
                'type': 'single_choice',
                'options': ['YouTube (long-form, 16:9)', 'TikTok (short-form, 9:16, fast-paced)', 'Instagram Reels (9:16, trendy)', 'Instagram Feed (1:1 or 4:5)', 'Facebook (various)', 'Cinema/Film (16:9, high quality)', 'TV Broadcast (16:9, standard)', 'Internal/Private (flexible)'],
                'required': True,
                'help_text': 'Platform affects pacing, style, and technical requirements'
            },
            'duration': {
                'id': 'target_duration',
                'category': 'duration',
                'question': 'What is your target duration?',
                'type': 'single_choice',
                'options': ['15-30 seconds (Short social media)', '30-60 seconds (Standard social)', '1-3 minutes (YouTube short/Medium)', '3-10 minutes (Long YouTube)', '10-30 minutes (Extended content)', 'Feature length (30+ minutes)'],
                'required': True,
                'help_text': 'Duration affects pacing and how much content we can include'
            },
            'rhythm': {
                'id': 'editing_rhythm',
                'category': 'rhythm',
                'question': 'What editing rhythm do you prefer?',
                'type': 'single_choice',
                'options': ['Slow (contemplative, long takes, artistic)', 'Medium (balanced, standard pacing)', 'Fast (dynamic, quick cuts, energetic)', 'Variable (mix of paces for emotional effect)'],
                'required': True,
                'help_text': 'Rhythm sets the overall energy and feel of the edit'
            },
            'tone': {
                'id': 'emotional_tone',
                'category': 'tone',
                'question': 'What is the primary emotional tone?',
                'type': 'single_choice',
                'options': ['Joyful / Uplifting', 'Melancholic / Sad', 'Suspenseful / Tense', 'Romantic / Tender', 'Inspirational / Motivational', 'Nostalgic / Reflective', 'Energetic / Exciting', 'Calm / Peaceful', 'Dramatic / Intense', 'Humorous / Light'],
                'required': True,
                'help_text': 'The emotional tone guides music selection, pacing, and color grading'
            },
            'music': {
                'id': 'music_style',
                'category': 'music',
                'question': 'What music style should accompany the video?',
                'type': 'single_choice',
                'options': ['Cinematic orchestral', 'Electronic / Synth', 'Acoustic / Folk', 'Jazz / Blues', 'Rock / Alternative', 'Hip-hop / Rap', 'Classical', 'Ambient / Atmospheric', 'Pop / Modern', 'No music (dialogue only)', 'Custom (specify in notes)'],
                'required': False,
                'help_text': 'Music significantly impacts the emotional impact'
            },
            'voice_over': {
                'id': 'voice_over_needed',
                'category': 'voice_over',
                'question': 'Do you need voice-over narration?',
                'type': 'single_choice',
                'options': ['Yes, single voice', 'Yes, multiple voices', 'No voice-over needed'],
                'required': False,
                'help_text': 'Voice-over can guide the narrative and add professional polish'
            },
            'voice_language': {
                'id': 'voice_language',
                'category': 'voice_over',
                'question': 'What language for the voice-over?',
                'type': 'single_choice',
                'options': ['English', 'Spanish', 'French', 'German', 'Italian', 'Portuguese', 'Chinese', 'Japanese', 'Other (specify)'],
                'required': False,
                'help_text': 'Language affects voice talent selection',
                'condition': 'voice_over_needed:Yes'
            },
            'voice_gender': {
                'id': 'voice_gender',
                'category': 'voice_over',
                'question': 'Preferred voice gender?',
                'type': 'single_choice',
                'options': ['Male', 'Female', 'Non-binary / Androgynous', 'No preference'],
                'required': False,
                'help_text': 'Voice characteristics affect the feel of the narration',
                'condition': 'voice_over_needed:Yes'
            },
            'voice_age': {
                'id': 'voice_age',
                'category': 'voice_over',
                'question': 'Preferred voice age range?',
                'type': 'single_choice',
                'options': ['Young (18-25)', 'Adult (25-40)', 'Middle-aged (40-55)', 'Senior (55+)', 'No preference'],
                'required': False,
                'help_text': 'Age range affects voice casting',
                'condition': 'voice_over_needed:Yes'
            },
            'subtitles': {
                'id': 'subtitles_enabled',
                'category': 'subtitles',
                'question': 'Do you need subtitles?',
                'type': 'single_choice',
                'options': ['Yes, burned-in (permanent on video)', 'Yes, SRT file (separate, optional)', 'No subtitles needed'],
                'required': False,
                'help_text': 'Subtitles improve accessibility and engagement'
            },
            'subtitle_style': {
                'id': 'subtitle_style',
                'category': 'subtitles',
                'question': 'What subtitle style?',
                'type': 'single_choice',
                'options': ['Cinematic (elegant, minimal)', 'Social Media (bold, colorful)', 'Professional (clean, readable)', 'Minimal (small, unobtrusive)', 'Custom (specify)'],
                'required': False,
                'help_text': 'Style should match your platform and tone',
                'condition': 'subtitles_enabled:Yes'
            },
            'ending': {
                'id': 'ending_style',
                'category': 'ending',
                'question': 'How should the video end?',
                'type': 'single_choice',
                'options': ['Closed ending (clear resolution)', 'Open ending (thought-provoking)', 'Call-to-action (subscribe, visit, etc.)', 'Cliffhanger (continued in next video)', 'Circular (returns to opening)', 'Emotional peak (strong feeling)', 'Informational summary'],
                'required': False,
                'help_text': 'The ending shapes how viewers remember your video'
            },
            'color_grade': {
                'id': 'color_grade',
                'category': 'style',
                'question': 'Preferred color grading style?',
                'type': 'single_choice',
                'options': ['Natural / Realistic', 'Warm / Golden', 'Cool / Blue tones', 'High contrast / Dramatic', 'Desaturated / Muted', 'Vibrant / Saturated', 'Black & White', 'Vintage / Film look', 'Teal & Orange (cinematic)', 'Custom (specify)'],
                'required': False,
                'help_text': 'Color grading sets the visual mood'
            },
            'source_material': {
                'id': 'source_material',
                'category': 'technical',
                'question': 'What is your source footage like?',
                'type': 'multiple_choice',
                'options': ['Single continuous take', 'Multiple camera angles', 'Interview footage', 'B-roll / supplementary footage', 'Screen recordings', 'Mobile phone footage', 'Professional camera footage', 'Mixed sources'],
                'required': True,
                'help_text': 'Helps determine editing approach and technical requirements'
            }
        }

    def detect_missing_info(self, prompt: str, existing_answers: Dict[str, Any]) -> List[str]:
        """Detect what information is missing from the prompt and answers"""
        missing = []
        
        # Check for format mentions
        if not any(x in prompt.lower() for x in ['16:9', '9:16', '1:1', 'landscape', 'portrait', 'square']):
            if 'video_format' not in existing_answers:
                missing.append('format')
        
        # Check for platform mentions
        platforms = ['youtube', 'tiktok', 'instagram', 'facebook', 'film', 'cinema', 'tv']
        if not any(p in prompt.lower() for p in platforms):
            if 'target_platform' not in existing_answers:
                missing.append('platform')
        
        # Check for duration
        duration_indicators = ['minute', 'second', 'hour', 'min', 'sec', 'long', 'short']
        if not any(d in prompt.lower() for d in duration_indicators):
            if 'target_duration' not in existing_answers:
                missing.append('duration')
        
        # Check for rhythm/pacing
        rhythm_words = ['slow', 'fast', 'quick', 'paced', 'rhythm', 'dynamic', 'calm']
        if not any(r in prompt.lower() for r in rhythm_words):
            if 'editing_rhythm' not in existing_answers:
                missing.append('rhythm')
        
        # Check for emotional tone
        tone_words = ['emotional', 'happy', 'sad', 'exciting', 'dramatic', 'funny', 'serious']
        if not any(t in prompt.lower() for t in tone_words):
            if 'emotional_tone' not in existing_answers:
                missing.append('tone')
        
        # Check for music
        music_words = ['music', 'song', 'soundtrack', 'audio']
        if not any(m in prompt.lower() for m in music_words):
            if 'music_style' not in existing_answers:
                missing.append('music')
        
        # Check for voice-over
        voice_words = ['voice', 'narration', 'narrator', 'speak', 'tell']
        if not any(v in prompt.lower() for v in voice_words):
            if 'voice_over_needed' not in existing_answers:
                missing.append('voice_over')
        
        # Check for subtitles
        sub_words = ['subtitle', 'caption', 'text on screen']
        if not any(s in prompt.lower() for s in sub_words):
            if 'subtitles_enabled' not in existing_answers:
                missing.append('subtitles')
        
        # Check for ending
        ending_words = ['end', 'finish', 'conclude', 'close', 'wrap up']
        if not any(e in prompt.lower() for e in ending_words):
            if 'ending_style' not in existing_answers:
                missing.append('ending')
        
        # Always ask about source material if not mentioned
        if 'source_material' not in existing_answers:
            missing.append('source_material')
        
        return missing

    def generate_questions(self, prompt: str, existing_answers: Dict[str, Any]) -> List[Question]:
        """Generate relevant questions based on missing information"""
        missing_categories = self.detect_missing_info(prompt, existing_answers)
        
        questions = []
        for category in missing_categories:
            if category in self.question_templates:
                template = self.question_templates[category]
                
                # Check if question has a condition
                if 'condition' in template:
                    condition_key, condition_value = template['condition'].split(':')
                    existing_value = existing_answers.get(condition_key, '')
                    if condition_value not in existing_value:
                        continue  # Skip this question if condition not met
                
                # Create Question object
                question = Question(
                    id=template['id'],
                    category=template['category'],
                    question=template['question'],
                    type=template['type'],
                    options=template.get('options'),
                    required=template.get('required', True),
                    help_text=template.get('help_text')
                )
                questions.append(question)
        
        # Sort: required questions first
        questions.sort(key=lambda q: (not q.required, q.id))
        
        return questions

    def check_completeness(self, questions: List[Any], answers: Dict[str, Any]) -> bool:
        """Check if all required questions have been answered"""
        # Handle both Question objects and dictionaries
        def is_required(q):
            if isinstance(q, dict):
                return q.get('required', True)
            return q.required
        
        def get_id(q):
            if isinstance(q, dict):
                return q.get('id', '')
            return q.id
        
        required_questions = [q for q in questions if is_required(q)]
        
        if not required_questions:
            return True
        
        answered_required = sum(1 for q in required_questions if get_id(q) in answers)
        return answered_required >= len(required_questions) * 0.8  # 80% threshold


    def process_answers(self, answers: Dict[str, Any]) -> Dict[str, Any]:
        """Process and validate user answers"""
        processed = {}
        
        for key, value in answers.items():
            # Clean and validate each answer
            if isinstance(value, str):
                processed[key] = value.strip()
            elif isinstance(value, list):
                processed[key] = [v.strip() for v in value]
            else:
                processed[key] = value
        
        return processed

    def generate_dynamic_questions(self, prompt: str, transcription: Dict, 
                                 visual_analysis: Dict, existing_answers: Dict[str, Any]) -> List[Question]:
        """
        Generate dynamic, context-aware questions using Ollama based on 
        video content and user request.
        """
        
        system_prompt = """ERES UN ASISTENTE DE EDICIÓN DE VIDEO PROFESIONAL.
Tu tarea es generar preguntas inteligentes para el usuario basándote en su solicitud y el contenido del video (transcripción y visuales).

REGLAS:
1. Genera entre 3 y 5 preguntas RELEVANTES.
2. Si ya hay información en el prompt o en las respuestas existentes, NO vuelvas a preguntar lo mismo.
3. Las preguntas deben ayudar a definir el estilo, ritmo, formato o intención del video.
4. Formato de salida: JSON ESTRICTO (una lista de objetos que sigan el esquema definido).

ESQUEMA DE PREGUNTA:
{
  "id": "string único",
  "category": "format|platform|duration|rhythm|tone|music|voice_over|subtitles|style",
  "question": "texto de la pregunta",
  "type": "single_choice|multiple_choice|text|number",
  "options": ["opción 1", "opción 2"] (solo si es choice),
  "required": true/false,
  "help_text": "explicación breve"
}

Responde SOLO con el JSON."""

        user_input = f"""
[PROMPT DEL USUARIO]: {prompt}
[TRANSCRIPCIÓN DEL VIDEO]: {json.dumps(transcription)}
[ANÁLISIS VISUAL]: {json.dumps(visual_analysis)}
[RESPUESTAS EXISTENTES]: {json.dumps(existing_answers)}
"""

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ]
            )
            
            content = response['message']['content']
            
            # Robust JSON extraction
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            
            if start_idx != -1 and end_idx != 0:
                questions_data = json.loads(content[start_idx:end_idx])
                questions = []
                for q_data in questions_data:
                    questions.append(Question(**q_data))
                return questions
            else:
                # Fallback to templates if no JSON found
                print("No JSON found in Ollama response for questions. Falling back to templates.")
                return self.generate_questions(prompt, existing_answers)
                
        except Exception as e:
            print(f"Error generating dynamic questions: {e}. Falling back to templates.")
            return self.generate_questions(prompt, existing_answers)


# Example usage
if __name__ == "__main__":
    questioning = IntelligentQuestioning()
    
    # Test prompt
    test_prompt = "Make a nice video about my vacation"
    existing_answers = {}
    
    questions = questioning.generate_questions(test_prompt, existing_answers)
    
    print(f"Prompt: {test_prompt}")
    print(f"Generated {len(questions)} questions:")
    for q in questions:
        print(f"  [{q.category}] {q.question}")
        print(f"    Type: {q.type}, Required: {q.required}")
        if q.options:
            print(f"    Options: {', '.join(q.options[:3])}...")
        print()
