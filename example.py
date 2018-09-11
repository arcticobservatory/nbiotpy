from nbiot import NbIoT

nb = NbIoT()
nb.connect()
nb.create_socket()
nb.send_to("RPi hello!")
nb.send_to("Message2")
nb.send_to("Message3")
nb.close_socket()
nb.disconnect()
