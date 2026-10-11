#!/usr/bin/env python3
"""
RAN-01 demo: plays a smooth, looping choreography on the arm.

Publishes sensor_msgs/JointState on /joint_states, so robot_state_publisher
and RViz show the motion. Moves between keyframes with smooth easing.

Run with:  roslaunch workspace_experiments demo.launch
"""
import math

import rospy
from sensor_msgs.msg import JointState

JOINTS = ["joint1", "joint2", "joint3", "joint4", "joint5", "joint6"]

# (name, [joint1 .. joint6] in radians, seconds to move there, seconds to hold)
KEYFRAMES = [
    ("home",          [ 0.00,  0.00,  0.00,  0.00,  0.00,  0.00], 2.0, 0.6),
    ("bow",           [ 0.00,  0.70,  1.40,  0.00,  0.90,  0.00], 2.0, 0.4),
    ("reach A",       [ 0.785, 1.054, 1.286, 0.00,  0.00,  0.00], 2.2, 0.8),
    ("reach B",       [ 1.571, 0.007, 1.666, 0.00,  0.00,  0.00], 2.2, 0.8),
    ("wrist twist",   [ 1.571, 0.007, 1.666, 1.60, -0.90,  3.14], 1.8, 0.3),
    ("swing left",    [-1.20,  0.50,  1.10, -1.20,  0.80, -3.14], 2.6, 0.4),
    ("look up",       [-0.40, -0.40,  0.90,  0.00, -1.20,  0.00], 2.0, 0.4),
    ("pick low",      [ 0.60,  0.70,  1.55,  0.00,  0.85,  1.57], 2.4, 0.5),
    ("show logo",     [ 0.00,  0.25,  0.30,  0.00,  0.00,  0.00], 2.2, 1.0),
]


def ease(t):
    """Smooth start and stop (cosine easing), t in [0, 1]."""
    return 0.5 - 0.5 * math.cos(math.pi * t)


def main():
    rospy.init_node("ran01_demo_motion")
    pub = rospy.Publisher("/joint_states", JointState, queue_size=10)
    rate_hz = rospy.get_param("~rate", 30.0)
    speed = rospy.get_param("~speed", 1.0)  # >1 faster, <1 slower
    rate = rospy.Rate(rate_hz)

    msg = JointState()
    msg.name = JOINTS

    def publish(positions):
        msg.header.stamp = rospy.Time.now()
        msg.position = positions
        pub.publish(msg)

    rospy.loginfo("RAN-01 demo running: %d keyframes, looping. Ctrl+C to stop.", len(KEYFRAMES))
    current = list(KEYFRAMES[0][1])

    while not rospy.is_shutdown():
        for name, target, move_s, hold_s in KEYFRAMES:
            rospy.loginfo("-> %s", name)
            start = list(current)
            move_s, hold_s = move_s / speed, hold_s / speed

            # move with easing
            t0 = rospy.Time.now()
            while not rospy.is_shutdown():
                t = (rospy.Time.now() - t0).to_sec() / move_s
                if t >= 1.0:
                    break
                s = ease(t)
                publish([a + (b - a) * s for a, b in zip(start, target)])
                rate.sleep()
            current = list(target)

            # hold the pose
            t0 = rospy.Time.now()
            while not rospy.is_shutdown() and (rospy.Time.now() - t0).to_sec() < hold_s:
                publish(current)
                rate.sleep()


if __name__ == "__main__":
    try:
        main()
    except rospy.ROSInterruptException:
        pass
