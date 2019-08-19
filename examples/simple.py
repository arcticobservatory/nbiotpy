from nbiotpy import NbIoT
import socket

addr = ('178.74.39.219', 31415)
hostname = socket.gethostname()

nb = NbIoT(debug=True)
nb.connect()
nb.send_to("[{}]: RPi hello!".format(hostname), addr)
nb.disconnect()
