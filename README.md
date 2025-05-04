# video-clipper-ai

Este proyecto es una aplicación de recorte de videos que utiliza inteligencia artificial para identificar los mejores momentos para recortar. El programa permite recortar videos en segmentos de un minuto a un minuto y treinta segundos, facilitando la creación de clips atractivos y dinámicos.

## Estructura del Proyecto

- `src/`: Contiene el código fuente de la aplicación.
  - `main.py`: Punto de entrada de la aplicación.
  - `video_processor/`: Módulo para el procesamiento de videos.
    - `clipper.py`: Contiene la clase `Clipper` para recortar videos.
    - `detector.py`: Contiene la clase `Detector` para identificar momentos destacados.
  - `ai_models/`: Módulo para modelos de inteligencia artificial.
    - `highlight_detector.py`: Contiene la clase `HighlightDetector` para detectar momentos destacados.
  - `utils/`: Módulo con funciones utilitarias para el manejo de videos.
    - `video_utils.py`: Funciones para cargar y guardar archivos de video.

- `tests/`: Contiene pruebas unitarias para asegurar la funcionalidad del código.
  - `test_clipper.py`: Pruebas para la clase `Clipper`.
  - `test_detector.py`: Pruebas para la clase `Detector`.

- `requirements.txt`: Lista de dependencias necesarias para el proyecto.
- `setup.py`: Script de configuración para la instalación del paquete.
- `.gitignore`: Archivos y directorios que deben ser ignorados por Git.

## Instalación

1. Clona el repositorio:
   ```
   git clone <url-del-repositorio>
   ```

2. Navega al directorio del proyecto:
   ```
   cd video-clipper-ai
   ```

3. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

## Uso

Para ejecutar la aplicación, utiliza el siguiente comando:
```
python src/main.py
```

Asegúrate de tener los archivos de video en el formato adecuado y especifica la ruta de entrada y salida en el código según sea necesario.