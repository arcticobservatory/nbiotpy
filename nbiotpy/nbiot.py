import serial
import time
import re
import binascii
import timeout_decorator
from .atcommands import *


class NbIoT:

    def __init__(self, serial_port='/dev/ttyACM0', apn='telenor.iot', mccmnc=24201, socket_port=9000, debug=False):

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
        if self._debug:
            print(msg)

    def connect(self):
        self.reboot()
        self.__radio_on()
        self.__set_apn()
        self.__select_operator()
        self.__check_if_attached()
        self.__activate_pdp_context()
        self.__create_socket()

    def disconnect(self):
        self.__close_socket()

    def reboot(self):
        self.__log("### REBOOT ###")
        status, _ = self.__execute_cmd(REBOOT)
        self.__log("##############")

        return status

    def send_to(self, data, addr):
        self.__log("### SEND_TO ###")
        cmd = SOST.format(self.socket)
        # packet = {
        #     "thingName": self.config['thing']['name'],
        #     "auth": self.config['thing']['auth'],
        #     "data": data
        # }
        #
        # msg = json.dumps(packet)
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

    def read_urc(self):
        while True:
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

    def set_urc(self, n):
        self.__log("### SET URC ###")
        self._complex_cmd = SCONN.format(n)
        status, _ = self.__execute_cmd(SCONN)

    def get_connection_status(self):
        self.__log("### CONNECTION STATUS ###")
        status, _ = self.__execute_cmd(CONS)
        self.__log("##############")

    def get_imei(self):
        self.__log("### IMEI ###")
        if self.imei is None:
            status, self.imei = self.__execute_cmd(IMEI)
        self.__log("##############")

    def get_imsi(self):
        self.__log("### IMSI ###")
        if self.imsi is None:
            status, self.imsi = self.__execute_cmd(IMSI)
        self.__log("##############")

    def get_pdp_context(self):
        self.__log("### PDP CONTEXT")
        status, _ = self.__execute_cmd(CGDCR)
        self.__log("##############")

    def get_pdp_address(self):
        self.__log("### PDP CONTEXT")
        self._complex_cmd = CGPR.format("1")
        status, _ = self.__execute_cmd(CGPR)
        self.__log("##############")

    def __radio_on(self):
        self.__log("### RADIO ON ###")
        status, _ = self.__execute_cmd(RADIO_ON)
        self.__log("##############")

        return status

    def __radio_off(self):
        self.__log("### RADIO OFF ###")
        status, _ = self.__execute_cmd(RADIO_OFF)
        self.__log("##############")

        return status

    # SARA-N2_ATCommands manual, point 9.3 "Response time up to 3 min"
    @timeout_decorator.timeout(180)
    def __check_if_attached(self):
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
        self.__log("### CREATE_SOCKET ###")

        if self.socket < 0:
            self._complex_cmd = SOCR.format(self.port)
            status, self.socket = self.__execute_cmd(SOCR)
            self.socket = int(self.socket)

        self.__log("##############")

    def __close_socket(self):
        self.__log("### CLOSE_SOCKET ###")

        if self.socket >= 0:
            self._complex_cmd = SOCL.format(self.socket)
            status, _ = self.__execute_cmd(SOCL)

        self.socket = -1
        self.__log("##############")

    # def receive_from(self):
    #     self.__log("### RECEIVE ###")
    #     self._complex_cmd = SORF.format(self.socket, 200)
    #
    #     status, _ = self.__execute_cmd(SORF)
    #     self.__log("##############")

    def __set_apn(self):
        self.__log("### SET APN ###")
        self._complex_cmd = CGDCS.format("1,\"IP\",\"{}\"".format(self.apn))
        status, _ = self.__execute_cmd(CGDCS)
        self.__log("##############")

    def __activate_pdp_context(self):
        self.__log("### ACTIVATE PDP CONTEXT")
        self._complex_cmd = CGAC.format("{},{}".format(1, 1))
        status, _ = self.__execute_cmd(CGAC)
        self.__log("##############")

    def __select_operator(self):
        self.__log("### SELECT OPERATOR ###")
        self._complex_cmd = COPS.format("1,2,\"{}\"".format(self.mccmnc))
        status, _ = self.__execute_cmd(COPS)
        self.__log("##############")

    # def set_coap_server(self):
    #     self.__log("### SET COAP SERVER ###")
    #     self._complex_cmd = COAP.format("0,\"{}\"".format(self.config['server']['ip']))
    #     status, _ = self.__execute_cmd(COAP)
    #     self.__log("##############")
    #
    # def set_coap_uri(self):
    #     self.__log("### SET COAP URI ###")
    #     self._complex_cmd = COAP.format("1,\"coap://{}:5683/time\"".format(self.config['server']['ip']))
    #     status, _ = self.__execute_cmd(COAP)
    #     self.__log("##############")
    #
    # def set_current_coap_profile(self):
    #     self.__log("### SET COAP PROFILE NUMBER ###")
    #     self._complex_cmd = COAP.format("3,\"0\"")
    #     status, _ = self.__execute_cmd(COAP)
    #     self.__log("##############")
    #
    # def set_coap_profile_valid_flag(self):
    #     self.__log("### SET COAP PROFILE VALID FLAG ###")
    #     self._complex_cmd = COAP.format("4,\"0\"")
    #     status, _ = self.__execute_cmd(COAP)
    #     self.__log("##############")
    #
    # def save_coap_profile(self):
    #     self.__log("### SAVE COAP PROFILE ###")
    #     self._complex_cmd = COAP.format("6,\"0\"")
    #     status, _ = self.__execute_cmd(COAP)
    #     self.__log("##############")
    #
    # def do_ucoapc(self):
    #     self.__log("### DO COAPC ###")
    #     self._complex_cmd = COAPC.format("1")
    #     status, _ = self.__execute_cmd(COAP)
    #     self.__log("--> Waiting for URC")
    #
    #     while True:
    #         x = self.serial.readline()
    #
    #         try:
    #             x = x.decode()
    #         except UnicodeDecodeError as e:
    #             continue
    #
    #         x = x.replace('\r', '').replace('\n', '')
    #
    #         if len(x) == 0:
    #             time.sleep(0.1)
    #             continue
    #
    #         self.__log("<-- %s" % x)
    #         break
    #
    #     self.__log("##############")

    def __execute_cmd(self, cmd):
        self._cmd = cmd
        self.__send_cmd()
        status, expected_value = self.__read_response()

        return status, expected_value

    def __send_cmd(self):
        full_cmd = None
        if not self._complex_cmd:
            full_cmd = "%s%s%s" % (PREFIX, self._cmd, POSTFIX)

        if self._complex_cmd:
            full_cmd = "%s%s%s" % (PREFIX, self._complex_cmd, POSTFIX)
            self._complex_cmd = None

        self.__log("---> %s" % full_cmd)
        self.serial.write(full_cmd.encode())

    def __read_response(self):
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

                    # if self._debug:
                    #     self.__log("[DEBUG] Found expected pattern: %s" % expected_line)

            if x.find(last_line) >= 0:
                # if self._debug:
                #     self.__log("[DEBUG] Found last line: %s vs %s" % (x, last_line))
                last_line_found = True

        return status, expected_line
