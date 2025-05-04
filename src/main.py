# src/main.py

from video_processor.detector import Detector
from ai_models.highlight_detector import HighlightDetector
import cv2
import os
from pathlib import Path
import time
from datetime import timedelta
import torch
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
try:
    from moviepy.editor import VideoFileClip
except ImportError:
    print("Error: Faltan dependencias. Ejecuta: pip install moviepy tqdm")
    exit(1)

def verify_video_path(path):
    """Verifica si el archivo de video existe y tiene una extensión válida"""
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
    path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"El archivo {path} no existe")
    
    if path.suffix.lower() not in video_extensions:
        raise ValueError(f"El archivo debe tener una de estas extensiones: {', '.join(video_extensions)}")
    
    return str(path.absolute())

def format_time(seconds):
    """Convierte segundos a formato HH:MM:SS"""
    return str(timedelta(seconds=int(seconds)))

def process_clip(clip_info):
    """Procesa un clip individual"""
    i, (start_time, end_time), video_path, output_dir = clip_info
    try:
        video = VideoFileClip(video_path)
        clip = video.subclip(start_time, end_time)
        output_path = output_dir / f"highlight_{i}.mp4"
        
        clip.write_videofile(
            str(output_path),
            codec='libx264',
            audio_codec='aac',
            temp_audiofile=f'temp-audio_{i}.m4a',
            remove_temp=True,
            logger=None,
            preset='ultrafast'  # Más rápido encoding
        )
        video.close()
        return i, True, output_path
    except Exception as e:
        return i, False, str(e)

def main():
    # Verificar disponibilidad de GPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Usando dispositivo: {device}")
    
    # Crear el detector de momentos destacados
    highlight_model = HighlightDetector(device=device)
    detector = Detector(model=highlight_model)
    
    while True:
        try:
            # Cargar el video
            video_path = input("Introduce la ruta del video (o 'q' para salir): ")
            
            if video_path.lower() == 'q':
                print("Programa terminado")
                break
                
            # Verificar la ruta del video
            video_path = verify_video_path(video_path)
            
            # Crear directorio para los clips si no existe
            output_dir = Path('clips_destacados')
            output_dir.mkdir(exist_ok=True)
            
            # Iniciar temporizador
            tiempo_inicio = time.time()
            
            # Cargar el video
            print("\nCargando video...")
            video = VideoFileClip(video_path)
            duracion_video = video.duration
            print(f"Duración del video: {format_time(duracion_video)}")
            
            # Detectar momentos destacados
            print("\nAnalizando video...")
            highlights = detector.detect_highlights(video)
            
            tiempo_analisis = time.time() - tiempo_inicio
            print(f"\nAnálisis completado en {format_time(tiempo_analisis)}")
            
            if not highlights:
                print("No se encontraron momentos destacados en el video.")
                continue
                
            print(f"Se encontraron {len(highlights)} momentos destacados")
            
            # Mostrar información de los clips
            print("\nInformación de los clips encontrados:")
            for i, (start_time, end_time) in enumerate(highlights, 1):
                duration = end_time - start_time
                print(f"\nClip {i}:")
                print(f"  └─ Inicio: {format_time(start_time)}")
                print(f"  └─ Fin: {format_time(end_time)}")
                print(f"  └─ Duración: {format_time(duration)}")
            
            # Preguntar si desea guardar los clips
            respuesta = input("\n¿Desea guardar los clips? (s/n): ").lower()
            if respuesta != 's':
                print("Operación cancelada.")
                continue
            
            # Guardar los clips en paralelo
            print("\nGuardando clips...")
            tiempo_guardado = time.time()
            
            # Preparar información para procesamiento paralelo
            clip_infos = [
                (i, (start_time, end_time), video_path, output_dir)
                for i, (start_time, end_time) in enumerate(highlights, 1)
            ]
            
            # Procesar clips en paralelo
            with ThreadPoolExecutor(max_workers=min(4, len(highlights))) as executor:
                futures = list(tqdm(
                    executor.map(process_clip, clip_infos),
                    total=len(clip_infos),
                    desc="Procesando clips"
                ))
            
            # Verificar resultados
            errores = []
            for i, success, result in futures:
                if success:
                    print(f"✓ Clip {i} guardado en: {result}")
                else:
                    print(f"✗ Error en clip {i}: {result}")
                    errores.append(i)
            
            if errores:
                print(f"\n⚠️ {len(errores)} clips tuvieron errores: {errores}")
            
            tiempo_total = time.time() - tiempo_inicio
            print("\n✓ Proceso completado:")
            print(f"└─ Tiempo de análisis: {format_time(tiempo_analisis)}")
            print(f"└─ Tiempo de guardado: {format_time(time.time() - tiempo_guardado)}")
            print(f"└─ Tiempo total: {format_time(tiempo_total)}")
            print(f"\nClips guardados en: {output_dir.absolute()}")
            
            # Cerrar el video
            video.close()
            
        except FileNotFoundError as e:
            print(f"Error: {e}")
            continue
        except ValueError as e:
            print(f"Error: {e}")
            continue
        except Exception as e:
            print(f"Error inesperado: {e}")
            print("Intentando continuar con el siguiente video...")
            continue
        
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()