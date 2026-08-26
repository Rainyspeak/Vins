#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""双目时间戳对齐体检: 实测左右 infra 流频率 + 左右帧 |Δt| 与 3ms 同步容差通过率.

用法(机载电脑, 相机驱动运行中, 不需要 vins):
    python3 tools/stereo_sync_check.py
VINS 的双目同步容差是 3ms (rosNodeTest.cpp), 通过率低于 100% 就会有帧被扔掉.
"""
import rospy
from sensor_msgs.msg import Image

left_stamps = []
right_stamps = []


def make_cb(buf):
    def cb(msg):
        buf.append(msg.header.stamp.to_sec())
        if len(buf) > 400:
            del buf[:200]
    return cb


def main():
    rospy.init_node('stereo_sync_check', anonymous=True)
    rospy.Subscriber('/camera/infra1/image_rect_raw', Image, make_cb(left_stamps))
    rospy.Subscriber('/camera/infra2/image_rect_raw', Image, make_cb(right_stamps))
    print('waiting for images ...')
    rate = rospy.Rate(0.5)
    while not rospy.is_shutdown():
        rate.sleep()
        if not left_stamps or not right_stamps:
            continue
        t0 = max(left_stamps[-1], right_stamps[-1]) - 10.0
        L = [t for t in left_stamps if t >= t0]
        R = [t for t in right_stamps if t >= t0]
        if not L or not R:
            print('no recent stamps')
            continue
        diffs = sorted(min(abs(l - r) for r in R) * 1000.0 for l in L)
        n = len(diffs)
        within3 = sum(1 for d in diffs if d <= 3.0)
        print('左 %.1f Hz  右 %.1f Hz | |dt| 中位 %.2f ms  最大 %.2f ms | 3ms容差内 %d/%d (%.0f%%)' % (
            len(L) / 10.0, len(R) / 10.0, diffs[n // 2], diffs[-1],
            within3, n, 100.0 * within3 / n))


if __name__ == '__main__':
    main()
