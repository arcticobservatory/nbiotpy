from nbiot import NbIoT

nb = NbIoT()
nb.connect()
nb.create_socket()
nb.send_to("RPi hello!")
nb.close_socket()
nb.disconnect()
