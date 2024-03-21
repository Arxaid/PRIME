# This file is part of the PRIME Project.
#
# Copyright (c) 2024 Vladyslav Sosedov, INVE Studios.
# Licensed under the Apache License, Version 2.0.

import bitstruct
import crcmod
import math

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
        self.msgvalues = []
    
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

    def decodemsg(self, msgcontent: bytes):
        self.msgtype = bitstruct.unpack('u12', msgcontent)[0]
        self.msgdecodestr, self.msgoutput, self.coeff = _getcontent(self.msgtype)
        self.msgdecoded = bitstruct.unpack(self.msgdecodestr, msgcontent)
        counter = 0
        for value in self.msgdecoded:
            tuple_element = (self.msgoutput[counter], value * self.coeff[counter])
            self.msgvalues.append(tuple_element)
            counter += 1
        return self.msgvalues
    
    def getSatelliteCoords(self, values: tuple):
        GM = 3.986005e14
        OMEGA_EPS = 7.292115e-5

        A = math.pow(values[18][1], 2)
        n0 = math.sqrt(GM/math.pow(A, 3))
        n = n0 + values[13][1]
        Mk = values[12][1] + n*(-10)
        Ek0 = Mk
        Ek1 = Mk + values[16][1]*math.sin(Ek0)
        Ek2 = Mk + values[16][1]*math.sin(Ek1)
        Ek3 = Mk + values[16][1]*math.sin(Ek2)
        Ek4 = Mk + values[16][1]*math.sin(Ek3)
        Ek = Ek4
        vkcos = (math.cos(Ek) - values[16][1])/(1 - values[16][1]*math.cos(Ek))
        vksin = (math.sqrt(1 - math.pow(values[16][1], 2))*math.sin(Ek))/(1 - values[16][1]*math.cos(Ek))
        Fk = math.acos(vkcos) + values[25][1]
        delta_uk = values[15][1]*math.cos(2*Fk) + values[17][1]*math.sin(2*Fk)
        uk = Fk + delta_uk
        delta_rk = values[12][1]*math.cos(2*Fk) + values[24][1]*math.sin(2*Fk)
        rk = A*(1 - values[16][1]*math.cos(Ek)) + delta_rk
        delta_ik = values[20][1]*math.cos(2*Fk) + values[22][1]*math.sin(2*Fk)
        ik = values[23][1] + values[5][1] + delta_ik
        Xk1 = rk*math.cos(uk)
        Yk1 = rk*math.sin(uk)
        Omegak = values[21][1] + (values[26][1] - OMEGA_EPS)*(-10) - OMEGA_EPS*values[19][1]

        Xk = Xk1*math.cos(Omegak) - Yk1*math.sin(Omegak)*math.cos(ik)
        Yk = Xk1*math.sin(Omegak) + Yk1*math.cos(Omegak)*math.cos(ik)
        Zk = Yk1*math.sin(ik)
        print(f'Earth-fixed geocentric satellite coordinate:\nX:{Xk}, Y:{Yk}, Z:{Zk}') 


    # GM = 3.986005e14
    # omega_eps = 7.292115e-5
    # e = 0.008834721171297133

    # A = math.pow(5153.677635192871, 2)
    # print(f'Semi-major axis: {A}')
    # n0 = math.sqrt(GM/math.pow(A, 3))
    # print(f'Computed mean motion: {n0}')
    # n = n0 + 4.367324773749724e-09
    # print(f'Corrected mean motion: {n}')
    # Mk = 0.4945540624703678 + n*(-10)
    # print(f'Mean anomaly: {Mk}')
    # Ek0 = Mk
    # Ek1 = Mk + e*math.sin(Ek0)
    # Ek2 = Mk + e*math.sin(Ek1)
    # Ek3 = Mk + e*math.sin(Ek2)
    # Ek4 = Mk + e*math.sin(Ek3)
    # Ek = Ek4
    # print(f'Eccentric anomaly: {Ek}')
    # vkcos = (math.cos(Ek) - e)/(1 - e*math.cos(Ek))
    # vksin = (math.sqrt(1 - math.pow(e, 2))*math.sin(Ek))/(1 - e*math.cos(Ek))
    # print(f'True anomaly: cos {vkcos}, sin {vksin}')
    # Fk = math.acos(vkcos) + 0.5666441652896561
    # print(f'Argument of Latitude: {Fk}')
    # delta_uk = 3.46451997756958e-06*math.cos(2*Fk) + 3.2223761081695557e-07*math.sin(2*Fk)
    # uk = Fk + delta_uk
    # print(f'Argument of latitude correction: {delta_uk}, corrected argument of latitude: {uk}')
    # delta_rk = 381.65625*math.cos(2*Fk) + 66.59375*math.sin(2*Fk)
    # rk = A*(1-e*math.cos(Ek)) + delta_rk
    # print(f'Radius correction: {delta_rk}, corrected radius: {rk}')
    # delta_ik = 3.5390257835388184e-08*math.cos(2*Fk) + 1.3224780559539795e-07*math.sin(2*Fk)
    # ik = 0.9768164824302019 + 1.4786330195717906e-10 + delta_ik
    # print(f'Inclination correction: {delta_ik}, corrected inclination: {ik}')
    # Xk1 = rk*math.cos(uk)
    # Yk1 = rk*math.sin(uk)
    # print(f'Position in the orbital plane: {Xk1}, {Yk1}')
    # Omegak = -2.113868738843562 + (8.409993167115206e-09 - omega_eps)*(-10) - omega_eps*122384
    # print(f'Corrected longitude of ascending node: {Omegak}')

    # Xk = Xk1*math.cos(Omegak) - Yk1*math.sin(Omegak)*math.cos(ik)
    # Yk = Xk1*math.sin(Omegak) + Yk1*math.cos(Omegak)*math.cos(ik)
    # Zk = Yk1*math.sin(ik)
    # print(f'Earth-fixed geocentric satellite coordinate:\nX:{Xk}, Y:{Yk}, Z:{Zk}')   

def _getcontent(msgtype):
    pi = 3.1415926535898
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
        msgdecodestr = ('u12u12u30s1u5s1s3u6s1u24s20u7u8u8')
        msgoutput = ['Message type: ', 'Reference station ID: ', 'GPS Epoch Time: ', 'Synchronous GNSS Flag: ',
                     'Satellite Signals Processed: ', 'Divergence-free Smoothing Indicator: ', 'Smoothing Interval: ',
                     'Satellite ID: ', 'L1 Code Indicator: ', 'L1 Pseudorange: ', 'L1 PhaseRange - L1 Pseudorange: ',
                     'L1 Lock time Indicator: ', 'Integer L1 Pseudorange Modulus Ambiguity: ', 'L1 CNR: ']
    elif (msgtype == 1019):
        msgdecodestr = ('u12u6u10u4s2s14u8u16s8s16s22u10s16s16s32s16u32s16u32u16s16s32s16s32s16s32s24s8u6s1s1')
        msgoutput = ['Message type: ', 'Satellite ID: ', 'Week Number: ', 'SV Accuracy: ', 'CODE ON L2: ',
                     'IDOT: ', 'IODE: ', 'toc: ', 'af2: ', 'af1: ', 'af0: ', 'IODC: ', 'Crs: ', '∆n: ', 'M0: ',
                     'Cuc: ', 'e: ', 'Cus: ', 'A½: ', 'toe: ', 'Cic: ', 'Ω0: ', 'Cis: ', 'i0: ', 'Crc: ', 'ω: ',
                     'Ω.: ', 'tGD: ', 'SV HEALTH: ', 'L2 P data flag: ', 'Fit Interval: ']
        coeff =     [1, 1, 1, 1, 1, P2_43*pi, 1, P2_P4, P2_55, P2_43, P2_31, 1, P2_5, P2_43*pi, P2_31*pi, P2_29, P2_33,
                     P2_29, P2_19, P2_P4, P2_29, P2_31*pi, P2_29, P2_31*pi, P2_5, P2_31*pi, P2_43*pi, P2_31, 1, 1, 1]
        
    
    return msgdecodestr, msgoutput, coeff