from controller import MachineController

controller = MachineController()

controller.start_machine()
controller.change_speed(3000)

print("Machine started at 3000 RPM")

for i in range(40):

    controller.update_machine()

    status = controller.get_machine_status()

    print(
        f"Temperature: {status['temperature']}°C | "
        f"RPM: {status['speed']} | "
        f"Running: {status['running']} | "
        f"Error: {status['error']}"
    )

    if status["error"]:
        break