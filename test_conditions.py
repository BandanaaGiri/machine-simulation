from machine import Machine

machine = Machine()

machine.start()
machine.set_speed(2000)

print("Machine started!")

for i in range(10):
    machine.update_conditions()

    status = machine.get_status()

    print(
        f"Temperature: {status['temperature']}°C | "
        f"Pressure: {status['pressure']} bar | "
        f"RPM: {status['speed']} | "
        f"Error: {status['error']}"
    )