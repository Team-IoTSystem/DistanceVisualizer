from matplotlib import pyplot as plt
import matplotlib.patches as patches
import numpy as np
import math
import sympy as sym
from itertools import product
import dbcontroller
from certification_data import *
import sys
import time


# 各RPIの座標
rpi_a_coor = [0, 0]
rpi_b_coor = [0, 5]
rpi_c_coor = [3.5, 5 / 2]


# 各RPIのmacaddr
rpi_a_mac = "3476c58b5506", "b827ebe98ea9"
rpi_b_mac = "b827ebf277a4", "3476c58b5522"
rpi_c_mac = "b827ebb63034", "106f3f59c177"


# # ダミーデータ
# data_a = {"id": 6, "macaddr": "AA:BB:CC:DD:EE", "pwr": -42, "distance": 2, "rpimac": "rpi_a"}
# data_b = {"DIST": 3, "MAC": "AA:BB:CC:DD:EE", "PWR": -20, "RPI_MAC": "rpi_b"}
# data_c = {"DIST": 1, "MAC": "AA:BB:CC:DD:EE", "PWR": -20, "RPI_MAC": "rpi_c"}


def make_heatmap():
    pass



def trilateration(a_dist, b_dist, c_dist):
    x, y, R = sym.symbols('x,y,R', real=True)
    sign = [-1, 1]
    minans = (0, 0, 1000)
    for o, p, q in product(sign, sign, sign):
        result = sym.solve([(x - rpi_a_coor[0]) ** 2 + (y - rpi_a_coor[1]) ** 2 - (R + o * a_dist) ** 2,
                            (x - rpi_b_coor[0]) ** 2 + (y - rpi_b_coor[1]) ** 2 - (R + p * b_dist) ** 2,
                            (x - rpi_c_coor[0]) ** 2 + (y - rpi_c_coor[1]) ** 2 - (R + q * c_dist) ** 2], [x, y, R])
        for ans in result:
            if 0 < ans[2] < minans[2]:
                minans = ans

    # ax = plt.axes()
    # c_pia = patches.Circle(xy=(rpi_a_coor[0], rpi_a_coor[1]), radius=a_dist, fc='#D8D6D8FF', fill=False)
    # c_pib = patches.Circle(xy=(rpi_b_coor[0], rpi_b_coor[1]), radius=b_dist, fc='#D8D6D8FF', fill=False)
    # c_pic = patches.Circle(xy=(rpi_c_coor[0], rpi_c_coor[1]), radius=c_dist, fc='#D8D6D8FF', fill=False)
    # ax.add_patch(c_pia)
    # ax.add_patch(c_pib)
    # ax.add_patch(c_pic)
    return minans[0], minans[1]


class Device:
    SIZE = 3

    def __init__(self, macaddr):

        self.macaddr = macaddr
        self.data_a_list = []
        self.data_b_list = []
        self.data_c_list = []

    def put_data_a(self, devdata):
        if len(self.data_a_list) == self.SIZE:
            temp = self.data_a_list[1:]
            temp.append(devdata)
            self.data_a_list = temp
        else:
            self.data_a_list.append(devdata)

    def put_data_b(self, devdata):
        if len(self.data_b_list) == self.SIZE:
            temp = self.data_b_list[1:]
            temp.append(devdata)
            self.data_b_list = temp
        else:
            self.data_b_list.append(devdata)

    def put_data_c(self, devdata):
        if len(self.data_c_list) == self.SIZE:
            temp = self.data_c_list[1:]
            temp.append(devdata)
            self.data_c_list = temp
        else:
            self.data_c_list.append(devdata)

        # for i, d in enumerate(data_list):
        #     print("{}: {}".format(i, d["id"]))

    def get_movingaverage(self, data_list):
        sum = 0
        for item in data_list:
            sum += item["distance"]
        return sum / self.SIZE


def main(argv):
    debug = True

    # data_x[j] = {"id", "macaddr", "pwr", "distance", "rpimac", "rpicoor"}
    devlist = []
    for macaddr in argv[1:]:
        dev = Device(macaddr)
        devlist.append(dev)
        if debug:
            dev.macaddr = "84:89:AD:8D:85:F6"

    conn, cur = dbcontroller.mysql_connect(host, user, passwd, db)
    try:
        while True:
            for dev in devlist:
                dev.put_data_a(dbcontroller.select_latest(conn, cur, dev.macaddr, rpi_a_mac))
                dev.put_data_b(dbcontroller.select_latest(conn, cur, dev.macaddr, rpi_b_mac))
                dev.put_data_c(dbcontroller.select_latest(conn, cur, dev.macaddr, rpi_c_mac))

                print("#a:{}  ###b{}  ###c{}".format(dev.get_movingaverage(dev.data_a_list), dev.get_movingaverage(dev.data_b_list), dev.get_movingaverage(dev.data_c_list),))

                dev.coordinate = trilateration(
                    dev.get_movingaverage(dev.data_a_list),
                    dev.get_movingaverage(dev.data_b_list),
                    dev.get_movingaverage(dev.data_c_list),
                    )

                print("x,y={},{}".format(dev.coordinate[0], dev.coordinate[1]))
                plt.ion()
                plt.scatter(dev.coordinate[0], dev.coordinate[1], s=40)
            plt.scatter([rpi_a_coor[0], rpi_b_coor[0], rpi_c_coor[0]], [rpi_a_coor[1], rpi_b_coor[1], rpi_c_coor[1]], s=10, c='red')
            plt.axes().set_aspect('equal', 'datalim')
            plt.savefig("position.png")
            plt.pause(5)

    except KeyboardInterrupt:
        plt.close()
        conn.close()


if __name__ == "__main__":
    main(sys.argv)



