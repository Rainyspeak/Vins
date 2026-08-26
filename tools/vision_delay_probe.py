#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测量视觉定位链路的软件延迟(消息时间戳 -> 到达时刻).

用法(机载电脑, mavros 与 vins 均在运行):
    python3 tools/vision_delay_probe.py                          # 测 vins_to_mavros 出口
    python3 tools/vision_delay_probe.py /vins_fusion/odometry    # 测 VINS 出口
消息时间戳源自图像采集时刻(RealSense global time 映射到系统时钟),
所以打印的延迟覆盖 相机采集->VINS解算->转发 全链路.
Ctrl+C 结束时输出最终统计.
"""
import sys

import numpy as np
import rospy
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry

samples = []


def on_stamp(header):
    delay_ms = (rospy.Time.now() - header.stamp).to_sec() * 1000.0
    if -50.0 < delay_ms < 2000.0:
        samples.append(delay_ms)


def stats():
    if not samples:
        print('no samples yet')
        return
    a = np.array(samples)
    print('N=%d  mean=%.1f ms  median=%.1f ms  p95=%.1f ms  min=%.1f  max=%.1f ms' % (
        len(a), a.mean(), np.median(a), np.percentile(a, 95), a.min(), a.max()))


def main():
    topic = sys.argv[1] if len(sys.argv) > 1 else '/mavros/vision_pose/pose'
    rospy.init_node('vision_delay_probe', anonymous=True)
    if 'odometry' in topic:
        rospy.Subscriber(topic, Odometry, lambda m: on_stamp(m.header))
    else:
        rospy.Subscriber(topic, PoseStamped, lambda m: on_stamp(m.header))
    print('probing %s ...' % topic)
    rate = rospy.Rate(0.2)
    while not rospy.is_shutdown():
        rate.sleep()
        stats()


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print('\n--- final ---')
        stats()
