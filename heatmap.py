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
import queue


# 各RPIの座標
rpi_a_coor = [0, 0]
rpi_b_coor = [0, 5]
rpi_c_coor = [3.5, 5 / 2]


# 各RPIのmacaddr
rpi_a_mac = "3476c58b5506"
rpi_b_mac = "b827ebf277a4"
rpi_c_mac = "b827ebb63034"


# # ダミーデータ
# data_a = {"id": 6, "macaddr": "AA:BB:CC:DD:EE", "pwr": -42, "discance": 2, "rpimac": "rpi_a"}
# data_b = {"DIST": 3, "MAC": "AA:BB:CC:DD:EE", "PWR": -20, "RPI_MAC": "rpi_b"}
# data_c = {"DIST": 1, "MAC": "AA:BB:CC:DD:EE", "PWR": -20, "RPI_MAC": "rpi_c"}


def make_heatmap():
    pass


def trilateration(data_a, data_b, data_c):
    x, y, R = sym.symbols('x,y,R', real=True)
    sign = [-1, 1]
    minans = (0, 0, 1000)
    for o, p, q in product(sign, sign, sign):
        result = sym.solve([(x - rpi_a_coor[0]) ** 2 + (y - rpi_a_coor[1]) ** 2 - (R + o * data_a["distance"]) ** 2,
                            (x - rpi_b_coor[0]) ** 2 + (y - rpi_b_coor[1]) ** 2 - (R + p * data_b["distance"]) ** 2,
                            (x - rpi_c_coor[0]) ** 2 + (y - rpi_c_coor[1]) ** 2 - (R + q * data_c["distance"]) ** 2], [x, y, R])
        for ans in result:
            if 0 < ans[2] < minans[2]:
                minans = ans
    ax = plt.axes()
    c_pia = patches.Circle(xy=(rpi_a_coor[0], rpi_a_coor[1]), radius=data_a["distance"], fc='#D8D6D8FF', fill=False)
    c_pib = patches.Circle(xy=(rpi_b_coor[0], rpi_b_coor[1]), radius=data_b["distance"], fc='#D8D6D8FF', fill=False)
    c_pic = patches.Circle(xy=(rpi_c_coor[0], rpi_c_coor[1]), radius=data_c["distance"], fc='#D8D6D8FF', fill=False)
    ax.add_patch(c_pia)
    ax.add_patch(c_pib)
    ax.add_patch(c_pic)
    return minans[0], minans[1]


def main(argv):
    debug = True
    # devlist[i] = {"data_a":[], "data_b":[], "data_c":[], "macaddr":str}
    # data_x[j] = {"id", "macaddr", "pwr", "distance", "rpimac", "rpicoor"}
    devlist = []
    for i, macaddr in enumerate(argv[1:]):
        devlist.append({})
        devlist[i]["macaddr"] = macaddr
        if debug:
            devlist[i]["macaddr"] = "f4:0f:24:27:db:00"
        else:
            devlist[i]["macaddr"] = macaddr
    conn, cur = dbcontroller.mysql_connect(host, user, passwd, db)
    try:
        while True:
            for dev in devlist:
                dev["data_a"] = []
                dev["data_b"] = []
                dev["data_c"] = []
                dev["data_a"].append(dbcontroller.select_latest(conn, cur, dev["macaddr"], rpi_a_mac))
                dev["data_b"].append(dbcontroller.select_latest(conn, cur, dev["macaddr"], rpi_b_mac))
                dev["data_c"].append(dbcontroller.select_latest(conn, cur, dev["macaddr"], rpi_c_mac))
                # if dev["data_a"][0].get("id") and dev["data_b"][0].get("id") and dev["data_c"][0].get("id"):
                #     dev["data_a"][0]["rpicoor"] = rpi_a_coor
                #     dev["data_b"][0]["rpicoor"] = rpi_b_coor
                #     dev["data_c"][0]["rpicoor"] = rpi_c_coor
                # else:
                #     continue
                print("data_a: {}, data_b: {}, data_c: {}".format(dev["data_a"][0]["id"], dev["data_b"][0]["id"], dev["data_c"][0]["id"]))
                dev["coordinate"] = trilateration(dev["data_a"][0], dev["data_b"][0], dev["data_c"][0])
                plt.scatter(dev["coordinate"][0], dev["coordinate"][1], s=40)
            plt.scatter([rpi_a_coor[0], rpi_b_coor[0], rpi_c_coor[0]], [rpi_a_coor[1], rpi_b_coor[1], rpi_c_coor[1]], s=10, c='red')
            plt.axes().set_aspect('equal', 'datalim')
            plt.pause(5)
            plt.clf()

    except KeyboardInterrupt:
        plt.close()


if __name__ == "__main__":
    main(sys.argv)



