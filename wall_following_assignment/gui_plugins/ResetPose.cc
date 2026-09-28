#include "ResetPose.hh"

#include <ignition/common/Console.hh>
#include <ignition/gui/Application.hh>
#include <ignition/msgs/boolean.pb.h>
#include <ignition/msgs/pose.pb.h>
#include <ignition/msgs/stringmsg_v.pb.h>
#include <ignition/msgs/Utility.hh>
#include <ignition/plugin/Register.hh>

#include <functional>
#include <sstream>
#include <vector>

namespace wall_following_assignment
{

ResetPose::ResetPose()
{
  // Expose this object to ResetPose.qml as `ResetPose`. Done here rather than
  // in LoadConfig because the QML item is instantiated before LoadConfig runs.
  ignition::gui::App()->Engine()->rootContext()->setContextProperty("ResetPose", this);
}

void ResetPose::LoadConfig(const tinyxml2::XMLElement * _pluginElem)
{
  if (this->title.empty()) {
    this->title = "Reset pose";
  }
  if (_pluginElem == nullptr) {
    return;
  }
  if (auto elem = _pluginElem->FirstChildElement("world"); elem && elem->GetText()) {
    world_ = elem->GetText();
  }
  if (auto elem = _pluginElem->FirstChildElement("model"); elem && elem->GetText()) {
    model_ = elem->GetText();
  }
  if (auto elem = _pluginElem->FirstChildElement("pose"); elem && elem->GetText()) {
    std::istringstream ss(elem->GetText());
    double x, y, z, roll, pitch, yaw;
    if (ss >> x >> y >> z >> roll >> pitch >> yaw) {
      pose_ = ignition::math::Pose3d(x, y, z, roll, pitch, yaw);
    } else {
      ignerr << "[ResetPose] <pose> must be 'x y z roll pitch yaw', got '"
             << elem->GetText() << "'; keeping " << pose_ << std::endl;
    }
  }
}

QString ResetPose::Status() const
{
  return status_;
}

void ResetPose::SetStatus(const std::string & _text)
{
  // Transport callbacks arrive on a non-GUI thread; hop to the GUI thread
  // before touching a property QML is bound to.
  QMetaObject::invokeMethod(
    this, [this, _text]() {
      status_ = QString::fromStdString(_text);
      emit StatusChanged();
    }, Qt::QueuedConnection);
}

std::string ResetPose::WorldName()
{
  if (!world_.empty()) {
    return world_;
  }
  ignition::msgs::StringMsg_V worlds;
  bool result = false;
  if (node_.Request("/gazebo/worlds", 1000, worlds, result) && result && worlds.data_size() > 0) {
    world_ = worlds.data(0);
  }
  return world_;
}

void ResetPose::OnReset()
{
  const std::string world = WorldName();
  if (world.empty()) {
    SetStatus("Could not determine the Gazebo world name");
    return;
  }
  const std::string service = "/world/" + world + "/set_pose";

  std::vector<ignition::transport::ServicePublisher> publishers;
  if (!node_.ServiceInfo(service, publishers)) {
    SetStatus("Service " + service + " not found; is the simulation running?");
    return;
  }

  ignition::msgs::Pose req;
  req.set_name(model_);
  ignition::msgs::Set(req.mutable_position(), pose_.Pos());
  ignition::msgs::Set(req.mutable_orientation(), pose_.Rot());

  const std::string model = model_;
  std::function<void(const ignition::msgs::Boolean &, const bool)> on_reply =
    [this, model](const ignition::msgs::Boolean & _rep, const bool _result) {
      if (_result && _rep.data()) {
        SetStatus("Moved " + model + " back to the start pose");
      } else {
        SetStatus("Gazebo refused to move '" + model + "'; check the model name");
      }
    };
  const bool sent = node_.Request(service, req, on_reply);
  SetStatus(sent ? "Resetting..." : "Failed to call " + service);
}

}  // namespace wall_following_assignment

IGNITION_ADD_PLUGIN(wall_following_assignment::ResetPose, ignition::gui::Plugin)
