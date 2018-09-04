PREFIX = "AT+"
POSTFIX = "\r\n"

RADIO_ON = "CFUN=1"
RADIO_OFF = "CFUN=0"
REBOOT = "NRB"
GPRS = "CGATT?"
SOCR = "NSOCR=\"DGRAM\",17,{},1"
SOCL = "NSOCL={}"
IMEI = "CGSN=1"
IMSI = "CIMI"
SOST = "NSOST={}"

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
    SOST: (R_OK, None)
}