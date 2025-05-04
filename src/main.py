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

def process_clip(clip_info, detector):
    """Procesa un clip individual"""
    i, (start_time, end_time), video_path, output_dir = clip_info
    try:
        tiempo_inicio = time.time()
        video = VideoFileClip(video_path)
        
        tiempo_recorte = time.time()
        clip = video.subclip(start_time, end_time)
        detector.stats['tiempos_recorte'].append(time.time() - tiempo_recorte)
        
        output_path = output_dir / f"highlight_{i}.mp4"
        
        tiempo_export = time.time()
        clip.write_videofile(
            str(output_path),
            codec='libx264',
            audio_codec='aac',
            temp_audiofile=f'temp-audio_{i}.m4a',
            remove_temp=True,
            logger=None,
            preset='veryslow',  # Mejor calidad
            bitrate='8000k'     # Alta tasa de bits
        )
        detector.stats['tiempos_exportacion'].append(time.time() - tiempo_export)
        
        video.close()
        return i, True, output_path, time.time() - tiempo_inicio
        
    except Exception as e:
        return i, False, str(e), 0

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
            tiempo_inicio_analisis = time.time()
            total_frames = int(video.fps * video.duration)
            
            with tqdm(total=total_frames, desc="Progreso") as pbar:
                def update_progress():
                    tiempo_actual = time.time() - tiempo_inicio_analisis
                    pbar.set_postfix({
                        'Tiempo': format_time(tiempo_actual),
                        'Frames/s': f"{pbar.n / tiempo_actual:.1f}" if tiempo_actual > 0 else "0.0"
                    })
                    pbar.update(1)
                
                highlights, tiempo_total = detector.detect_highlights(video, progress_callback=update_progress)
            
            print(f"\nAnálisis completado en {format_time(tiempo_total)}")
            print(f"Velocidad promedio: {total_frames / tiempo_total:.1f} frames/s")
            
            if not highlights:
                print("No se encontraron clips que cumplan con los criterios.")
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
                
                if i == 1 or input(f"\n¿Desea procesar el clip {i}? (s/n): ").lower() == 's':
                    clip_info = (i, (start_time, end_time), video_path, output_dir)
                    success, result = process_clip(clip_info, detector)
                    
                    if success:
                        print(f"✓ Clip {i} guardado en: {result}")
                    else:
                        print(f"✗ Error al procesar clip {i}: {result}")
                else:
                    print(f"Clip {i} saltado.")
            
            # Mostrar estadísticas
            stats = detector.get_stats_summary()
            if isinstance(stats, dict):
                print("\n=== Estadísticas de Procesamiento ===")
                print(f"Análisis por frame: {stats['analisis_promedio']:.3f} segundos")
                print(f"Recorte promedio: {stats['recorte_promedio']:.3f} segundos")
                print(f"Exportación promedio: {stats['exportacion_promedio']:.3f} segundos")
            
            tiempo_total = time.time() - tiempo_inicio
            print("\n✓ Proceso completado:")
            print(f"└─ Tiempo de análisis: {format_time(tiempo_total)}")
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