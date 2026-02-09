"""
PHASE 1 — PROMPT REFINER (MANDATORY)

Senior Prompt Engineer trained with:
- Internal prompting strategies from OpenAI, Anthropic, DeepMind
- Professional few-shot prompting
- Anti-hallucination and ambiguity reduction techniques

OBJECTIVE: Improve the user's prompt without changing its meaning.

STRICT RULES:
- Do NOT add new ideas
- Do NOT remove ideas
- Do NOT change emotional tone
- ONLY improve clarity, structure, specificity
"""

import json
import re
from typing import List, Dict, Any
from models.schemas import PromptRefinementOutput


class PromptRefiner:
    """Phase 1: Refine user prompts while preserving intent"""

    def __init__(self):
        self.common_ambiguities = [
            'vague timing words (soon, later, eventually)',
            'unclear subject references',
            'missing specific constraints',
            'ambiguous emotional descriptors',
            'undefined technical parameters',
            'unclear target audience',
            'missing context about source material'
        ]
        
    def analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """Analyze prompt for issues and ambiguities"""
        issues = []
        
        # Check for vague timing
        vague_timing = ['soon', 'later', 'eventually', 'sometime', 'at some point']
        if any(word in prompt.lower() for word in vague_timing):
            issues.append("Contains vague timing words that need specification")
        
        # Check for unclear emotional descriptors
        vague_emotions = ['good', 'nice', 'bad', 'interesting', 'emotional']
        if any(word in prompt.lower() for word in vague_emotions):
            issues.append("Emotional descriptors are too generic - needs specificity")
        
        # Check for missing technical details
        if 'video' in prompt.lower() and not any(x in prompt.lower() for x in ['format', 'resolution', 'aspect ratio']):
            issues.append("Missing technical specifications (format, resolution, aspect ratio)")
        
        # Check for missing duration
        if not any(x in prompt.lower() for x in ['minute', 'second', 'hour', 'length', 'duration', 'short', 'long']):
            issues.append("No duration or length constraints specified")
        
        # Check for missing platform context
        platforms = ['youtube', 'tiktok', 'instagram', 'facebook', 'twitter', 'film', 'cinema', 'tv']
        if not any(platform in prompt.lower() for platform in platforms):
            issues.append("Target platform not specified (affects format and style decisions)")
        
        # Check for vague action words
        vague_actions = ['make', 'do', 'create something', 'fix', 'improve']
        if any(phrase in prompt.lower() for phrase in vague_actions):
            issues.append("Action verbs are vague - needs specific editing actions")
        
        return {
            'issues_detected': issues,
            'original_length': len(prompt),
            'complexity_score': self._calculate_complexity(prompt)
        }
    
    def _calculate_complexity(self, prompt: str) -> int:
        """Calculate a complexity score for the prompt"""
        score = 0
        # More words = more complex
        score += len(prompt.split()) // 10
        
        # Technical terms add complexity
        technical_terms = ['transition', 'color grade', 'sound design', 'b-roll', 'montage']
        score += sum(1 for term in technical_terms if term in prompt.lower())
        
        return min(score, 10)  # Cap at 10
    
    def improve_prompt(self, prompt: str, analysis: Dict[str, Any]) -> str:
        """Generate improved version of the prompt"""
        issues = analysis['issues_detected']
        
        # Start with original
        improved = prompt.strip()
        
        # Add structure if missing
        if not any(marker in improved for marker in ['Goal:', 'Objective:', 'I want to']):
            improved = f"Goal: {improved[0].upper()}{improved[1:]}"
        
        # Improve based on detected issues
        improvements = []
        
        if "vague timing" in str(issues).lower():
            improved += "\n- Timing: Specific timestamps or sequence to be defined"
            improvements.append("Added timing specification placeholder")
        
        if "emotional descriptors" in str(issues).lower():
            improved += "\n- Emotional tone: [Specify exact emotion - e.g., melancholic, triumphant, suspenseful]"
            improvements.append("Requested specific emotional tone clarification")
        
        if "technical specifications" in str(issues).lower():
            improved += "\n- Technical: [Format: 16:9/9:16/1:1], [Resolution: 1080p/4K], [Frame rate if relevant]"
            improvements.append("Added technical specification section")
        
        if "duration" in str(issues).lower():
            improved += "\n- Duration: [Target length - e.g., 30 seconds, 2 minutes, feature length]"
            improvements.append("Added duration constraint placeholder")
        
        if "platform" in str(issues).lower():
            improved += "\n- Platform: [YouTube/TikTok/Instagram/Film/etc.] - affects pacing and format"
            improvements.append("Added platform specification for format decisions")
        
        if "vague action" in str(issues).lower():
            improved = improved.replace("make a video", "edit raw footage into a cinematic sequence")
            improved = improved.replace("create something", "produce a narrative-driven edit")
            improvements.append("Replaced vague action verbs with specific editing terminology")
        
        # Add quality section if complex enough
        if analysis['complexity_score'] > 3:
            improved += "\n- Quality: Professional cinematic standards with attention to pacing, audio sync, and visual flow"
            improvements.append("Added quality standards specification")
        
        return improved, improvements
    
    def refine(self, original_prompt: str) -> Dict[str, Any]:
        """
        Main refinement method.
        
        Returns dict matching PromptRefinementOutput schema:
        {
          "original_prompt": "...",
          "improved_prompt": "...",
          "issues_detected": [...],
          "improvements_made": [...],
          "user_action_required": "accept | revise"
        }
        """
        if not original_prompt or not original_prompt.strip():
            return {
                "original_prompt": "",
                "improved_prompt": "",
                "issues_detected": ["Empty prompt provided"],
                "improvements_made": [],
                "user_action_required": "revise"
            }
        
        # Analyze the prompt
        analysis = self.analyze_prompt(original_prompt)
        
        # Generate improved version
        improved_prompt, improvements = self.improve_prompt(original_prompt, analysis)
        
        # Determine if revision is needed
        needs_revision = len(analysis['issues_detected']) > 2
        
        return {
            "original_prompt": original_prompt,
            "improved_prompt": improved_prompt,
            "issues_detected": analysis['issues_detected'],
            "improvements_made": improvements,
            "user_action_required": "revise" if needs_revision else "accept"
        }
    
    def refine_with_feedback(self, original_prompt: str, previous_improved: str, feedback: str) -> Dict[str, Any]:
        """
        Generate new refinement based on user feedback.
        
        If user rejects first attempt, use feedback to create better version.
        """
        # Parse feedback for specific issues
        feedback_lower = feedback.lower()
        
        # Adjust based on feedback
        adjusted_prompt = previous_improved
        
        if 'too long' in feedback_lower or 'verbose' in feedback_lower:
            # Make it more concise
            lines = adjusted_prompt.split('\n')
            adjusted_prompt = lines[0]  # Keep only the main goal
            
        if 'too technical' in feedback_lower or 'simple' in feedback_lower:
            # Remove technical placeholders
            adjusted_prompt = re.sub(r'\n- Technical:.*', '', adjusted_prompt)
            adjusted_prompt = re.sub(r'\n- Duration:.*', '', adjusted_prompt)
            
        if 'more detail' in feedback_lower or 'elaborate' in feedback_lower:
            # Add more structure
            if 'Style:' not in adjusted_prompt:
                adjusted_prompt += "\n- Style: [Cinematic approach - documentary, narrative, experimental, etc.]"
            if 'Audio:' not in adjusted_prompt:
                adjusted_prompt += "\n- Audio: [Music style, voice-over needs, sound design requirements]"
        
        # Re-analyze
        new_analysis = self.analyze_prompt(adjusted_prompt)
        
        return {
            "original_prompt": original_prompt,
            "improved_prompt": adjusted_prompt,
            "issues_detected": new_analysis['issues_detected'],
            "improvements_made": ["Adjusted based on user feedback"] + self.improve_prompt(adjusted_prompt, new_analysis)[1],
            "user_action_required": "accept",
            "feedback_incorporated": feedback
        }


# Example usage and testing
if __name__ == "__main__":
    refiner = PromptRefiner()
    
    # Test cases
    test_prompts = [
        "Make a nice video about my vacation",
        "Create a cinematic edit of my interview footage for YouTube, 5 minutes long, emotional tone",
        "Fix this wedding video to make it more emotional"
    ]
    
    for prompt in test_prompts:
        print("=" * 60)
        print(f"ORIGINAL: {prompt}")
        result = refiner.refine(prompt)
        print(f"IMPROVED: {result['improved_prompt']}")
        print(f"ISSUES: {result['issues_detected']}")
        print(f"ACTION: {result['user_action_required']}")
        print()
