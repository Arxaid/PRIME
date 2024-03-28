# This file is part of the PRIME Project.
#
# Copyright (c) 2024 Vladyslav Sosedov, INVE Studios.
# Licensed under the Apache License, Version 2.0.

from src.rtcmDecoder import PRIME
import numpy as np
import math

if __name__ == '__main__':
    primeDecoder = PRIME()
    print('======================== 1002 ========================')
    _, msgcontent_1002 = primeDecoder.get_message('data/1002.rtcm')
    msgvalues_1002 = primeDecoder.decode_message(msgcontent_1002, 'all')
    primeDecoder.get_GPS_pseudoranges(msgvalues_1002, number=6)
    print('======================== 1019 ========================')
    for counter in range(0,6):
        print(f'==================== Satellite #{counter+1} ====================')
        _, msgcontent = primeDecoder.get_message('data/1019.rtcm', number=counter)
        msgvalues = primeDecoder.decode_message(msgcontent)
        primeDecoder.get_GPS_satellite_coords(msgvalues, show=False)