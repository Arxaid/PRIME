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
    
    def get_message(self, path):
        with open(path, 'rb') as file:
            data = file.read()
        if data[0:1] == b'\xd3':
            frame_header_unpack = bitstruct.unpack('u8u6u10', data[0:3])
            self.msglen = frame_header_unpack[2]
            self.crcValue = self.crcFunc(data[0:6 + self.msglen])
            if self.crcValue == 0:
                self.msgcontent = data[3:3 + self.msglen]

        return self.msglen, self.msgcontent

    def decode_message(self, msgcontent: bytes):
        self.msgtype = bitstruct.unpack('u12', msgcontent)[0]
        self.msgdecodestr, self.msgoutput, self.coeff = _get_content(self.msgtype)
        self.msgdecoded = bitstruct.unpack(self.msgdecodestr, msgcontent)
        counter = 0
        for value in self.msgdecoded:
            tuple_element = (self.msgoutput[counter], value * self.coeff[counter])
            self.msgvalues.append(tuple_element)
            counter += 1

        return self.msgvalues
    
    def get_GPS_satellite_coords(self, values: tuple, show=False):
        assert values[0][1] == 1019, 'Calculation is only possible for GPS Satellite Ephemeris Data (1019) message.'
        # WGS-84 value for the product of gravitational constant G and the mass of the Earth M
        GM = 3.986005e14
        # WGS-84 value of the Earth’s rotation rate
        OMEGA_EPS = 7.292115e-5

        semi_major_axis = math.pow(values[18][1], 2)
        mean_motion_computed = math.sqrt(GM / math.pow(semi_major_axis, 3))
        mean_motion = mean_motion_computed + values[13][1]
        mean_anomaly = values[14][1] + mean_motion*(-10)
        eccentric_anomaly_0 = mean_anomaly
        eccentric_anomaly_1 = mean_anomaly + values[16][1] * math.sin(eccentric_anomaly_0)
        eccentric_anomaly_2 = mean_anomaly + values[16][1] * math.sin(eccentric_anomaly_1)
        eccentric_anomaly_3 = mean_anomaly + values[16][1] * math.sin(eccentric_anomaly_2)
        eccentric_anomaly =   mean_anomaly + values[16][1] * math.sin(eccentric_anomaly_3)
        true_anomaly_cos = (math.cos(eccentric_anomaly) - values[16][1])/(1 - values[16][1] * math.cos(eccentric_anomaly))
        true_anomaly_sin = (math.sqrt(1 - math.pow(values[16][1], 2)) * math.sin(eccentric_anomaly))/(1 - values[16][1]*math.cos(eccentric_anomaly))
        latitude_arg = math.acos(true_anomaly_cos) + values[25][1]
        latitude_corr_arg = values[15][1] * math.cos(2 * latitude_arg) + values[17][1] * math.sin(2 * latitude_arg)
        latitude_corr = latitude_arg + latitude_corr_arg
        radius_corr_arg = values[24][1] * math.cos(2 * latitude_arg) + values[12][1] * math.sin(2 * latitude_arg)
        radius_corr = semi_major_axis * (1 - values[16][1] * math.cos(eccentric_anomaly)) + radius_corr_arg
        inclination_corr_arg = values[20][1] * math.cos(2 * latitude_arg) + values[22][1] * math.sin(2 * latitude_arg)
        inclination_corr = values[23][1] + values[5][1] + inclination_corr_arg
        orbital_plane_X = radius_corr * math.cos(latitude_corr)
        orbital_plane_Y = radius_corr * math.sin(latitude_corr)
        ascending_node_longitude_corr = values[21][1] + (values[26][1] - OMEGA_EPS)*(-10) - OMEGA_EPS*values[19][1]

        Xk = orbital_plane_X * math.cos(ascending_node_longitude_corr) - orbital_plane_Y * math.sin(ascending_node_longitude_corr) * math.cos(inclination_corr)
        Yk = orbital_plane_X * math.sin(ascending_node_longitude_corr) + orbital_plane_Y * math.cos(ascending_node_longitude_corr) * math.cos(inclination_corr)
        Zk = orbital_plane_Y * math.sin(inclination_corr)
        
        if (show==True):
            print(f'Semi-major axis: {semi_major_axis}')
            print(f'Computed mean motion: {mean_motion_computed}')
            print(f'Corrected mean motion: {mean_motion}')
            print(f'Mean anomaly: {mean_anomaly}')
            print(f'Eccentric anomaly: {eccentric_anomaly}')
            print(f'True anomaly: cos {true_anomaly_cos}, sin {true_anomaly_sin}')
            print(f'Argument of Latitude: {latitude_arg}')
            print(f'Argument of latitude correction: {latitude_corr_arg}, corrected argument of latitude: {latitude_corr}')
            print(f'Radius correction: {radius_corr_arg}, corrected radius: {radius_corr}')
            print(f'Inclination correction: {inclination_corr_arg}, corrected inclination: {inclination_corr}')
            print(f'Position in the orbital plane: {orbital_plane_X}, {orbital_plane_Y}')
            print(f'Corrected longitude of ascending node: {ascending_node_longitude_corr}')
        print(f'Earth-fixed geocentric satellite coordinate:\nX: {Xk}, Y: {Yk}, Z: {Zk}')
        
def _get_content(msgtype):
    PI = 3.1415926535898
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
        coeff =     [1, 1, 1, 1, 1, P2_43*PI, 1, P2_P4, P2_55, P2_43, P2_31, 1, P2_5, P2_43*PI, P2_31*PI, P2_29, P2_33,
                     P2_29, P2_19, P2_P4, P2_29, P2_31*PI, P2_29, P2_31*PI, P2_5, P2_31*PI, P2_43*PI, P2_31, 1, 1, 1]
        
    return msgdecodestr, msgoutput, coeff