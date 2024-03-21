# This file is part of the PRIME Project.
#
# Copyright (c) 2024 Vladyslav Sosedov, INVE Studios.
# Licensed under the Apache License, Version 2.0.

from src.rtcmDecoder import PRIME
import numpy as np
import math

if __name__ == '__main__':
    primeDecoder = PRIME()
    _, msgcontent = primeDecoder.get_message('1019.rtcm')
    msgvalues = primeDecoder.decode_message(msgcontent)
    primeDecoder.get_GPS_satellite_coords(msgvalues, show=True)