#!/usr/bin/env python3
import math

import rclpy
from rcl_interfaces.msg import (FloatingPointRange, ParameterDescriptor,
                                SetParametersResult)
from rclpy.node import Node
from rclpy.parameter import Parameter
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float32


class PID:
    def __init__(self, Kp, Td, Ti, dt):
        self.Kp = Kp
        self.Td = Td
        self.Ti = Ti
        self.curr_error = 0.0
        self.prev_error = 0.0
        self.sum_error = 0.0
        self.prev_error_deriv = 0.0
        self.curr_error_deriv = 0.0
        self.control = 0.0
        self.dt = dt

    def update_control(self, current_error, reset_prev=False):
        self.prev_error = self.curr_error
        self.curr_error = current_error
        self.prev_error_deriv = self.curr_error_deriv
        self.curr_error_deriv = (self.curr_error - self.prev_error) / self.dt
        self.sum_error = self.sum_error + self.curr_error

        self.control = (self.Kp * self.curr_error
                        + self.Td * self.curr_error_deriv
                        + self.Ti * self.sum_error)

    def get_control(self):
        return self.control


class WallFollowerHusky(Node):
    def __init__(self):
        super().__init__('wall_follower')

        # no defaults: these must be set from the launch file
        self.declare_parameter('forward_speed', Parameter.Type.DOUBLE)
        self.declare_parameter('desired_distance_from_wall',
                               Parameter.Type.DOUBLE)
        gain_range = FloatingPointRange(from_value=0.0, to_value=1.0, step=0.0)
        for name, default in (('Kp', 0.16), ('Td', 0.61), ('Ti', 0.0)):
            self.declare_parameter(
                name, default,
                ParameterDescriptor(floating_point_range=[gain_range]))

        self.forward_speed = self.get_parameter('forward_speed').value
        self.desired_distance_from_wall = self.get_parameter(
            'desired_distance_from_wall').value
        self.hz = 50

        self.pid_controller = PID(self.get_parameter('Kp').value,
                                  self.get_parameter('Td').value,
                                  self.get_parameter('Ti').value,
                                  1.0 / self.hz)

        # using geometry_msgs.msg.Twist messages
        self.cmd_pub = self.create_publisher(Twist, '/a200_0000/cmd_vel', 1)
        self.cte_pub = self.create_publisher(Float32, '/a200_0000/cte', 1)

        # this sets up a callback that runs every time another node
        # publishes a laser scan message
        self.laser_sub = self.create_subscription(
            LaserScan, '/a200_0000/sensors/lidar2d_0/scan',
            self.laser_scan_callback, 1)

        # live gain tuning via `ros2 param set` or rqt_reconfigure
        self.add_on_set_parameters_callback(self.parameters_callback)

    def parameters_callback(self, params):
        for p in params:
            if p.name in ('Kp', 'Td', 'Ti'):
                setattr(self.pid_controller, p.name, p.value)
                self.get_logger().info(f'{p.name} set to {p.value}')
        return SetParametersResult(successful=True)

    def laser_scan_callback(self, msg):
        # Compute the cross-track error as mentioned in the PID slides:
        # distance to the closest object minus the desired distance.
        valid = [r for r in msg.ranges
                 if not math.isnan(r) and not math.isinf(r)]
        if not valid:
            return
        current_error = min(valid) - self.desired_distance_from_wall
        self.cte_pub.publish(Float32(data=current_error))

        # You can populate the command based on either of the following
        # two methods:
        # (1) using only the distance to the closest wall
        # (2) using the distance to the closest wall and the orientation
        #     of the wall
        # If you select option 2, you might want to use cascading PID
        # control.
        self.pid_controller.update_control(current_error)
        twist = Twist()
        twist.linear.x = self.forward_speed
        twist.angular.z = self.pid_controller.get_control()
        self.cmd_pub.publish(twist)


def main():
    rclpy.init()
    node = WallFollowerHusky()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()


if __name__ == '__main__':
    main()
