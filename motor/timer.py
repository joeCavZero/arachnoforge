class Timer:
    def __init__(self):
        self.time: float = 0.0
    
    def update(self, delta_time: float):
        if self.time > 0:
            self.time -= delta_time
    def restart(self, time: float):
        self.time = time
    def is_finished(self) -> bool:
        return self.time <= 0