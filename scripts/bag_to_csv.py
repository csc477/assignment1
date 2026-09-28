#!/usr/bin/env python3
"""Convert a recorded cross-track-error bag into a CSV file for submission.

Usage: bag_to_csv.py <bag_directory> <output.csv> [topic]

<bag_directory> is the directory written by
    ros2 bag record -o <bag_directory> /a200_0000/cte
The CSV has two columns: time in seconds since the first message, and the
cross-track error in metres.
"""
import csv
import sys

import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message

DEFAULT_TOPIC = '/a200_0000/cte'


def main():
    if len(sys.argv) < 3:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    bag_dir, out_path = sys.argv[1], sys.argv[2]
    topic = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_TOPIC

    reader = rosbag2_py.SequentialReader()
    reader.open(rosbag2_py.StorageOptions(uri=bag_dir, storage_id=''),
                rosbag2_py.ConverterOptions('', ''))
    types = {t.name: t.type for t in reader.get_all_topics_and_types()}
    if topic not in types:
        sys.exit(f'topic {topic} not in bag; it contains: {sorted(types)}')
    msg_type = get_message(types[topic])
    reader.set_filter(rosbag2_py.StorageFilter(topics=[topic]))

    rows = []
    t0 = None
    while reader.has_next():
        _, data, t_ns = reader.read_next()
        if t0 is None:
            t0 = t_ns
        msg = deserialize_message(data, msg_type)
        rows.append(((t_ns - t0) * 1e-9, msg.data))

    with open(out_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['time_s', 'cte_m'])
        for t, v in rows:
            w.writerow([f'{t:.4f}', f'{v:.5f}'])
    print(f'wrote {len(rows)} rows to {out_path}')


if __name__ == '__main__':
    main()
