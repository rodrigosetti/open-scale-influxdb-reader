open-scale-influxdb-reader
================================

Reads data from [Open-Scale device](https://github.com/sparkfun/OpenScale)
connected to a serial port, and writes it into
an [InfluxDB database](https://github.com/influxdata/influxdb).

Requirements
---------------

### Sofware

 * Python 3
 * [pyserial](https://github.com/pyserial/pyserial)
 
### Hardware

 * A Scale (_e.g._ cheap kitchen scale)
 * [Sparkfun OpenScale](https://www.sparkfun.com/products/13261) or anything that
   will output the same serial data (Arduino + Temperature Sensor), as specified
   by [the firmware](https://github.com/sparkfun/OpenScale).
