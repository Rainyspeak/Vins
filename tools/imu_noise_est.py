#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""快速估计 IMU 白噪声参数（VINS 的 acc_n / gyr_n）。

用法（机载电脑上，飞机静止放桌面，采 5~10 分钟）:
    rostopic echo -p /mavros/imu/data_raw > imu_static.csv
    python3 tools/imu_noise_est.py imu_static.csv

说明:
  - 用相邻差分法做一阶估计: noise = std(diff(x)) / sqrt(2*dt)
  - 只估白噪声(acc_n/gyr_n); acc_w/gyr_w 需要长时 Allan 方差,
    请用 allan_variance_ros, 本脚本不猜这两个值
"""
import sys

import numpy as np


def load_imu_csv(path):
    # 拒绝包含 ".." 的路径, 只读当前目录树内的文件
    if any(part == '..' for part in path.replace('\\', '/').split('/')):
        raise ValueError('reject path containing ".."')
    data = np.genfromtxt(path, delimiter=',', names=True, deletechars='',
                         dtype=None, encoding=None)

    def find_field(sub):
        for name in data.dtype.names:
            if sub in name:
                return name
        raise KeyError('column not found: %s' % sub)

    f_time = find_field('%time')
    f_gyr = [find_field('angular_velocity.' + a) for a in 'xyz']
    f_acc = [find_field('linear_acceleration.' + a) for a in 'xyz']

    t = np.asarray(data[f_time], dtype=float)
    gyr = np.column_stack([np.asarray(data[f], dtype=float) for f in f_gyr])
    acc = np.column_stack([np.asarray(data[f], dtype=float) for f in f_acc])
    ok = ~(np.isnan(t) | np.isnan(gyr).any(axis=1) | np.isnan(acc).any(axis=1))
    return t[ok], gyr[ok], acc[ok]


def white_noise(sig, dt):
    # 相邻差分的一阶白噪声估计, 每轴独立
    return [float(np.std(np.diff(sig[:, k])) / np.sqrt(2.0 * dt)) for k in range(3)]


def main():
    if len(sys.argv) != 2:
        print('usage: python3 imu_noise_est.py <imu_static.csv>')
        return 1
    t, gyr, acc = load_imu_csv(sys.argv[1])
    dt = float(np.median(np.diff(t))) * 1e-9
    dur = (t[-1] - t[0]) * 1e-9

    mean_g = float(np.abs(gyr.mean(axis=0)).max())
    acc_norm = float(np.linalg.norm(acc.mean(axis=0)))
    warn = ''
    if mean_g > 0.02 or abs(acc_norm - 9.8) > 0.5:
        warn = '  <<< 警告: 数据似乎不是静止的, 请静止放置后重采!'

    gyr_n = white_noise(gyr, dt)
    acc_n = white_noise(acc, dt)

    def fmt(v):
        return 'x=%.5f  y=%.5f  z=%.5f' % tuple(v)

    print('样本 %d 个, 频率 %.1f Hz, 时长 %.1f s%s' % (len(t), 1.0 / dt, dur, warn))
    print('静止检查: |gyro|_max_mean=%.4f rad/s, |acc|=%.3f m/s^2' % (mean_g, acc_norm))
    print()
    print('gyr_n (每轴): ' + fmt(gyr_n))
    print('acc_n (每轴): ' + fmt(acc_n))
    print()
    print('建议写入 vins.yaml (取各轴最大值, 保守):')
    print('  acc_n: %.4f' % max(acc_n))
    print('  gyr_n: %.4f' % max(gyr_n))
    print()
    print('参考: 当前 yaml 为 acc_n: 0.095, gyr_n: 0.0122')
    print('acc_w / gyr_w 本次不估计, 维持现值或用 allan_variance_ros 测。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
