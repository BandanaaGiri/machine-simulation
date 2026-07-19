from machine import Machine


class MachineController:

    def __init__(self):
        self.machine = Machine()

    def start_machine(self):
        # Prevent starting if tripped or still critically overheated
        if not self.machine.error and self.machine.temperature < 75.0:
            self.machine.start()

    def stop_machine(self):
        self.machine.stop()

    def change_speed(self, speed):
        self.machine.set_speed(speed)

    def reset_fault(self):
        self.machine.error = None

    def update_machine(self):
        # Advance simulation physics regardless of running or cooling state
        self.machine.update_conditions()

        status = self.machine.get_status()

        if status["temperature"] >= 80.0 and self.machine.running:
            self.machine.stop()
            self.machine.error = "EMERGENCY STOP: OVERHEATING"

    def get_machine_status(self):
        return self.machine.get_status()