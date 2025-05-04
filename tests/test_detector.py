import unittest
from src.video_processor.detector import Detector

class TestDetector(unittest.TestCase):
    
    def setUp(self):
        self.detector = Detector()

    def test_detect_highlights(self):
        # Aquí se debe agregar un video de prueba y verificar que los momentos destacados se detecten correctamente
        test_video_path = "path/to/test/video.mp4"
        highlights = self.detector.detect_highlights(test_video_path)
        self.assertIsInstance(highlights, list)
        self.assertGreater(len(highlights), 0)

if __name__ == '__main__':
    unittest.main()