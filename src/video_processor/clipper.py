class Clipper:
    def __init__(self, video_path):
        self.video_path = video_path

    def clip(self, start_time, end_time):
        if start_time < 0 or end_time <= start_time:
            raise ValueError("Invalid start or end time for clipping.")
        # Aquí se implementaría la lógica para recortar el video
        # utilizando una biblioteca de procesamiento de video.
        pass

    def clip_one_minute_segments(self):
        # Lógica para recortar segmentos de un minuto a un minuto y treinta segundos
        start_time = 0
        while True:
            end_time = start_time + 90  # 90 segundos para el recorte
            self.clip(start_time, end_time)
            start_time += 60  # Avanzar un minuto
            # Aquí se podría agregar una condición para detener el recorte
            # si se alcanza el final del video.