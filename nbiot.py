import json
import serial
import time
import re
import binascii
import timeout_decorator
import atcommands as AT


class NbIoT:

    def __init__(self, config_file='config.json', debug=False):
        with open(config_file) as f:
            self.config = json.load(f)

        self.serial = serial.Serial(
            self.config['serial']['port'],
            baudrate=self.config['serial']['baudrate'],
            timeout=self.config['serial']['timeout']
        )

        self.socket = -1
        self.imei = None
        self.imsi = None

        self._cmd = None
        self._complex_cmd = None
        self._debug = debug

    def connect(self):
        self.reboot()
        self.radio_on()
        self.set_apn()
        self.select_operator()
        self.check_if_attached()
        self.activate_pdp_context()

    def disconnect(self):
        self.radio_off()

    def reboot(self):
        print("### REBOOT ###")
        status, _ = self.__execute_cmd(AT.REBOOT)
        print("##############")

        return status

    def radio_on(self):
        print("### RADIO ON ###")
        status, _ = self.__execute_cmd(AT.RADIO_ON)
        print("##############")

        return status

    def radio_off(self):
        print("### RADIO OFF ###")
        status, _ = self.__execute_cmd(AT.RADIO_OFF)
        print("##############")

        return status

    # SARA-N2_ATCommands manual, point 9.3 "Response time up to 3 min"
    @timeout_decorator.timeout(180)
    def check_if_attached(self):
        print("### CHECK IF ATTACHED (up to 180s) ###")
        online = False

        while not online:
            status, cgatt = self.__execute_cmd(AT.GPRS)

            if status:
                online = bool(int(cgatt))
                if self._debug:
                    print("[DEBUG] Online: %r" % online)

            if not online:
                time.sleep(5)

        print("##############")

    def create_socket(self):
        print("### CREATE_SOCKET ###")

        if self.socket < 0:
            self._complex_cmd = AT.SOCR.format(self.config['thing']['port'])
            status, self.socket = self.__execute_cmd(AT.SOCR)
            self.socket = int(self.socket)

        print("##############")

    def close_socket(self):
        print("### CLOSE_SOCKET ###")

        if self.socket >= 0:
            self._complex_cmd = AT.SOCL.format(self.socket)
            status, _ = self.__execute_cmd(AT.SOCL)

        self.socket = -1
        print("##############")

    def send_to(self, data):
        print("### SEND_TO ###")
        cmd = AT.SOST.format(self.socket)
        packet = {
            "thingName": self.config['thing']['name'],
            "auth": self.config['thing']['auth'],
            "data": data
        }

        msg = json.dumps(packet)
        msg_len = len(msg)

        # AT+NSOST=<socket>,<remote_ip_address>,<remote_port>,<length>,<data>
        # AT+NSOST=1,"192.158.5.1",1024,2,"07FF"
        self._complex_cmd = "{},\"{}\",{},{},\"{}\"".format(
            cmd,
            self.config['server']['ip'],
            self.config['server']['port'],
            msg_len,
            binascii.hexlify(msg.encode()).decode()
        )

        status, _ = self.__execute_cmd(AT.SOST)
        print("##############")

    def receive_from(self):
        print("### RECEIVE ###")
        self._complex_cmd = AT.SORF.format(self.socket, 200)

        status, _ = self.__execute_cmd(AT.SORF)
        print("##############")

    def get_connection_status(self):
        print("### CONNECTION STATUS ###")
        status, _ = self.__execute_cmd(AT.CONS)
        print("##############")

    def set_urc(self, n):
        print("### SET URC ###")
        self._complex_cmd = AT.SCONN.format(n)
        status, _ = self.__execute_cmd(AT.SCONN)

    def get_imei(self):
        print("### IMEI ###")
        if self.imei is None:
            status, self.imei = self.__execute_cmd(AT.IMEI)
        print("##############")

    def get_imsi(self):
        print("### IMSI ###")
        if self.imsi is None:
            status, self.imsi = self.__execute_cmd(AT.IMSI)
        print("##############")

    def set_apn(self):
        print("### SET APN ###")
        self._complex_cmd = AT.CGDCS.format("1,\"IP\",\"{}\"".format(self.config['mno']['apn']))
        status, _ = self.__execute_cmd(AT.CGDCS)
        print("##############")

    def activate_pdp_context(self):
        print("### ACTIVATE PDP CONTEXT")
        self._complex_cmd = AT.CGAC.format("{},{}".format(1, 1))
        status, _ = self.__execute_cmd(AT.CGAC)
        print("##############")

    def get_pdp_context(self):
        print("### PDP CONTEXT")
        status, _ = self.__execute_cmd(AT.CGDCR)
        print("##############")

    def get_pdp_address(self):
        print("### PDP CONTEXT")
        self._complex_cmd = AT.CGPR.format("1")
        status, _ = self.__execute_cmd(AT.CGPR)
        print("##############")

    def select_operator(self):
        print("### SELECT OPERATOR ###")
        self._complex_cmd = AT.COPS.format("1,2,\"{}\"".format(self.config['mno']['mcc_mnc']))
        status, _ = self.__execute_cmd(AT.COPS)
        print("##############")

    def __execute_cmd(self, cmd):
        self._cmd = cmd
        self.__send_cmd()
        status, expected_value = self.__read_response()

        return status, expected_value

    def __send_cmd(self):
        full_cmd = None
        if not self._complex_cmd:
            full_cmd = "%s%s%s" % (AT.PREFIX, self._cmd, AT.POSTFIX)

        if self._complex_cmd:
            full_cmd = "%s%s%s" % (AT.PREFIX, self._complex_cmd, AT.POSTFIX)
            self._complex_cmd = None

        print("---> %s" % full_cmd)
        self.serial.write(full_cmd.encode())

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

            print("<-- %s" % x)

    def __read_response(self):
        last_line, expected_pattern = AT.RESPONSE[self._cmd]
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

            print("<-- %s" % x)

            if x == AT.R_OK:
                status = True

            if x == AT.R_ERROR:
                status = False
                break

            if expected_line is None and expected_pattern is not None:
                search = pattern.findall(x)

                if len(search) > 0:
                    expected_line = search[0]

                    if self._debug:
                        print("[DEBUG] Found expected pattern: %s" % expected_line)

            if x.find(last_line) >= 0:
                if self._debug:
                    print("[DEBUG] Found last line: %s vs %s" % (x, last_line))
                last_line_found = True

        return status, expected_line
