from matplotlib import pyplot as plt
import numpy as np
import sympy as sym
from itertools import product
import dbcontroller
from certification_data import *
import sys
import mpld3


# 各RPIの座標
rpi_a_coor = [0, 0]
rpi_b_coor = [0, 5]
rpi_c_coor = [3.5, 5 / 2]

# ヒートマップ表示範囲[m]
map_range = 5

# 各RPIのmacaddr
rpi_a_mac = "3476c58b5506", "b827ebe98ea9"
rpi_b_mac = "b827ebf277a4", "3476c58b5522"
rpi_c_mac = "b827ebb63034", "106f3f59c177"


# # ダミーデータ
# data_a = {"id": 6, "macaddr": "AA:BB:CC:DD:EE", "pwr": -42, "distance": 2, "rpimac": "rpi_a"}


def trilateration(a_dist, b_dist, c_dist):
    """各RPIを中心、デバイスまでの距離を半径とした3つの円を考え、それら3円に接する最も半径の小さい円の中心座標と半径を返す"""
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
    print("R:{}".format(minans[2]))
    return minans[0], minans[1], minans[2]


class Device:
    PI_DATA_SIZE = 5
    CIRCLE_DATA_SIZE = 5

    def __init__(self, macaddr):
        self.macaddr = macaddr
        self.data_a_list = []
        self.data_b_list = []
        self.data_c_list = []
        self.range_circle_list = []

    def put_data_a(self, devdata):
        if len(self.data_a_list) == self.PI_DATA_SIZE:
            temp = self.data_a_list[1:]
            temp.append(devdata)
            self.data_a_list = temp
        else:
            self.data_a_list.append(devdata)

    def put_data_b(self, devdata):
        if len(self.data_b_list) == self.PI_DATA_SIZE:
            temp = self.data_b_list[1:]
            temp.append(devdata)
            self.data_b_list = temp
        else:
            self.data_b_list.append(devdata)

    def put_data_c(self, devdata):
        if len(self.data_c_list) == self.PI_DATA_SIZE:
            temp = self.data_c_list[1:]
            temp.append(devdata)
            self.data_c_list = temp
        else:
            self.data_c_list.append(devdata)

    def put_range_circle(self, circle_data):
        if len(self.range_circle_list) == self.CIRCLE_DATA_SIZE:
            temp = self.range_circle_list[1:]
            temp.append(circle_data)
            self.range_circle_list = temp
        else:
            self.range_circle_list.append(circle_data)

    def get_moving_average_of_dist(self, data_list):
        sum = 0
        for item in data_list:
            sum += item["distance"]
        return sum / self.PI_DATA_SIZE

    def get_moving_average_of_circle(self, data_list):
        sum_x = 0
        sum_y = 0
        sum_r = 0
        for item in data_list:
            sum_x += item[0]
            sum_y += item[1]
            sum_r += item[2]
        return sum_x / self.CIRCLE_DATA_SIZE, sum_y / self.CIRCLE_DATA_SIZE, sum_r / self.CIRCLE_DATA_SIZE

    def make_heatmap(self, circle_list):
        squares = 40
        weight = 10
        dot_per_meter = int(squares / map_range)
        map_ary = [[0]*squares for s in range(squares)]
        for i, circle in enumerate(circle_list):
            circle_squ = [int(p * dot_per_meter) for p in circle]
            y_min = circle_squ[1] - circle_squ[2]
            y_max = circle_squ[1] + circle_squ[2]
            for y in range(squares):
                if y_min < y < y_max:
                    for x in range(squares):
                        if (x-circle_squ[0])**2 + (y-circle_squ[1])**2 < circle_squ[2]**2:
                            map_ary[x][y] += weight
        return map_ary

    def make_histogram(self, circle_list):
        # ドットの数
        squares = 5
        dot_per_meter = int(squares / map_range)
        x_ary = []
        y_ary = []
        for i, circle in enumerate(circle_list):
            circle_squ = [p*dot_per_meter for p in circle]
            for x_squ, y_squ in product(range(squares), range(squares)):
                if (x_squ-circle_squ[0])**2 + (y_squ-circle_squ[1])**2 <= circle_squ[2]**2:
                    x_ary.append(x_squ / dot_per_meter)
                    y_ary.append(y_squ / dot_per_meter)
        return x_ary, y_ary


def main(argv):
    debug = True
    map_margin = 1
    devlist = []
    for macaddr in argv[1:]:
        dev = Device(macaddr)
        devlist.append(dev)
        if debug:
            dev.macaddr = "84:89:AD:8D:85:F6"
            dev.hostname = "iPhone"

    conn, cur = dbcontroller.mysql_connect(host, user, passwd, db)
    try:
        while True:
            for dev in devlist:
                dev.put_data_a(dbcontroller.select_latest(conn, cur, dev.macaddr, rpi_a_mac))
                dev.put_data_b(dbcontroller.select_latest(conn, cur, dev.macaddr, rpi_b_mac))
                dev.put_data_c(dbcontroller.select_latest(conn, cur, dev.macaddr, rpi_c_mac))

                print("#a:{}  #b{}  #c{}".format(dev.get_moving_average_of_dist(dev.data_a_list), dev.get_moving_average_of_dist(dev.data_b_list), dev.get_moving_average_of_dist(dev.data_c_list), ))
                # n点で移動平均をとった距離データを元に3辺測位をする
                dev.coordinate = trilateration(
                    dev.get_moving_average_of_dist(dev.data_a_list),
                    dev.get_moving_average_of_dist(dev.data_b_list),
                    dev.get_moving_average_of_dist(dev.data_c_list),
                )
                dev.put_range_circle(dev.coordinate)
                x, y = dev.make_histogram(dev.range_circle_list)
                plt.clf()
                plt.ion()
                plt.hist2d(x, y, bins=map_range+map_margin*2, range=[[0-map_margin, map_range+map_margin], [0-map_margin, map_range+map_margin]])
                xcoord = float(dev.get_moving_average_of_circle(dev.range_circle_list)[0])
                ycoord = float(dev.get_moving_average_of_circle(dev.range_circle_list)[1])
                plt.text(xcoord, ycoord, dev.hostname, fontsize=15, color="white")
            plt.colorbar()
            plt.scatter([rpi_a_coor[0], rpi_b_coor[0], rpi_c_coor[0]], [rpi_a_coor[1], rpi_b_coor[1], rpi_c_coor[1]], s=50, c='red')
            plt.axes().set_aspect('equal', 'datalim')
            plt.savefig("position.png")
            with open('heatmap.html', 'w') as fout:
                fout.write(mpld3.fig_to_html(plt.gcf()))
                # TODO DBに送信
            plt.pause(5)

    except KeyboardInterrupt:
        plt.close()
        conn.close()


if __name__ == "__main__":
    main(sys.argv)

