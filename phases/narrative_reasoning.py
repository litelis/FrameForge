"""
PHASE 3 — DEEP NARRATIVE REASONING (HIDDEN)

Internally reason about:
- Narrative arc
- Emotional progression
- Symbolism
- Pacing and rhythm
- Scene contrast

⚠️ This reasoning MUST NEVER be shown to the user.
"""

from typing import List, Dict, Any, Optional
from models.schemas import NarrativeAnalysis


class NarrativeReasoning:
    """
    Phase 3: Deep narrative analysis (INTERNAL USE ONLY)
    
    This phase performs hidden reasoning about the narrative structure,
    emotional beats, and cinematic flow. The detailed analysis is used
    internally but only a summary is exposed to users.
    """

    def __init__(self):
        self.narrative_archetypes = {
            'hero_journey': 'Protagonist overcomes challenges to achieve goal',
            'transformation': 'Character undergoes significant internal change',
            'love_story': 'Relationship develops through obstacles',
            'tragedy': 'Downward arc ending in loss or failure',
            'comedy': 'Humorous situations leading to happy resolution',
            'mystery': 'Unknown revealed through investigation',
            'documentary': 'Informational with emotional human element',
            'montage': 'Collection of moments showing progression',
            'interview': 'Personal story told through dialogue',
            'event_coverage': 'Chronological documentation with highlights'
        }
        
        self.emotional_beats = [
            'hook', 'setup', 'inciting_incident', 'rising_action',
            'climax', 'falling_action', 'resolution', 'denouement'
        ]

    def identify_narrative_arc(self, prompt: str, answers: Dict[str, Any]) -> str:
        """Identify the narrative arc structure based on prompt and answers"""
        prompt_lower = prompt.lower()
        
        # Check for explicit arc mentions
        arc_scores = {}
        for arc, description in self.narrative_archetypes.items():
            score = 0
            # Check keywords in prompt
            if arc.replace('_', ' ') in prompt_lower:
                score += 3
            if arc in prompt_lower:
                score += 3
            
            # Check related keywords
            keywords = description.lower().split()
            for keyword in keywords:
                if keyword in prompt_lower and len(keyword) > 4:
                    score += 1
            
            arc_scores[arc] = score
        
        # Check answers for clues
        tone = answers.get('emotional_tone', '').lower()
        source = answers.get('source_material', [])
        
        # Adjust based on tone
        if 'tragedy' in tone or 'sad' in tone or 'melancholic' in tone:
            arc_scores['tragedy'] = arc_scores.get('tragedy', 0) + 2
        if 'inspirational' in tone or 'motivational' in tone:
            arc_scores['hero_journey'] = arc_scores.get('hero_journey', 0) + 2
        if 'romantic' in tone or 'love' in tone:
            arc_scores['love_story'] = arc_scores.get('love_story', 0) + 2
        
        # Adjust based on source material
        if 'interview footage' in source:
            arc_scores['interview'] = arc_scores.get('interview', 0) + 3
        if 'b-roll' in source and 'interview' in source:
            arc_scores['documentary'] = arc_scores.get('documentary', 0) + 2
        
        # Return highest scoring arc
        if arc_scores:
            best_arc = max(arc_scores, key=arc_scores.get)
            if arc_scores[best_arc] > 0:
                return best_arc
        
        # Default based on content type
        if 'interview' in prompt_lower:
            return 'interview'
        elif any(x in prompt_lower for x in ['wedding', 'event', 'vacation', 'trip']):
            return 'montage'
        else:
            return 'documentary'

    def map_emotional_progression(self, prompt: str, answers: Dict[str, Any], 
                                   transcription: Dict, visual_analysis: Dict) -> List[Dict[str, Any]]:
        """Map the emotional progression through the narrative"""
        progression = []
        
        # Get tone from answers
        tone = answers.get('emotional_tone', 'neutral')
        rhythm = answers.get('editing_rhythm', 'medium')
        
        # Define emotional curve based on tone and rhythm
        if 'slow' in rhythm:
            # Slow, contemplative progression
            progression = [
                {'beat': 'hook', 'emotion': 'curiosity', 'intensity': 0.3, 'pacing': 'slow'},
                {'beat': 'setup', 'emotion': tone, 'intensity': 0.4, 'pacing': 'slow'},
                {'beat': 'rising_action', 'emotion': tone, 'intensity': 0.5, 'pacing': 'medium'},
                {'beat': 'climax', 'emotion': 'intense_' + tone, 'intensity': 0.7, 'pacing': 'slow'},
                {'beat': 'resolution', 'emotion': 'peaceful', 'intensity': 0.3, 'pacing': 'very_slow'}
            ]
        elif 'fast' in rhythm:
            # Fast, energetic progression
            progression = [
                {'beat': 'hook', 'emotion': 'excitement', 'intensity': 0.7, 'pacing': 'fast'},
                {'beat': 'setup', 'emotion': tone, 'intensity': 0.5, 'pacing': 'fast'},
                {'beat': 'rising_action', 'emotion': 'building_' + tone, 'intensity': 0.8, 'pacing': 'very_fast'},
                {'beat': 'climax', 'emotion': 'peak_' + tone, 'intensity': 1.0, 'pacing': 'fast'},
                {'beat': 'resolution', 'emotion': 'satisfaction', 'intensity': 0.6, 'pacing': 'medium'}
            ]
        else:
            # Balanced progression
            progression = [
                {'beat': 'hook', 'emotion': 'interest', 'intensity': 0.5, 'pacing': 'medium'},
                {'beat': 'setup', 'emotion': tone, 'intensity': 0.4, 'pacing': 'medium'},
                {'beat': 'rising_action', 'emotion': 'developing_' + tone, 'intensity': 0.6, 'pacing': 'medium'},
                {'beat': 'climax', 'emotion': 'intense_' + tone, 'intensity': 0.9, 'pacing': 'medium_fast'},
                {'beat': 'resolution', 'emotion': 'fulfillment', 'intensity': 0.5, 'pacing': 'slow'}
            ]
        
        # Adjust based on ending style
        ending = answers.get('ending_style', '')
        if 'open' in ending.lower():
            progression[-1]['emotion'] = 'contemplation'
            progression[-1]['intensity'] = 0.4
        elif 'cliffhanger' in ending.lower():
            progression[-1]['emotion'] = 'suspense'
            progression[-1]['intensity'] = 0.8
        
        return progression

    def analyze_scene_contrasts(self, visual_analysis: Dict, emotional_progression: List[Dict]) -> List[Dict[str, Any]]:
        """Identify contrasts between scenes for dynamic editing"""
        contrasts = []
        
        # Handle None visual_analysis
        if not visual_analysis:
            return contrasts
        
        # Analyze visual elements for contrast opportunities
        scenes = visual_analysis.get('scenes', []) if visual_analysis else []

        
        if len(scenes) >= 2:
            for i in range(len(scenes) - 1):
                current = scenes[i]
                next_scene = scenes[i + 1]
                
                # Detect contrast types
                contrast_types = []
                
                # Lighting contrast
                if current.get('lighting') != next_scene.get('lighting'):
                    contrast_types.append('lighting')
                
                # Color contrast
                if current.get('color_palette') != next_scene.get('color_palette'):
                    contrast_types.append('color')
                
                # Movement contrast
                if current.get('movement') != next_scene.get('movement'):
                    contrast_types.append('movement')
                
                # Scale contrast
                if current.get('scale') != next_scene.get('scale'):
                    contrast_types.append('scale')
                
                if contrast_types:
                    contrasts.append({
                        'between_scenes': [i, i + 1],
                        'contrast_types': contrast_types,
                        'emotional_shift': {
                            'from': emotional_progression[min(i, len(emotional_progression)-1)]['emotion'],
                            'to': emotional_progression[min(i+1, len(emotional_progression)-1)]['emotion']
                        },
                        'recommended_transition': 'cut' if 'movement' in contrast_types else 'fade'
                    })
        
        return contrasts

    def calculate_pacing(self, answers: Dict[str, Any], 
                        emotional_progression: List[Dict]) -> Dict[str, Any]:
        """Calculate recommended pacing for the edit"""
        duration_answer = answers.get('target_duration', '')
        rhythm = answers.get('editing_rhythm', 'medium')
        
        # Parse duration
        duration_seconds = 180  # Default 3 minutes
        if '15-30' in duration_answer:
            duration_seconds = 30
        elif '30-60' in duration_answer:
            duration_seconds = 60
        elif '1-3' in duration_answer:
            duration_seconds = 180
        elif '3-10' in duration_answer:
            duration_seconds = 600
        elif '10-30' in duration_answer:
            duration_seconds = 1800
        
        # Calculate cuts per minute based on rhythm
        cuts_per_minute = {
            'slow': 8,
            'medium': 15,
            'fast': 30
        }.get(rhythm, 15)
        
        # Adjust for platform
        platform = answers.get('target_platform', '')
        if 'tiktok' in platform.lower() or 'reels' in platform.lower():
            cuts_per_minute = max(cuts_per_minute, 25)  # Faster for social
        
        total_cuts = int((duration_seconds / 60) * cuts_per_minute)
        
        return {
            'total_duration_seconds': duration_seconds,
            'cuts_per_minute': cuts_per_minute,
            'estimated_total_cuts': total_cuts,
            'average_shot_length_seconds': int(60 / cuts_per_minute),
            'rhythm_pattern': self._generate_rhythm_pattern(emotional_progression, cuts_per_minute)
        }

    def _generate_rhythm_pattern(self, emotional_progression: List[Dict], 
                                  base_cuts_per_minute: int) -> List[Dict[str, Any]]:
        """Generate a rhythm pattern that follows emotional beats"""
        pattern = []
        
        for beat in emotional_progression:
            intensity = beat['intensity']
            pacing = beat['pacing']
            
            # Adjust cuts based on emotional intensity
            if intensity > 0.8:  # High intensity = faster cuts
                beat_cuts = int(base_cuts_per_minute * 1.5)
            elif intensity < 0.4:  # Low intensity = slower cuts
                beat_cuts = int(base_cuts_per_minute * 0.6)
            else:
                beat_cuts = base_cuts_per_minute
            
            pattern.append({
                'beat': beat['beat'],
                'cuts_per_minute': beat_cuts,
                'pacing': pacing,
                'intensity': intensity
            })
        
        return pattern

    def detect_symbolism(self, prompt: str, visual_analysis: Dict) -> Optional[str]:
        """Detect potential symbolic elements in the content"""
        prompt_lower = prompt.lower()
        
        # Common symbolic elements
        symbols = []
        
        if any(word in prompt_lower for word in ['journey', 'travel', 'road', 'path']):
            symbols.append("Journey/Path = Life's progression or personal growth")
        
        if any(word in prompt_lower for word in ['light', 'sun', 'bright', 'dark', 'shadow']):
            symbols.append("Light/Dark = Hope/despair, knowledge/ignorance, good/evil")
        
        if any(word in prompt_lower for word in ['water', 'ocean', 'river', 'rain']):
            symbols.append("Water = Emotions, purification, life flow")
        
        if any(word in prompt_lower for word in ['mountain', 'climb', 'peak', 'height']):
            symbols.append("Mountains/Height = Challenges, achievement, perspective")
        
        if any(word in prompt_lower for word in ['door', 'gate', 'entrance', 'threshold']):
            symbols.append("Doors/Gates = New opportunities, transitions, choices")
        
        if any(word in prompt_lower for word in ['mirror', 'reflection', 'glass']):
            symbols.append("Mirrors = Self-reflection, truth, identity")
        
        if symbols:
            return "; ".join(symbols)
        
        return None

    def analyze(self, prompt: str, answers: Dict[str, Any],
                transcription: Dict, visual_analysis: Dict) -> Dict[str, Any]:
        """
        Main analysis method.
        
        Performs comprehensive narrative analysis but returns only
        what should be stored internally. User-facing output is
        filtered by the API endpoint.
        """
        # Identify narrative structure
        narrative_arc = self.identify_narrative_arc(prompt, answers)
        
        # Map emotional progression
        emotional_progression = self.map_emotional_progression(
            prompt, answers, transcription, visual_analysis
        )
        
        # Analyze scene contrasts
        scene_contrasts = self.analyze_scene_contrasts(
            visual_analysis, emotional_progression
        )
        
        # Calculate pacing
        pacing = self.calculate_pacing(answers, emotional_progression)
        
        # Detect symbolism
        symbolism = self.detect_symbolism(prompt, visual_analysis)
        
        # Determine dominant tone
        dominant_tone = answers.get('emotional_tone', 'neutral')
        
        return {
            'narrative_arc': narrative_arc,
            'emotional_progression': emotional_progression,
            'dominant_tone': dominant_tone,
            'pacing_recommendation': pacing,
            'scene_contrasts': scene_contrasts,
            'symbolism_notes': symbolism,
            # Internal detailed analysis (not exposed to users)
            '_internal_analysis': {
                'arc_confidence': 'high' if narrative_arc != 'documentary' else 'medium',
                'emotional_beats_count': len(emotional_progression),
                'contrast_opportunities': len(scene_contrasts),
                'pacing_notes': f"Base rhythm: {pacing['cuts_per_minute']} cuts/min"
            }
        }


# Example usage
if __name__ == "__main__":
    reasoning = NarrativeReasoning()
    
    # Test data
    test_prompt = "Create a cinematic edit of my interview about overcoming challenges"
    test_answers = {
        'emotional_tone': 'Inspirational / Motivational',
        'editing_rhythm': 'Medium (balanced, standard pacing)',
        'target_duration': '3-10 minutes (Long YouTube)',
        'target_platform': 'YouTube (long-form, 16:9)',
        'ending_style': 'Emotional peak (strong feeling)'
    }
    test_transcription = {}
    test_visual = {'scenes': [{'lighting': 'bright'}, {'lighting': 'dark'}]}
    
    result = reasoning.analyze(test_prompt, test_answers, test_transcription, test_visual)
    
    print("NARRATIVE ANALYSIS (INTERNAL)")
    print("=" * 50)
    print(f"Arc: {result['narrative_arc']}")
    print(f"Dominant Tone: {result['dominant_tone']}")
    print(f"Symbolism: {result['symbolism_notes']}")
    print(f"Pacing: {result['pacing_recommendation']['cuts_per_minute']} cuts/min")
    print(f"Emotional Beats: {len(result['emotional_progression'])}")
