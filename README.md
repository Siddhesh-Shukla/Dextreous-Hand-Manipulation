# Dextreous-Hand-Manipulation

This repository contains an implementation of a robotic hand control policy using Proximal Policy Optimization (PPO) for in-hand manipulation tasks. The simulation is done using the MuJoCo physics engine and the model of the hand is based on the one used in the OpenAI Gym robotics environments. The goal is to reorient the object to a desired target configuration in hand with rewards given for achieving the goal and penalties for dropping the object. 

The state of the system is a 61-dimensional observation of the robot joints, object position, and desired goal.
