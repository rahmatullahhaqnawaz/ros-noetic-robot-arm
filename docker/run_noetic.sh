#!/usr/bin/env bash
# Start a ROS Noetic container with GUI support (RViz, sliders).
# First run creates the container "noetic"; later runs reopen it.
set -e

xhost +local:docker > /dev/null

if docker ps -a --format '{{.Names}}' | grep -qx noetic; then
  docker start -ai noetic
else
  docker run -it --net=host \
    -e DISPLAY="$DISPLAY" \
    -e LIBGL_ALWAYS_SOFTWARE=1 \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v "$HOME/catkin_ws":/root/catkin_ws \
    --name noetic \
    osrf/ros:noetic-desktop-full bash
fi
