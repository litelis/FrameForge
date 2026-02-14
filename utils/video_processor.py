
import os
import json
import torch
import whisper
import cv2
import numpy as np
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from typing import List, Dict, Any

class AudioAnalysis:
    """Phase 1: Audio Analysis using OpenAI Whisper"""
    
    def __init__(self, model_name: str = "base"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading Whisper model '{model_name}' on {self.device}...")
        self.model = whisper.load_model(model_name, device=self.device)
        
    def transcribe(self, video_path: str) -> Dict[str, Any]:
        """Generate timestamped transcription"""
        print(f"Transcribing audio from {video_path}...")
        result = self.model.transcribe(video_path, verbose=False)
        
        segments = []
        for segment in result.get("segments", []):
            segments.append({
                "start": segment["start"],
                "end": segment["end"],
                "text": segment["text"].strip()
            })
        
        return {
            "full_text": result.get("text", "").strip(),
            "segments": segments,
            "language": result.get("language", "en")
        }

class VisualAnalysis:
    """Phase 2: Visual Analysis using CLIP"""
    
    def __init__(self, model_name: str = "openai/clip-vit-base-patch32"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading CLIP model '{model_name}' on {self.device}...")
        self.model = CLIPModel.from_pretrained(model_name).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(model_name)
        
    def analyze_video(self, video_path: str, search_concepts: List[str] = None, interval: int = 2) -> Dict[str, Any]:
        """Sample video and match frames against search concepts"""
        if search_concepts is None:
            search_concepts = ["nature", "city", "people", "action", "emotional", "cinematic", "interview"]
            
        print(f"Analyzing visuals in {video_path} every {interval} seconds...")
        
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            return {"scenes": [], "key_frames": [], "visual_quality": {}}
            
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
        
        # Format as expected by the session
        return {
            "scenes": detections,
            "key_frames": [d["time"] for d in detections if d["score"] > 0.5],
            "visual_quality": {"overall_score": 0.8} # Placeholder
        }
