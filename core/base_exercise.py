from abc import ABC, abstractmethod
import math

class BaseExercise(ABC):

    def __init__(self):
        self.reps = 0
        self.stage = None

    def calculate_angle(self, a, b, c):
        ax, ay = a[0] - b[0], a[1] - b[1]
        cx, cy = c[0] - b[0], c[1] - b[1]

        dot = ax * cx + ay * cy

        magnitude_a = math.sqrt(ax ** 2 + ay ** 2)
        magnitude_c = math.sqrt(cx ** 2 + cy ** 2)

        magnitude = magnitude_a * magnitude_c

        if magnitude == 0:
            return 0.0
        
        cos_angle = max(-1.0, min(1.0, dot / magnitude))

        return math.degrees(math.acos(cos_angle))

    def get_point(self, landmarks, idx):
        p = landmarks[idx]

        return (p.x, p.y)

    @abstractmethod
    def process(self, landmarks):
        pass

    @abstractmethod
    def reset(self):
        pass