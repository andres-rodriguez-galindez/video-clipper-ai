# src/main.py

from video_processor.clipper import Clipper
from video_processor.detector import Detector
from ai_models.highlight_detector import HighlightDetector
from utils.video_utils import load_video, save_video

def main():
    video_path = "ruta/al/video.mp4"  # Cambiar a la ruta del video
    output_path = "ruta/al/video_recortado.mp4"  # Cambiar a la ruta de salida

    # Cargar el video
    video = load_video(video_path)

    # Inicializar el detector y el clipper
    detector = Detector()
    clipper = Clipper()

    # Detectar los mejores momentos
    highlights = detector.detect_highlights(video)

    # Recortar el video en segmentos
    for highlight in highlights:
        clip = clipper.clip_video(video, highlight.start, highlight.end)
        save_video(clip, output_path)

if __name__ == "__main__":
    main()