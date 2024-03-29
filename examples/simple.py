# Copyright (C) 2018  Distributed Arctic Observatory
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Example of simple udp text message send to the remote server using NB-IoT

from nbiotpy import NbIoT
import socket

PORT = 0  # Remote server port
addr = ('REMOTE_SERVER_IP', PORT)
hostname = socket.gethostname()

nb = NbIoT(debug=True)
nb.connect()
nb.send_to("[{}]: hello!".format(hostname), addr)
nb.disconnect()
