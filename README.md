# Introduction

This repository contains python library for NB-IoT ublox SARA-N210 modem. The code was tested with Raspberry PI 3B and 
[EE-NBIOT-01 breakout module](https://shop.exploratory.engineering/collections/frontpage/products/ee-nbiot-01-v1-1-breakout-module) 
(NB-IoT module for Europe. Sim locked to Telenor Norway and can only be used in Norway).


# Hardware connections

The following four pins from EE-NBIOT-01 module needs to be connected:
- Tx to Tx GPIO014
- Rx to Rx GPIO15
- VCC to 3.3V
- GND to GND

# Configuration
An example configuration is stored in the file `config.dist.json` which should be copied and renamed to `config.dist.json`.
All the parameteres specified in the config file should be reviewed and updated.

# TODO
- [ ] CoAP
- [ ] Downlink (receive from)

# Licence

Copyright (c) 2018, DAO (Distributed Arctic Observatory).
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
3. All advertising materials mentioning features or use of this software
   must display the following acknowledgement:
   This product includes software developed by the DAO.
4. Neither the name of the <organization> nor the
   names of its contributors may be used to endorse or promote products
   derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY DAO ''AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL DAO BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.