from matplotlib import pyplot as plt
import numpy as np
import math
import sympy as sym
from itertools import product
import dbcontroller


def make_heatmap():
    pass


def trilateration(data_a, data_b, data_c):
    x, y, R = sym.symbols('x,y,R')
    sign = [-1, 1]
    minans = (0, 0, 1000)
    for o, p, q in product(sign, sign, sign):
        result = sym.solve([(x - rpi_a[0]) ** 2 + (y - rpi_a[1]) ** 2 - (R + o * data_a["DIST"]) ** 2,
                         (x - rpi_b[0]) ** 2 + (y - rpi_b[1]) ** 2 - (R + p * data_b["DIST"]) ** 2,
                         (x - rpi_c[0]) ** 2 + (y - rpi_c[1]) ** 2 - (R + q * data_c["DIST"]) ** 2], [x, y, R])
        print(result)
        for ans in result:
            if 0 < ans[2] < minans[2]:
                minans = ans
    return minans[0], minans[1]

# ダミーデータ
data_a = {"DIST": 3, "MAC": "AA:BB:CC:DD:EE", "PWR": -42, "RPI_MAC": "rpi_a"}
data_b = {"DIST": 2, "MAC": "AA:BB:CC:DD:EE", "PWR": -20, "RPI_MAC": "rpi_b"}
data_c = {"DIST": 4, "MAC": "AA:BB:CC:DD:EE", "PWR": -20, "RPI_MAC": "rpi_b"}

rpi_a = [0, 0]
rpi_b = [0, 5]
rpi_c = [5*math.sqrt(3)/2, 5/2]
plt.scatter([rpi_a[0], rpi_b[0], rpi_c[0]], [rpi_a[1], rpi_b[1], rpi_c[1]])
x, y = trilateration(data_a, data_b, data_c)
plt.scatter(x, y)
plt.show()
