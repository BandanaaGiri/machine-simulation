from controller import MachineController

controller = MachineController()

print("Initial status:")
print(controller.get_machine_status())

print("\nStarting machine...")
controller.start_machine()
print(controller.get_machine_status())

print("\nChanging speed to 2000 RPM...")
controller.change_speed(2000)
print(controller.get_machine_status())

print("\nStopping machine...")
controller.stop_machine()
print(controller.get_machine_status())