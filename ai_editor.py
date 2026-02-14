
import os
import json
import torch
import whisper
import cv2
import numpy as np
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from moviepy import VideoFileClip, concatenate_videoclips
import ollama
from typing import List, Dict, Any

class AudioAnalysis:
    """Phase 1: Audio Analysis using OpenAI Whisper"""
    
    def __init__(self, model_name: str = "base"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading Whisper model '{model_name}' on {self.device}...")
        self.model = whisper.load_model(model_name, device=self.device)
        
    def transcribe(self, video_path: str) -> List[Dict[str, Any]]:
        """Generate timestamped transcription"""
        print(f"Transcribing audio from {video_path}...")
        result = self.model.transcribe(video_path, verbose=False)
        
        transcription = []
        for segment in result.get("segments", []):
            transcription.append({
                "start": segment["start"],
                "end": segment["end"],
                "text": segment["text"].strip()
            })
        
        return transcription

class VisualAnalysis:
    """Phase 2: Visual Analysis using CLIP"""
    
    def __init__(self, model_name: str = "openai/clip-vit-base-patch32"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading CLIP model '{model_name}' on {self.device}...")
        self.model = CLIPModel.from_pretrained(model_name).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(model_name)
        
    def analyze_video(self, video_path: str, search_concepts: List[str], interval: int = 2) -> List[Dict[str, Any]]:
        """Sample video and match frames against search concepts"""
        print(f"Analyzing visuals in {video_path} every {interval} seconds...")
        
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        detections = []
        
        frame_idx = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            timestamp = frame_idx / fps
            
            # Sample every X seconds
            if frame_idx % int(fps * interval) == 0:
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(rgb_frame)
                
                # Process with CLIP
                inputs = self.processor(
                    text=search_concepts, 
                    images=pil_image, 
                    return_tensors="pt", 
                    padding=True
                ).to(self.device)
                
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    logits_per_image = outputs.logits_per_image
                    probs = logits_per_image.softmax(dim=1)
                
                # Get best match
                max_prob, max_idx = torch.max(probs[0], dim=0)
                
                detections.append({
                    "time": timestamp,
                    "description": search_concepts[max_idx.item()],
                    "score": float(max_prob.item())
                })
                
            frame_idx += 1
            if frame_idx >= total_frames:
                break
                
        cap.release()
        return detections

class NarrativeEngine:
    """Phase 3: Narrative Decision Engine using Ollama"""
    
    SYSTEM_PROMPT = """ERES UN EDITOR DE CINE DE ÉLITE GANADOR DEL OSCAR. Tienes acceso a la transcripción completa de una película y a un análisis visual de sus escenas.

TU OBJETIVO:
Crear una secuencia de video (edición) basada estrictamente en la solicitud del usuario, combinando los mejores momentos visuales con los diálogos más relevantes.

INPUTS QUE RECIBIRÁS:
1. [SOLICITUD]: La intención del usuario (ej: "Haz un trailer triste sobre el amor").
2. [TRANSCRIPCIÓN]: Lista de diálogos con tiempos {start, end, text}.
3. [VISUALES]: Lista de momentos visuales clave detectados {time, description, score}.

INSTRUCCIONES DE RAZONAMIENTO:
1. Busca en la [TRANSCRIPCIÓN] frases que apoyen la narrativa solicitada.
2. Busca en los [VISUALES] imágenes que coincidan con esas frases o creen un contraste poético.
3. Prioriza clips donde haya coincidencia semántica (ej: si hablan de "muerte", busca visuales oscuros o tristes).
4. Mantén un ritmo: alterna entre planos con diálogo y planos puramente visuales/musicales.

FORMATO DE SALIDA (JSON ESTRICTO):
Debes responder ÚNICAMENTE con un objeto JSON válido. Sin texto antes ni después.

{
  "title": "Título Creativo",
  "rationale": "Breve explicación de por qué elegiste este enfoque",
  "cuts": [
    {
      "start": "00:00:10",
      "end": "00:00:15",
      "type": "visual",
      "description": "Plano de establecimiento del jardín"
    },
    {
      "start": "00:05:20",
      "end": "00:05:35",
      "type": "dialogue",
      "description": "Calisto hablando de su dolor"
    }
  ]
}"""

    def __init__(self, model_name: str = "llama3"):
        self.model_name = model_name
        
    def generate_plan(self, user_request: str, transcription: List[Dict], visual_analysis: List[Dict]) -> Dict[str, Any]:
        """Call Ollama to generate an editing plan"""
        print(f"Generating editing plan using {self.model_name} via Ollama...")
        
        prompt = f"""
[SOLICITUD]:
{user_request}

[TRANSCRIPCIÓN]:
{json.dumps(transcription, indent=2)}

[VISUALES]:
{json.dumps(visual_analysis, indent=2)}
"""

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = response['message']['content']
            
            # Robust JSON extraction
            try:
                # Find the first '{' and last '}'
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx != -1 and end_idx != 0:
                    json_str = content[start_idx:end_idx]
                    return json.loads(json_str)
                else:
                    raise ValueError("No JSON found in response")
            except Exception as e:
                print(f"Error parsing JSON from Ollama: {e}")
                print(f"Raw response: {content}")
                return None
                
        except Exception as e:
            print(f"Error communicating with Ollama: {e}")
            return None

class VideoRenderer:
    """Phase 4: Video Rendering using MoviePy"""
    
    def __init__(self):
        pass
        
    def _timestamp_to_seconds(self, ts: str) -> float:
        """Convert HH:MM:SS to seconds"""
        parts = ts.split(':')
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
        elif len(parts) == 2:
            return int(parts[0]) * 60 + float(parts[1])
        else:
            return float(ts)

    def render(self, video_path: str, plan: Dict[str, Any], output_path: str = "edited_video.mp4"):
        """Cut and concatenate clips exactly as defined in the plan"""
        print(f"Rendering final video to {output_path}...")
        
        main_clip = VideoFileClip(video_path)
        final_clips = []
        
        for cut in plan.get("cuts", []):
            start = self._timestamp_to_seconds(cut["start"])
            end = self._timestamp_to_seconds(cut["end"])
            
            print(f"  Cutting {cut['type']}: {start}s - {end}s ({cut.get('description', '')})")
            
            # Ensure boundaries are within clip duration
            start = max(0, min(start, main_clip.duration))
            end = max(start, min(end, main_clip.duration))
            
            if end > start:
                # Compatibility between MoviePy 1.x and 2.x
                if hasattr(main_clip, 'subclipped'):
                    clip = main_clip.subclipped(start, end)
                else:
                    clip = main_clip.subclip(start, end)
                final_clips.append(clip)
        
        if final_clips:
            final_video = concatenate_videoclips(final_clips)
            final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
            print(f"Video successfully rendered to {output_path}")
        else:
            print("No valid cuts found in plan. Skipping render.")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Fully Local AI-Powered Video Editor")
    parser.add_argument("video", help="Path to the local video file")
    parser.add_argument("prompt", help="Natural language user request")
    parser.add_argument("--concepts", nargs="+", default=["love", "fire", "sword", "sad woman", "action", "emotion"], help="Search concepts for CLIP")
    parser.add_argument("--output", default="edited_video.mp4", help="Path for the output video")
    parser.add_argument("--model", default="llama3", help="Ollama model to use")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.video):
        print(f"Error: Video file {args.video} not found.")
        return

    # 1. Audio Analysis
    audio_engine = AudioAnalysis(model_name="base")
    transcription = audio_engine.transcribe(args.video)
    
    # 2. Visual Analysis
    visual_engine = VisualAnalysis()
    visual_detections = visual_engine.analyze_video(args.video, args.concepts)
    
    # 3. Narrative Decision Engine
    narrative_engine = NarrativeEngine(model_name=args.model)
    editing_plan = narrative_engine.generate_plan(args.prompt, transcription, visual_detections)
    
    if not editing_plan:
        print("Failed to generate editing plan. Exiting.")
        return
        
    print(f"\nEditing Plan Generated: {editing_plan.get('title', 'Untitled')}")
    print(f"Rationale: {editing_plan.get('rationale', 'No rationale provided')}")
    
    # 4. Video Rendering
    renderer = VideoRenderer()
    renderer.render(args.video, editing_plan, args.output)

if __name__ == "__main__":
    main()
