cmake_minimum_required(VERSION 3.8)
project(wall_following_assignment)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(std_msgs REQUIRED)

add_executable(wall_follower_node src/wall_follower_node.cpp)
target_include_directories(wall_follower_node PRIVATE include)
ament_target_dependencies(wall_follower_node rclcpp sensor_msgs geometry_msgs std_msgs)
install(TARGETS wall_follower_node DESTINATION lib/${PROJECT_NAME})

# Gazebo GUI plugin: the "Reset pose to start" button docked under Teleop.
# Built against Ignition Fortress (gui6/transport11/msgs8), which is what
# clearpath_simulator on Humble runs. The library must be named
# lib<filename>.so for the <plugin filename="ResetPose"> element in the GUI
# config, and launch/gazebo_world.launch.py points IGN_GUI_PLUGIN_PATH at
# the install directory below.
find_package(ignition-gui6 REQUIRED)
find_package(ignition-transport11 REQUIRED)
find_package(ignition-msgs8 REQUIRED)
find_package(ignition-plugin1 REQUIRED COMPONENTS register)
find_package(Qt5 REQUIRED COMPONENTS Core Qml Quick QuickControls2)
if(POLICY CMP0100)
  cmake_policy(SET CMP0100 NEW)  # let AUTOMOC process the .hh header
endif()
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
add_library(ResetPose SHARED
  gui_plugins/ResetPose.cc
  gui_plugins/ResetPose.hh
  gui_plugins/ResetPose.qrc)
target_compile_features(ResetPose PRIVATE cxx_std_17)
target_link_libraries(ResetPose PRIVATE
  ignition-gui6::ignition-gui6
  ignition-transport11::ignition-transport11
  ignition-msgs8::ignition-msgs8
  ignition-plugin1::register
  Qt5::Core Qt5::Qml Qt5::Quick Qt5::QuickControls2)
install(TARGETS ResetPose LIBRARY DESTINATION lib/${PROJECT_NAME}/gui_plugins)

install(DIRECTORY include/ DESTINATION include)

install(DIRECTORY config DESTINATION share/${PROJECT_NAME})

install(DIRECTORY worlds DESTINATION share/${PROJECT_NAME})

install(DIRECTORY launch DESTINATION share/${PROJECT_NAME})

# Also install the world SDF files directly under the package's bare
# share/ prefix (not share/${PROJECT_NAME}/worlds). clearpath_gz's
# gz_sim.launch.py builds IGN_GAZEBO_RESOURCE_PATH from
# `<AMENT_PREFIX_PATH entry>/share` for every sourced package (see
# /opt/ros/humble/share/clearpath_gz/launch/gz_sim.launch.py), and Gazebo
# resolves the `world` launch argument (with .sdf appended) as a bare
# filename against that resource path. Our own package's AMENT_PREFIX_PATH
# entry is this package's install prefix, so `<prefix>/share` is searched
# but `<prefix>/share/${PROJECT_NAME}/worlds` is not -- hence this second
# copy, purely so Gazebo can find "walls_one_sided.sdf" etc. by name.
file(GLOB WORLD_SDF_FILES worlds/*.sdf)
install(FILES ${WORLD_SDF_FILES} DESTINATION share)

install(PROGRAMS scripts/wall_follower.py DESTINATION lib/${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_cmake_pytest REQUIRED)
  ament_add_pytest_test(test_pid test/test_pid.py)
  ament_add_pytest_test(test_gui_config test/test_gui_config.py)
endif()

ament_package()
