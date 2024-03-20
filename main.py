# This file is part of the PRIME Project.
#
# Copyright (c) 2024 Vladyslav Sosedov, INVE Studios.
# Licensed under the Apache License, Version 2.0.

from src.rtcmDecoder import PRIME
from pyrtcm import RTCMReader

if __name__ == '__main__':
    primeDecoder = PRIME()
    msglen, msgcontent = primeDecoder.getmsg('1019.rtcm')
    msgdecoded = primeDecoder.decodemsg(msgcontent)

    # print('============== Проверка корректности ==============')
    # stream = open('1019.rtcm', 'rb')
    # rtr = RTCMReader(stream)
    # for (raw_data, parsed_data) in rtr: print(parsed_data)
    # print('===================================================')