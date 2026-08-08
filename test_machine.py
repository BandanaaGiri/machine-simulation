from machine import Machine

machine = Machine()

print(machine.get_status())

machine.start()

print(machine.get_status())

machine.set_speed(2000)

print(machine.get_status())

machine.stop()

print(machine.get_status())