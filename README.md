# Introduction

This repository contains python library for NB-IoT ublox SARA-N210 modem. The code was tested with Raspberry PI 3B and 
[EE-NBIOT-01 breakout module](https://shop.exploratory.engineering/collections/frontpage/products/ee-nbiot-01-v1-1-breakout-module) 
(NB-IoT module for Europe. Sim locked to Telenor Norway and can only be used in Norway).


# Hardware connections

The following four pins from EE-NBIOT-01 module needs to be connected:
- Tx to GPIO14 (TX)
- Rx to GPIO15 (RX)
- VCC to 3.3V
- GND to GND

# Licence

NBIoTPy library is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with NBIoTPy library. If not, see <https://www.gnu.org/licenses/>.