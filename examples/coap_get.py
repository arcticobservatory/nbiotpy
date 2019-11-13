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

# Example of simple CoAP operation
# Required additional testing

from nbiotpy import NbIoT
import socket

addr = ('COAP_SERVER_ADDRESS', 5683)
hostname = socket.gethostname()

nb = NbIoT(debug=True)
nb.connect()
nb.set_coap_server(addr)
nb.set_coap_uri('/time')
nb.set_coap_pdu()
nb.set_current_coap_profile()
nb.set_coap_profile_valid_flag()
nb.save_coap_profile()
nb.restore_and_use_coap_profile()
nb.select_coap_at()
nb.do_ucoapc()
nb.disconnect()
