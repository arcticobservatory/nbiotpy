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

# Example of file sending using NB-IoT

from nbiotpy import NbIoT
import binascii
import hashlib
import argparse
import os.path

START_MSG = "0#{}#{}#{}"


def send_file(path, part_size, addr):
    nb = NbIoT()
    nb.connect()

    path_parts = path.split('/')
    file_name = path_parts.pop()

    with open(path, 'rb') as f:
        data = f.read()
        hexified_data = binascii.hexlify(data).decode()
        sha256 = hashlib.sha256(data)
        checksum = sha256.hexdigest()
        data_len = len(hexified_data)

        if data_len > part_size:
            parts = [data[i:i + part_size] for i in range(0, len(data), part_size)]
            start_msg = START_MSG.format(file_name, len(parts), checksum)
            nb.send_to(start_msg, addr)
            counter = 1
            for part in parts:
                msg = "{}#{}".format(counter, binascii.hexlify(part).decode())
                nb.send_to(msg, addr)
                counter += 1
        else:
            start_msg = START_MSG.format(file_name, 1, checksum)
            nb.send_to(start_msg, addr)

    nb.disconnect()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sends file using NB-IoT')
    parser.add_argument('path', help='Absolute path of the file to send')
    parser.add_argument('server_ip', help='Remote server IP')
    parser.add_argument('server_port', help='Remote server port')
    parser.add_argument('-s', '--size', help='Number of bytes per single packet. Max allowed is 400 bytes.', type=int,
                        default=200)
    args = parser.parse_args()

    if os.path.isfile(args.path) is not True:
        raise FileNotFoundError("Given file does not exist: {}".format(args.path))

    if args.size > 400:
        raise ValueError('Single packet size could not be bigger than 400 bytes!')

    send_file(args.path, args.size, (args.server_ip, args.server_port))
