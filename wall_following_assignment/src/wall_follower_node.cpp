#include <cmath>
#include <memory>
#include <vector>

#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <sensor_msgs/msg/laser_scan.hpp>
#include <std_msgs/msg/float32.hpp>

#include <wall_following_assignment/pid.h>

class WallFollowerNode : public rclcpp::Node {
 public:
  WallFollowerNode() : rclcpp::Node("wall_follower") {
    // Getting params before setting up the topic subscribers,
    // otherwise the callback might get executed with default
    // wall following parameters. No defaults: these must be set from
    // the launch file.
    forward_speed_ = declare_parameter<double>("forward_speed");
    desired_distance_from_wall_ =
        declare_parameter<double>("desired_distance_from_wall");

    rcl_interfaces::msg::ParameterDescriptor gain_desc;
    rcl_interfaces::msg::FloatingPointRange range;
    range.from_value = 0.0;
    range.to_value = 1.0;
    range.step = 0.0;
    gain_desc.floating_point_range = {range};
    kp_ = declare_parameter("Kp", 0.16, gain_desc);
    td_ = declare_parameter("Td", 0.61, gain_desc);
    ti_ = declare_parameter("Ti", 0.0, gain_desc);
    pid_ = std::make_unique<PID>(kp_, td_, ti_, 1.0 / 50.0);

    // Provided: live gain tuning via `ros2 param set` or rqt_reconfigure.
    params_cb_ = add_on_set_parameters_callback(
        [this](const std::vector<rclcpp::Parameter>& params) {
          for (const auto& p : params) {
            if (p.get_name() == "Kp") kp_ = p.as_double();
            if (p.get_name() == "Td") td_ = p.as_double();
            if (p.get_name() == "Ti") ti_ = p.as_double();
          }
          pid_->set_gains(kp_, td_, ti_);
          rcl_interfaces::msg::SetParametersResult result;
          result.successful = true;
          return result;
        });

    // todo: set up the command publisher on topic '/a200_0000/cmd_vel'
    // using geometry_msgs::msg::Twist messages
    // cmd_pub_ = ??

    // todo: set up the cross-track error publisher on topic
    // '/a200_0000/cte' using std_msgs::msg::Float32 messages
    // cte_pub_ = ??

    // todo: set up the laser scan subscriber on topic
    // '/a200_0000/sensors/lidar2d_0/scan'; this sets up a callback
    // function that gets executed every time another node publishes
    // a laser scan message
    // laser_sub_ = ??
  }

 private:
  void laser_scan_callback(const sensor_msgs::msg::LaserScan::SharedPtr msg) {
    geometry_msgs::msg::Twist cmd;
    cmd.linear.x = forward_speed_;  // forward speed is fixed

    // Populate this command based on the distance to the closest
    // object in laser scan. I.e. compute the cross-track error
    // as mentioned in the PID slides, and publish it on the cte topic.
    // Watch out for NaN and inf values in msg->ranges.

    // You can populate the command based on either of the following
    // two methods:
    // (1) using only the distance to the closest wall
    // (2) using the distance to the closest wall and the orientation
    //     of the wall
    //
    // If you select option 2, you might want to use cascading PID
    // control.

    // cmd.angular.z = ???
    // cmd_pub_->publish(cmd);
    (void)msg;
  }

  double forward_speed_ = 0.0;               // in meters / sec
  double desired_distance_from_wall_ = 0.0;  // in meters
  double kp_, td_, ti_;
  std::unique_ptr<PID> pid_;
  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr cmd_pub_;
  rclcpp::Publisher<std_msgs::msg::Float32>::SharedPtr cte_pub_;
  rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr laser_sub_;
  OnSetParametersCallbackHandle::SharedPtr params_cb_;
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<WallFollowerNode>());
  rclcpp::shutdown();
  return 0;
}
