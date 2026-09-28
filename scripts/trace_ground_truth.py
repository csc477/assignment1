#!/usr/bin/env python3
"""Log the robot's true pose from Gazebo, and report whether it completed a lap.

Wheel odometry on /a200_0000/platform/odom is not usable for this: a robot
pinned against a wall with its wheels spinning keeps integrating motion, so a
crashed run shows up as a large phantom circle. This reads Gazebo's own pose
feed instead.

Usage: trace_ground_truth.py <world> [duration_seconds]
"""
import math
import re
import subprocess
import sys
import time

# Course extents of walls_one_sided, from the wall poses in the .sdf. A lap
# means visiting all four sides of the wall ring.
QUADRANTS = (
    ('E', lambda x, y: x > 20.0),
    ('N', lambda x, y: y > 17.5),
    ('W', lambda x, y: x < -3.0),
    ('S', lambda x, y: y < 3.5),
)


def main():
    world = sys.argv[1] if len(sys.argv) > 1 else 'walls_one_sided'
    duration = float(sys.argv[2]) if len(sys.argv) > 2 else 180.0

    cmd = ['ign', 'topic', '-e', '-t', f'/world/{world}/dynamic_pose/info']
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                            text=True, bufsize=1)

    t0 = time.time()
    nxt = 0.0
    in_robot = False
    x = y = z = None
    visited = []
    path = []
    print('   t        x        y       z    visited')
    try:
        for line in proc.stdout:
            if time.time() - t0 > duration:
                break
            if 'name:' in line:
                in_robot = 'a200_0000/robot' in line
                continue
            if not in_robot:
                continue
            m = re.match(r'\s*([xyz]):\s*(-?[\d.e+-]+)', line)
            if not m:
                continue
            if m.group(1) == 'x':
                x = float(m.group(2))
            elif m.group(1) == 'y':
                y = float(m.group(2))
            elif m.group(1) == 'z':
                z = float(m.group(2))
                if x is None or y is None:
                    continue
                # Record only first arrival on each side. Appending on every
                # change instead makes the summary alternate endlessly while
                # the robot straddles two regions near a corner.
                for name, test in QUADRANTS:
                    if test(x, y) and name not in visited:
                        visited.append(name)
                el = time.time() - t0
                path.append((el, x, y))
                if el >= nxt:
                    print('%6.1f %8.2f %8.2f %7.3f    %s'
                          % (el, x, y, z, ''.join(visited)))
                    nxt += 5.0
                in_robot = False
    except KeyboardInterrupt:
        pass
    proc.terminate()

    print()
    print('side visit order:', ' '.join(visited) if visited else '(none)')
    # A full lap touches all four sides.
    seen = set(visited)
    print('sides touched: %d/4 (%s)' % (len(seen), ','.join(sorted(seen))))
    if len(seen) == 4:
        print('RESULT: completed a lap')
    else:
        print('RESULT: did NOT complete a lap')
    if path:
        # Total ground-truth path length, versus straight-line displacement.
        dist = sum(math.dist(path[i][1:], path[i + 1][1:])
                   for i in range(len(path) - 1))
        print('ground-truth path length %.1f m, final pose (%.2f, %.2f)'
              % (dist, path[-1][1], path[-1][2]))


if __name__ == '__main__':
    main()
