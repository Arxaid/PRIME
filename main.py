# This file is part of the PRIME Project.
#
# Copyright (c) 2024 Vladyslav Sosedov, INVE Studios.
# Licensed under the Apache License, Version 2.0.

from src.rtcmDecoder import PRIME
import numpy as np
import math

if __name__ == '__main__':
    primeDecoder = PRIME()
    msglen, msgcontent = primeDecoder.getmsg('1019.rtcm')
    msgvalues = primeDecoder.decodemsg(msgcontent)
    primeDecoder.getSatelliteCoords(msgvalues)

    print('====================== CALC ==================')
    GM = 3.986005e14
    omega_eps = 7.292115e-5
    e = 0.008834721171297133

    A = math.pow(5153.677635192871, 2)
    print(f'Semi-major axis: {A}')
    n0 = math.sqrt(GM/math.pow(A, 3))
    print(f'Computed mean motion: {n0}')
    n = n0 + 4.367324773749724e-09
    print(f'Corrected mean motion: {n}')
    Mk = 0.4945540624703678 + n*(-10)
    print(f'Mean anomaly: {Mk}')
    Ek0 = Mk
    Ek1 = Mk + e*math.sin(Ek0)
    Ek2 = Mk + e*math.sin(Ek1)
    Ek3 = Mk + e*math.sin(Ek2)
    Ek4 = Mk + e*math.sin(Ek3)
    Ek = Ek4
    print(f'Eccentric anomaly: {Ek}')
    vkcos = (math.cos(Ek) - e)/(1 - e*math.cos(Ek))
    vksin = (math.sqrt(1 - math.pow(e, 2))*math.sin(Ek))/(1 - e*math.cos(Ek))
    print(f'True anomaly: cos {vkcos}, sin {vksin}')
    Fk = math.acos(vkcos) + 0.5666441652896561
    print(f'Argument of Latitude: {Fk}')
    delta_uk = 3.46451997756958e-06*math.cos(2*Fk) + 3.2223761081695557e-07*math.sin(2*Fk)
    uk = Fk + delta_uk
    print(f'Argument of latitude correction: {delta_uk}, corrected argument of latitude: {uk}')
    delta_rk = 381.65625*math.cos(2*Fk) + 66.59375*math.sin(2*Fk)
    rk = A*(1-e*math.cos(Ek)) + delta_rk
    print(f'Radius correction: {delta_rk}, corrected radius: {rk}')
    delta_ik = 3.5390257835388184e-08*math.cos(2*Fk) + 1.3224780559539795e-07*math.sin(2*Fk)
    ik = 0.9768164824302019 + 1.4786330195717906e-10 + delta_ik
    print(f'Inclination correction: {delta_ik}, corrected inclination: {ik}')
    Xk1 = rk*math.cos(uk)
    Yk1 = rk*math.sin(uk)
    print(f'Position in the orbital plane: {Xk1}, {Yk1}')
    Omegak = -2.113868738843562 + (8.409993167115206e-09 - omega_eps)*(-10) - omega_eps*122384
    print(f'Corrected longitude of ascending node: {Omegak}')

    Xk = Xk1*math.cos(Omegak) - Yk1*math.sin(Omegak)*math.cos(ik)
    Yk = Xk1*math.sin(Omegak) + Yk1*math.cos(Omegak)*math.cos(ik)
    Zk = Yk1*math.sin(ik)
    print(f'Earth-fixed geocentric satellite coordinate:\nX:{Xk}, Y:{Yk}, Z:{Zk}')