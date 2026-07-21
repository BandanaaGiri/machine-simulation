import random


class Machine:

    AMBIENT_TEMP = 25.0
    AMBIENT_PRESSURE = 1.0

    def __init__(self):
        self.running = False
        self.speed = 0
        self.temperature = self.AMBIENT_TEMP
        self.pressure = self.AMBIENT_PRESSURE
        self.error = None

    def start(self):
        self.running = True
        self.speed = 1000
        self.error = None

    def stop(self):
        self.running = False
        self.speed = 0

    def set_speed(self, speed):
        if 0 <= speed <= 3000:
            self.speed = speed
        else:
            raise ValueError("Speed must be between 0 and 3000 RPM")

    def update_conditions(self):
        if self.running and self.speed > 0:
            # Heat generation proportional to speed
            temperature_increase = (self.speed / 1000.0) * 0.5
            self.temperature += temperature_increase

            # Running pressure fluctuations
            self.pressure += random.uniform(-0.05, 0.05)
            self.pressure = max(0.5, min(self.pressure, 5.0))

            # Detect overheating trip
            if self.temperature >= 80.0:
                self.error = "OVERHEATING"
                self.running = False
                self.speed = 0

        else:
            # Passive cooldown to ambient (25.0 °C)
            if self.temperature > self.AMBIENT_TEMP:
                self.temperature = max(self.AMBIENT_TEMP, round(self.temperature - 2.0, 2))

            # Normalize pressure to atmospheric (1.0 bar)
            if self.pressure > self.AMBIENT_PRESSURE:
                self.pressure = max(self.AMBIENT_PRESSURE, round(self.pressure - 0.05, 2))
            elif self.pressure < self.AMBIENT_PRESSURE:
                self.pressure = min(self.AMBIENT_PRESSURE, round(self.pressure + 0.05, 2))

    def get_status(self):
        return {
            "running": self.running,
            "speed": self.speed,
            "temperature": round(self.temperature, 2),
            "pressure": round(self.pressure, 2),
            "error": self.error
        }