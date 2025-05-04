# src/video_processor/detector.py

import numpy as np
import time

class Detector:
    def __init__(self, model):
        self.model = model
        self.min_clip_duration = 60  # 1 minuto
        self.max_clip_duration = 90  # 1.5 minutos
        self.stats = {
            'tiempos_analisis': [],
            'tiempos_recorte': [],
            'tiempos_exportacion': []
        }
        
    def _find_best_segments(self, scores, fps):
        """
        Encuentra los mejores segmentos del video basados en las puntuaciones
        """
        # Convertir scores a array de numpy para operaciones más eficientes
        scores = np.array(scores)
        
        # Calcular el umbral basado en el percentil 75
        threshold = np.percentile(scores, 75)
        
        # Encontrar segmentos continuos que superan el umbral
        segments = []
        start_frame = None
        
        for i in range(len(scores)):
            if scores[i] > threshold and start_frame is None:
                start_frame = i
            elif scores[i] <= threshold and start_frame is not None:
                # Convertir frames a segundos
                start_time = start_frame / fps
                end_time = i / fps
                duration = end_time - start_time
                
                # Verificar duración mínima y máxima
                if duration >= self.min_clip_duration:
                    if duration > self.max_clip_duration:
                        end_time = start_time + self.max_clip_duration
                    segments.append((start_time, end_time))
                start_frame = None
        
        # Manejar el último segmento si existe
        if start_frame is not None:
            start_time = start_frame / fps
            end_time = len(scores) / fps
            duration = end_time - start_time
            
            if duration >= self.min_clip_duration:
                if duration > self.max_clip_duration:
                    end_time = start_time + self.max_clip_duration
                segments.append((start_time, end_time))
        
        return segments

    def detect_highlights(self, video, progress_callback=None):
        """Detecta los momentos más interesantes en el video"""
        tiempo_inicio = time.time()
        
        # Análisis frame por frame con estadísticas
        scores = []
        frames_processed = 0
        
        for frame in video.iter_frames():
            frame_inicio = time.time()
            result = self.model.analyze_frame(frame)
            # Extraer solo el valor de score del diccionario
            score = result['score'] if isinstance(result, dict) else result
            scores.append(score)
            frames_processed += 1
            
            self.stats['tiempos_analisis'].append(time.time() - frame_inicio)
            
            if progress_callback:
                progress_callback()
        
        # Calcular tiempo total
        tiempo_total = time.time() - tiempo_inicio
        
        # Encontrar los mejores segmentos
        highlights = self._find_best_segments(scores, video.fps)
        
        if not highlights:
            print("No se encontraron momentos destacados que cumplan con los criterios")
            return [], tiempo_total
        
        return highlights, tiempo_total

    def get_stats_summary(self):
        """Retorna un resumen de las estadísticas"""
        if not self.stats['tiempos_analisis']:
            return "No hay estadísticas disponibles"
            
        return {
            'analisis_promedio': np.mean(self.stats['tiempos_analisis']),
            'recorte_promedio': np.mean(self.stats['tiempos_recorte']) if self.stats['tiempos_recorte'] else 0,
            'exportacion_promedio': np.mean(self.stats['tiempos_exportacion']) if self.stats['tiempos_exportacion'] else 0
        }