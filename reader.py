#! /bin/env python3

#
# ==== Influx DB configuration ====
#
DATABASE_NAME = 'readings'
DATABASE_HOST = 'http://localhost:8086'

#
# ==== Scale configuration ====
#
SERIAL_PORT = '/dev/tty.usbserial-DN02LKRG'
BAUDRATE = 9600
PREFACE_MAX_LINES = 100
CALIBRATION_G = 446.1
RAW_TARE = 107670

#
# end of configuration
# ==============================
#
import sys
import serial
from urllib import request
import logging

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG)

print_dict = lambda d: ','.join(str(k) + '=' + str(v) for k,v in d.items())

WRITE_URL = request.urljoin(DATABASE_HOST, 'write?db=' + request.quote(DATABASE_NAME))

def send_measurement(measurement, tags={}, fields={}):
    line = measurement
    if tags:
        line += ',' + print_dict(tags)
    line += ' ' + print_dict(fields)

    try:
        with request.urlopen(WRITE_URL, line.encode()) as r:
            pass
    except Exception as e:
        logging.error("Exception occurred when trying to connect to DB: %s", e)


class CalibratedScale:
    def __init__(self, raw_tare, calibration):
        self.raw_tare = raw_tare
        self.calibration = calibration

    def __call__(self, raw):
        return (self.raw_tare - raw) / self.calibration

raw_to_grams = CalibratedScale(RAW_TARE, CALIBRATION_G)

if __name__ == "__main__":

    with serial.Serial(SERIAL_PORT, baudrate=BAUDRATE) as ser:

        def lines():
            while True:
                yield ser.readline().strip().lower()

        def readings():
            # assuming configuration of:
            # <weight>,<unit>,<raw>,<temp>,
            # no timestamp, no remote temp, raw enabled
            for line in lines():
                parts = line.split(b',')
                raw = int(parts[2])
                local_temp = float(parts[3])
                yield raw, local_temp

        # initialize
        for n, line in enumerate(lines()):
            if line == b'readings:':
                break
            if n >= PREFACE_MAX_LINES:
                logging.error("Error: read %d lines but still no readings.", PREFACE_MAX_LINES)
                sys.exit(1)

        try:
            for raw, temp in readings():
                grams = int(raw_to_grams(raw))

                logging.info("%d g, %.2f C", grams, temp)

                send_measurement('weight', {'unit': 'g'}, {'value': grams})
                send_measurement('temperature', {'unit': 'C'}, {'value': temp})
        except KeyboardInterrupt:
            pass
