# This file is part of the PRIME Project.
#
# Copyright (c) 2024 Vladyslav Sosedov, INVE Studios.
# Licensed under the Apache License, Version 2.0.

import bitstruct
import crcmod

class PRIME:
    def __init__(self):
        self.crcFunc = crcmod.crcmod.mkCrcFun(0x1864CFB, rev = False, initCrc=0x000000, xorOut=0x000000)
        self.crcValue = 0
        self.msglen = None
        self.msgcontent = None
        self.msgtype = None
        self.msgcontent = ''
        self.msgoutput = ''
        self.msgdecoded = None
    
    def getmsg(self, path):
        with open(path, 'rb') as file:
            data = file.read()
        if data[0:1] == b'\xd3':
            frame_header_unpack = bitstruct.unpack('u8u6u10', data[0:3])
            self.msglen = frame_header_unpack[2]
            self.crcValue = self.crcFunc(data[0:6 + self.msglen])
            if self.crcValue == 0:
                self.msgcontent = data[3:3 + self.msglen]
        return self.msglen, self.msgcontent

    def decodemsg(self, msgcontent):
        self.msgtype = bitstruct.unpack('u12', msgcontent)[0]
        self.msgdecodestr, self.msgoutput, self.coeff = _getcontent(self.msgtype)
        self.msgdecoded = bitstruct.unpack(self.msgdecodestr, msgcontent)
        
        counter = 0
        for value in self.msgdecoded:
            print(f'{self.msgoutput[counter]}{value * self.coeff[counter]}')
            counter += 1
        return self.msgdecoded
    
def _getcontent(msgtype):
    P2_P4 = 16
    P2_4 = 0.0625
    P2_5 = 0.03125
    P2_6 = 0.015625
    P2_10 = 0.0009765625
    P2_11 = 0.00048828125
    P2_19 = 1.9073486328125e-06
    P2_20 = 9.5367431640625e-07
    P2_24 = 5.960464477539063e-08
    P2_28 = 3.725290298461914e-09
    P2_29 = 1.862645149230957e-09
    P2_30 = 9.313225746154785e-10
    P2_31 = 4.656612873077393e-10
    P2_32 = 2.3283064365386963e-10
    P2_33 = 1.1641532182693481e-10
    P2_34 = 5.820766091346741e-11
    P2_41 = 4.547473508864641e-13
    P2_43 = 1.1368683772161603e-13
    P2_46 = 1.4210854715202004e-14
    P2_50 = 8.881784197001252e-16
    P2_55 = 2.7755575615628914e-17
    P2_59 = 1.734723475976807e-18
    P2_66 = 1.3552527156068805e-20

    if (msgtype == 1002):
        msgdecodestr = ('')
        msgoutput = ('')
    elif (msgtype == 1019):
        msgdecodestr = ('u12u6u10u4s2s14u8u16s8s16s22u10s16s16s32s16u32s16u32u16s16s32s16s32s16s32s24s8u6s1s1')
        msgoutput = ['Message type: ', 'Satellite ID: ', 'Week Number: ', 'SV Accuracy: ', 'CODE ON L2: ',
                     'IDOT: ', 'IODE: ', 'toc: ', 'af2: ', 'af1: ', 'af0: ', 'IODC: ', 'Crs: ', '∆n: ', 'M0: ',
                     'Cuc: ', 'e: ', 'Cus: ', 'A½: ', 'toe: ', 'Cic: ', 'Ω0: ', 'Cis: ', 'i0: ', 'Crc: ', 'ω: ',
                     'Ω.: ', 'tGD: ', 'SV HEALTH: ', 'L2 P data flag: ', 'Fit Interval: ']
        coeff =     [1,1,1,1,1,P2_43,1,P2_P4,P2_55,P2_43,P2_31,1,P2_5,P2_43,P2_31,P2_29,P2_33,
                     P2_29,P2_19,P2_P4,P2_29,P2_31,P2_29,P2_31,P2_5,P2_31,P2_43,P2_31,1,1,1]
    return msgdecodestr, msgoutput, coeff