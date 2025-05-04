# src/video_processor/detector.py

import numpy as np

class Detector:
    def __init__(self, model):
        self.model = model
        self.min_clip_duration = 60  # 1 minuto
        self.max_clip_duration = 90  # 1.5 minutos
    
    def detect_highlights(self, video):
        """Detecta los momentos más interesantes en el video"""
        # Análisis frame por frame
        scores = []
        for frame in video.iter_frames():
            score = self.model.analyze_frame(frame)
            scores.append(score)
            
        # Normalizar puntuaciones
        scores = np.array(scores)
        scores = (scores - scores.min()) / (scores.max() - scores.min())
        
        # Encontrar los mejores segmentos
        highlights = self._find_best_segments(scores, video.fps)
        
        return highlights
    
    def _find_best_segments(self, scores, fps):
        """Encuentra los mejores segmentos basados en las puntuaciones"""
        segments = []
        threshold = np.percentile(scores, 75)  # Top 25% de momentos
        
        i = 0
        while i < len(scores):
            if scores[i] > threshold:
                start_frame = i
                # Buscar el final del segmento
                while i < len(scores) and scores[i] > threshold:
                    i += 1
                end_frame = i
                
                # Convertir frames a segundos
                start_time = start_frame / fps
                end_time = end_frame / fps
                
                # Ajustar duración del clip
                duration = end_time - start_time
                if duration >= self.min_clip_duration:
                    if duration > self.max_clip_duration:
                        end_time = start_time + self.max_clip_duration
                    segments.append((start_time, end_time))
            i += 1
        
        return segments