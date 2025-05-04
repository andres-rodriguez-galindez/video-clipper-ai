# src/ai_models/highlight_detector.py

import cv2
import numpy as np
import torch
import torch.nn.functional as F
from sklearn.preprocessing import MinMaxScaler

class HighlightDetector:
    def __init__(self, device="cpu"):
        self.scaler = MinMaxScaler()
        self.device = device
        self.batch_size = 32  # Procesar múltiples frames a la vez
        
    def analyze_frame(self, frame):
        try:
            # Convertir a tensor y mover a GPU si está disponible
            if isinstance(frame, np.ndarray):
                frame_tensor = torch.from_numpy(frame).to(self.device)
                if frame_tensor.dtype == torch.uint8:
                    frame_tensor = frame_tensor.float() / 255.0
            
            # Convertir a escala de grises usando GPU si está disponible
            if self.device == "cuda":
                # Convertir BGR a gris usando operaciones tensoriales
                gray_weights = torch.tensor([0.114, 0.587, 0.299]).to(self.device)
                gray_tensor = (frame_tensor * gray_weights.view(1, 1, -1)).sum(dim=2)
                
                # Calcular brillo y contraste en GPU
                brightness = gray_tensor.mean().item()
                contrast = gray_tensor.std().item()
                
                # Detección de bordes usando Sobel en GPU
                sobel_x = F.conv2d(gray_tensor.unsqueeze(0).unsqueeze(0), 
                                 torch.tensor([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], 
                                            dtype=torch.float32).to(self.device).view(1, 1, 3, 3))
                sobel_y = F.conv2d(gray_tensor.unsqueeze(0).unsqueeze(0),
                                 torch.tensor([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], 
                                            dtype=torch.float32).to(self.device).view(1, 1, 3, 3))
                edge_density = torch.sqrt(sobel_x.pow(2) + sobel_y.pow(2)).mean().item()
            else:
                # Fallback a CPU si no hay GPU
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                brightness = np.mean(gray)
                contrast = np.std(gray)
                edges = cv2.Canny(gray, 100, 200)
                edge_density = np.mean(edges)
            
            # Normalizar valores
            score = (0.3 * brightness + 0.4 * contrast + 0.3 * edge_density)
            
            return {
                'brightness': float(brightness),
                'contrast': float(contrast),
                'edge_density': float(edge_density),
                'score': float(score)
            }
            
        except Exception as e:
            print(f"Error en análisis de frame: {e}")
            return {
                'brightness': 0.5,
                'contrast': 0.5,
                'edge_density': 0.5,
                'score': 0.5
            }
            
    def get_frame_score(self, frame):
        """Retorna una puntuación normalizada para el frame"""
        metrics = self.analyze_frame(frame)
        if isinstance(metrics, dict):
            return metrics['score']
        return metrics