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

"""
Subset of SARA-N210 AT commands used in the implementation

.. seealso:: SARA-N2_ATCommands manual (https://www.u-blox.com/sites/default/files/SARA-N2_ATCommands_%28UBX-16014887%29.pdf)
"""

PREFIX = "AT+"
POSTFIX = "\r\n"

RADIO_ON = "CFUN=1"
RADIO_OFF = "c"
REBOOT = "NRB"
GPRS = "CGATT?"
CGAC = "CGACT={}"
SOCR = "NSOCR=\"DGRAM\",17,{},1"
SOCL = "NSOCL={}"
IMEI = "CGSN=1"
IMSI = "CIMI"
SOST = "NSOST={}"
SORF = "NSORF={},{}"
CONS = "CSCON?"
SCONN = "CSCON={}"
CGDCS = "CGDCONT={}"
CGDCR = "CGDCONT?"
COPS = "COPS={}"
CGPR = "CGPADDR={}"
COAP = "UCOAP={}"
COAPC = "UCOAPC={}"
NPING = "NPING=\"{}\""
USELCP = "USELCP=1"

MSG_TYPE = "1"

R_OK = "OK"
R_ERROR = "ERROR"

RESPONSE = {
    RADIO_ON: (R_OK, None),
    RADIO_OFF: (R_OK, None),
    REBOOT: ("+UFOTAS", None),
    GPRS: (R_OK, "\+CGATT\:\s+(\d+)"),
    SOCR: (R_OK, "^\d+"),
    SOCL: (R_OK, None),
    IMEI: (R_OK, "\+CGSN\:\s+(\d{15})"),
    IMSI: (R_OK, "(\d{15})"),
    SOST: (R_OK, None),
    SORF: (R_OK, None),
    CONS: (R_OK, None),
    SCONN: (R_OK, None),
    CGDCS: (R_OK, None),
    CGDCR: (R_OK, None),
    COPS: (R_OK, None),
    CGPR: (R_OK, None),
    CGAC: (R_OK, None),
    COAP: (R_OK, None),
    COAPC: (R_OK, None),
    NPING: (R_OK, None),
    USELCP: (R_OK, None)
}
