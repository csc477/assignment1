// Gazebo (Ignition Fortress) GUI plugin: a single button that teleports the
// course robot back to its spawn pose via the world's `set_pose` service.
//
// Loaded by the Gazebo GUI from the config that launch/gazebo_world.launch.py
// generates, where it is docked directly below the Teleop panel. Configured
// through the plugin element:
//
//   <plugin filename="ResetPose" name="Reset pose">
//     <world>walls_one_sided</world>       <!-- optional, auto-detected -->
//     <model>a200_0000/robot</model>       <!-- Gazebo model name -->
//     <pose>-3 2 0.3 0 0 0</pose>          <!-- x y z roll pitch yaw -->
//   </plugin>

#ifndef WALL_FOLLOWING_ASSIGNMENT__RESET_POSE_HH_
#define WALL_FOLLOWING_ASSIGNMENT__RESET_POSE_HH_

#include <string>

#include <ignition/gui/Plugin.hh>
#include <ignition/math/Pose3.hh>
#include <ignition/transport/Node.hh>

namespace wall_following_assignment
{

class ResetPose : public ignition::gui::Plugin
{
  Q_OBJECT

  // One-line status shown under the button ("Reset", "service not found"...).
  Q_PROPERTY(QString status READ Status NOTIFY StatusChanged)

public:
  ResetPose();

  void LoadConfig(const tinyxml2::XMLElement * _pluginElem) override;

  // Called from QML when the button is clicked.
  Q_INVOKABLE void OnReset();

  QString Status() const;

signals:
  void StatusChanged();

private:
  // Thread-safe: may be called from a transport callback thread.
  void SetStatus(const std::string & _text);

  // Resolve the world name, querying Gazebo when the config did not set it.
  std::string WorldName();

  ignition::transport::Node node_;
  std::string world_;
  std::string model_{"robot"};
  ignition::math::Pose3d pose_{0, 0, 0.3, 0, 0, 0};
  QString status_;
};

}  // namespace wall_following_assignment

#endif  // WALL_FOLLOWING_ASSIGNMENT__RESET_POSE_HH_
