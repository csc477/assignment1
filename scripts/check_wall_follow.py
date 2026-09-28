#!/usr/bin/env python3
"""Assert the wall follower is tracking: robot advances and |cte| settles.

Usage: check_wall_follow.py [duration_seconds]   (default 40)
Exit 0 on success, nonzero with a message otherwise.
"""
import sys
import time

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from std_msgs.msg import Float32

ODOM_TOPIC = '/a200_0000/platform/odom'


class Checker(Node):
    def __init__(self):
        super().__init__('wall_follow_checker')
        self.ctes = []
        self.xy = []
        self.create_subscription(Float32, '/a200_0000/cte',
                                 lambda m: self.ctes.append(m.data), 10)
        self.create_subscription(
            Odometry, ODOM_TOPIC,
            lambda m: self.xy.append((m.pose.pose.position.x,
                                      m.pose.pose.position.y)), 10)


def main():
    duration = float(sys.argv[1]) if len(sys.argv) > 1 else 40.0
    rclpy.init()
    n = Checker()
    deadline = time.time() + duration
    while time.time() < deadline:
        rclpy.spin_once(n, timeout_sec=0.5)
    assert len(n.ctes) > 50, f'too few cte messages: {len(n.ctes)}'
    assert len(n.xy) > 10, f'too few odom messages: {len(n.xy)}'
    dx = n.xy[-1][0] - n.xy[0][0]
    dy = n.xy[-1][1] - n.xy[0][1]
    dist = (dx * dx + dy * dy) ** 0.5
    tail = n.ctes[len(n.ctes) // 2:]
    mean_abs = sum(abs(c) for c in tail) / len(tail)
    print(f'displacement {dist:.2f} m, mean |cte| (2nd half) {mean_abs:.3f} m')
    assert dist > 3.0, 'robot did not travel along the wall'
    assert mean_abs < 0.5, 'cross-track error did not settle under 0.5 m'
    print('PASS')
    rclpy.shutdown()


if __name__ == '__main__':
    main()
