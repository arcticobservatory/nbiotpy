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

import serial
import time
import re
import binascii
import timeout_decorator
from timeit import default_timer as timer
from .atcommands import *


class NbIoT:
    """Class responsible for interaction with SARA-N210 modem

    :ivar serial.Serial serial: pyserial object for communication with the modem
    :ivar int socket: socket number returned by the network operator
    :ivar int imei: International Mobile Equipment Identity
    :ivar int imsi: International Mobile Subscriber Identity)
    :ivar int mccmnc: Mobile Country Code and Mobile Network Code
    :ivar str apn: Access Point Name
    :ivar int port: Port number to create the socket
    :ivar str _cmd: Stores simple AT command that will be send via serial to the modem
    :ivar str _complex_cmd: Stores complex AT command (usually with input parameters) that will be send via serial to the modem
    :ivar bool _debug: Indicates whether to display debug messages from the class or not
    """

    def __init__(self, serial_port='/dev/ttyACM0', apn='telenor.iot', mccmnc=24201, socket_port=9000, debug=False):
        """
        :param serial.Serial serial_port:
        :param str apn:
        :param int mccmnc:
        :param int socket_port:
        :param bool debug:
        """

        self.serial = serial.Serial(serial_port, 9600, 5.0)
        self.socket = -1
        self.imei = None
        self.imsi = None
        # Mobile Country Code and Mobile Network Code
        self.mccmnc = mccmnc
        self.apn = apn
        self.port = socket_port

        self._cmd = None
        self._complex_cmd = None
        self._debug = debug

    def __log(self, msg):
        """If self._debug sets to True prints msg

        :param object msg: message to print
        """
        if self._debug:
            print(msg)

    def connect(self):
        """Connects modem to the network operator

        Performs the following steps to get modem connected to the operator:
        * reboots the modem to have errors free state
        * changes the status of modem radio to enabled
        * sets the operator mccmnc data
        * activates the operator APN
        * creates socket at the operators side

        """
        self.reboot()
        self.__radio_on()
        self.__set_apn()
        self.__select_operator()
        self.__check_if_attached()
        self.__activate_pdp_context()
        self.__create_socket()

    def disconnect(self):
        """Closes socket at the operator side
        """
        self.__close_socket()

    def reboot(self):
        """Sends command to reboot the modem

        :return: operation status
        :rtype: bool
        """
        self.__log("### REBOOT ###")
        status, _ = self.__execute_cmd(REBOOT)
        self.__log("##############")

        return status

    def ping(self, addr, timeout=30):
        """Pings specific pair of ip_address and port

        :param (str, int) addr: address with port to ping
        :param int timeout: timeout for urc
        :return: operation status
        :rtype bool
        """
        self.__log("### PING ###")
        ping_status = False
        self.set_urc(1)
        self._complex_cmd = NPING.format(addr)
        status, _ = self.__execute_cmd(NPING)
        urc = self.read_urc(timeout)
        self.set_urc(0)

        pattern = re.compile("+NPING:\s\d?(.*),(\d+),(\d+)")
        for x in urc:
            search = pattern.findall(x)

            if len(search) >= 2:
                ping_status = True
                self.__log(search)

        self.__log("##############")
        return ping_status

    def send_to(self, data, addr):
        """Sends string data to a specific address

        :param str data: data to send
        :param (str, int) addr: (ip_address, port)
        :return: operation status
        :rtype: bool
        """
        self.__log("### SEND_TO ###")
        cmd = SOST.format(self.socket)
        msg_len = len(data)

        # AT+NSOST=<socket>,<remote_ip_address>,<remote_port>,<length>,<data>
        # AT+NSOST=1,"192.158.5.1",1024,2,"07FF"
        self._complex_cmd = "{},\"{}\",{},{},\"{}\"".format(
            cmd,
            addr[0],
            addr[1],
            msg_len,
            binascii.hexlify(data.encode()).decode('utf-8')
        )

        status, _ = self.__execute_cmd(SOST)
        self.__log("##############")

        return status

    def read_urc(self, timeout):
        """For a given timeout collects all unsolicited response codes

        :param int timeout: timeout for urc
        :return: all urcs collected during the given time period
        :rtype: list(str)
        """
        start = timer()
        urc = []
        while True:
            x = self.serial.readline()
            try:
                x = x.decode()
            except UnicodeDecodeError as e:
                continue

            x = x.replace('\r', '').replace('\n', '')

            if len(x) > 0:
                urc.append(x)
                self.__log("<-- %s" % x)

            now = timer()
            if (now - start) >= timeout:
                return urc

            time.sleep(0.1)

    def set_urc(self, n):
        """Enables/Disabled URC mode

        :param int n: 0 to disable, 1 to enable
        :return: operation status
        :rtype: bool
        """
        self.__log("### SET URC ###")
        self._complex_cmd = SCONN.format(n)
        status, _ = self.__execute_cmd(SCONN)

        return status

    def get_connection_status(self):
        """Returns connection status

        :return: operation status
        :rtype: bool

        .. todo:: extract status from the modem response
        """
        self.__log("### CONNECTION STATUS ###")
        status, _ = self.__execute_cmd(CONS)
        self.__log("##############")

        return status

    def get_imei(self):
        """Gets IMEI from modem and sets corresponding class member

        :return: operation status
        :rtype: bool
        """
        self.__log("### IMEI ###")
        status = True
        if self.imei is None:
            status, self.imei = self.__execute_cmd(IMEI)
        self.__log("##############")

        return status

    def get_imsi(self):
        """Gets IMSI from modem and sets corresponding class member

        :return: operation status
        :rtype: bool
        """
        self.__log("### IMSI ###")
        status = True
        if self.imsi is None:
            status, self.imsi = self.__execute_cmd(IMSI)
        self.__log("##############")

        return status

    def get_pdp_context(self):
        """Gets current PDP context definition

        :return: operation status
        :rtype: bool

        .. todo:: extract PDP context from the modem response
        """
        self.__log("### PDP CONTEXT")
        status, _ = self.__execute_cmd(CGDCR)
        self.__log("##############")

        return status

    def get_pdp_address(self):
        """Gets current PDP address

        :return: operation status
        :rtype: bool

        .. todo:: extract PDP address from the modem response
        """
        self.__log("### PDP CONTEXT")
        self._complex_cmd = CGPR.format("1")
        status, _ = self.__execute_cmd(CGPR)
        self.__log("##############")

        return status

    def __radio_on(self):
        """Enables modem radio

        :return: operation status
        :rtype: bool
        """
        self.__log("### RADIO ON ###")
        status, _ = self.__execute_cmd(RADIO_ON)
        self.__log("##############")

        return status

    def __radio_off(self):
        """Disables modem radio

        :return: operation status
        :rtype: bool
        """
        self.__log("### RADIO OFF ###")
        status, _ = self.__execute_cmd(RADIO_OFF)
        self.__log("##############")

        return status

    @timeout_decorator.timeout(180)
    def __check_if_attached(self):
        """Waits up to 3 minutes for modem to get attached to the network

        .. seealso:: SARA-N2_ATCommands manual, point 9.3 "Response time up to 3 min"
        """
        self.__log("### CHECK IF ATTACHED (up to 180s) ###")
        online = False

        while not online:
            status, cgatt = self.__execute_cmd(GPRS)

            if status:
                online = bool(int(cgatt))

            if not online:
                time.sleep(5)

        self.__log("##############")

    def __create_socket(self):
        """Creates remote socket and sets class member to the returned value

        :return: operation status
        :rtype: bool
        """
        self.__log("### CREATE_SOCKET ###")
        status = True
        if self.socket < 0:
            self._complex_cmd = SOCR.format(self.port)
            status, self.socket = self.__execute_cmd(SOCR)
            self.socket = int(self.socket)

        self.__log("##############")

        return status

    def __close_socket(self):
        """Closes remote socket

        :return: operation status
        :rtype: bool
        """
        self.__log("### CLOSE_SOCKET ###")

        status = True
        if self.socket >= 0:
            self._complex_cmd = SOCL.format(self.socket)
            status, _ = self.__execute_cmd(SOCL)

        self.socket = -1
        self.__log("##############")

        return status

    # def receive_from(self):
    #     self.__log("### RECEIVE ###")
    #     self._complex_cmd = SORF.format(self.socket, 200)
    #
    #     status, _ = self.__execute_cmd(SORF)
    #     self.__log("##############")

    def __set_apn(self):
        """Sets APN

        :return: operation status
        :rtype: bool
        """
        self.__log("### SET APN ###")
        self._complex_cmd = CGDCS.format("1,\"IP\",\"{}\"".format(self.apn))
        status, _ = self.__execute_cmd(CGDCS)
        self.__log("##############")

        return status

    def __activate_pdp_context(self):
        """Activated selected PDP context

        :return: operation status
        :rtype: bool
        """
        self.__log("### ACTIVATE PDP CONTEXT")
        self._complex_cmd = CGAC.format("{},{}".format(1, 1))
        status, _ = self.__execute_cmd(CGAC)
        self.__log("##############")

        return status

    def __select_operator(self):
        """Sets operators MCCMNC code

        :return: operation status
        :rtype: bool
        """
        self.__log("### SELECT OPERATOR ###")
        self._complex_cmd = COPS.format("1,2,\"{}\"".format(self.mccmnc))
        status, _ = self.__execute_cmd(COPS)
        self.__log("##############")

        return status

    def set_coap_server(self, addr):
        """Sets CoAP server for CoAP protocol

        :return: operation status
        :rtype: bool
        """
        self.__log("### SET COAP SERVER ###")
        self._complex_cmd = COAP.format("0,\"{}\",\"{}\"".format(addr[0], addr[1]))
        status, _ = self.__execute_cmd(COAP)
        self.__log("##############")

        return status

    def set_coap_uri(self, uri):
        """Sets uri for CoAp operation

        :return: operation status
        :rtype: bool
        """
        self.__log("### SELECT OPERATOR ###")
        self._complex_cmd = COPS.format("1,2,\"{}\"".format(self.mccmnc))
        status, _ = self.__execute_cmd(COPS)
        self.__log("##############")

        return status
        self.__log("### SET COAP URI ###")
        self._complex_cmd = COAP.format("1,\"{}\"".format(uri))
        status, _ = self.__execute_cmd(COAP)
        self.__log("##############")

        return status

    def set_coap_pdu(self):
        """Sets CoAP PDU

        """
        self.__log("### SET COAP PDU ###")
        self._complex_cmd = COAP.format("2,\"4\",\"1\"")
        status, _ = self.__execute_cmd(COAP)
        self._complex_cmd = COAP.format("2,\"0\",\"1\"")
        status, _ = self.__execute_cmd(COAP)
        self._complex_cmd = COAP.format("2,\"1\",\"1\"")
        status, _ = self.__execute_cmd(COAP)
        self._complex_cmd = COAP.format("2,\"2\",\"1\"")
        status, _ = self.__execute_cmd(COAP)
        self.__log("##############")

    def set_current_coap_profile(self):
        """Sets CoAP profile

        :return: operation status
        :rtype: bool
        """
        self.__log("### SET COAP PROFILE NUMBER ###")
        self._complex_cmd = COAP.format("3,\"0\"")
        status, _ = self.__execute_cmd(COAP)
        self.__log("##############")

        return status

    def set_coap_profile_valid_flag(self):
        """Sets CoAP profile validity flag

        :return: operation status
        :rtype: bool
        """
        self.__log("### SET COAP PROFILE VALID FLAG ###")
        self._complex_cmd = COAP.format("4,\"1\"")
        status, _ = self.__execute_cmd(COAP)
        self.__log("##############")

        return status

    def save_coap_profile(self):
        """Sets CoAP profile

        :return: operation status
        :rtype: bool
        """
        self.__log("### SAVE COAP PROFILE ###")
        self._complex_cmd = COAP.format("6,\"0\"")
        status, _ = self.__execute_cmd(COAP)
        self.__log("##############")

        return status

    def restore_and_use_coap_profile(self):
        """Restore previously stored CoAP profile

        :return: operation status
        :rtype: bool
        """
        self.__log("### RESTORE AND USE COAP PROFILE ###")
        self._complex_cmd = COAP.format("7,\"0\"")
        status, _ = self.__execute_cmd(COAP)
        self.__log("##############")

        return status

    def select_coap_at(self):
        """Selects CoAP component for AT use

        :return: operation status
        :rtype: bool
        """
        self.__log("### SELECT COAP COMPONENT FOR AT USE ###")
        status, _ = self.__execute_cmd(USELCP)
        self.__log("##############")

        return status

    def do_ucoapc(self, timeout=60):
        """Triggers the CoAP action

        :return: status of the operation and all urcs collected during the given time period
        :rtype: (bool, list(str))
        """
        self.__log("### DO COAPC ###")
        self.set_urc(1)
        self._complex_cmd = COAPC.format("1")
        status, _ = self.__execute_cmd(COAPC)
        self.__log("--> Waiting for URC")
        urc = self.read_urc(timeout)
        self.set_urc(0)
        self.__log("##############")

        return status, urc

    def __execute_cmd(self, cmd):
        """Executes simple command that do not require any additional input

        :return: operation status and expected_value if defined in atcommand.py
        :rtype: (bool, object)
        """
        self._cmd = cmd
        self.__send_cmd()
        status, expected_value = self.__read_response()

        return status, expected_value

    def __send_cmd(self):
        """Serial communication with the modem

        """
        full_cmd = None
        if not self._complex_cmd:
            full_cmd = "%s%s%s" % (PREFIX, self._cmd, POSTFIX)

        if self._complex_cmd:
            full_cmd = "%s%s%s" % (PREFIX, self._complex_cmd, POSTFIX)
            self._complex_cmd = None

        self.__log("---> %s" % full_cmd)
        self.serial.write(full_cmd.encode())

    def __read_response(self):
        """Reads serial response from the modem

        :return: operation status and expected_value if defined in atcommand.py
        :rtype: (bool, object)
        """
        last_line, expected_pattern = RESPONSE[self._cmd]
        expected_line = None
        last_line_found = False
        status = False
        pattern = None

        if expected_pattern is not None:
            pattern = re.compile(expected_pattern)

        while not last_line_found:
            x = self.serial.readline()

            try:
                x = x.decode()
            except UnicodeDecodeError as e:
                continue

            x = x.replace('\r', '').replace('\n', '')

            if len(x) == 0:
                time.sleep(0.1)
                continue

            self.__log("<-- %s" % x)

            if x == R_OK:
                status = True

            if x == R_ERROR:
                status = False
                break

            if expected_line is None and expected_pattern is not None:
                search = pattern.findall(x)

                if len(search) > 0:
                    expected_line = search[0]

                    if self._debug:
                        self.__log("[DEBUG] Found expected pattern: %s" % expected_line)

            if x.find(last_line) >= 0:
                if self._debug:
                    self.__log("[DEBUG] Found last line: %s vs %s" % (x, last_line))
                last_line_found = True

        return status, expected_line
