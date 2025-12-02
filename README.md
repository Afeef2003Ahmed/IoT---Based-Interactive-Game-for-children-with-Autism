# IoT-Based Interactive Motion Game for Children with Autism

An IoT-powered motion-interactive game designed to support children with autism by encouraging physical movement, gesture recognition, and real-time feedback through an engaging user interface.
This project integrates embedded systems, machine learning, and web technologies into a seamless therapy-support tool.

# 🚀 Project Overview

Children with autism often face challenges with physical engagement and social interaction. This project provides an interactive solution using motion-based gestures, allowing children to play simple games that respond to their movements in real time.

The system uses Nordic Thingy:52 for motion sensing, Edge Impulse for gesture classification, Raspberry Pi for IoT communication, and a Flask web app for visualization.

# 🎯 Key Features

1) Real-time gesture recognition (Wave, Jump, Circle, Rotate, Raise, Still)
2) On-device ML inference using Edge Impulse on Nordic Thingy:52
3) IoT pipeline with BLE + MQTT for seamless data flow
4) Interactive Flask + SocketIO UI for real-time game updates
5) Embedded-friendly int8 ML model optimized for Cortex-M4F

# 🛠️ System Architecture

<img width="1386" height="754" alt="image" src="https://github.com/user-attachments/assets/ca0e4550-ada0-4c6e-a35a-9de95b19ddfe" />

# 🧩 Tech Stack
# Hardware
1) Nordic Thingy:52 (nRF52832, Cortex-M4F)
2) Raspberry Pi 4
# Software & ML
1) Edge Impulse (Model training + deployment)
2) Python (BLE, MQTT handling)
3) Flask + SocketIO (UI)
4) HTML, CSS, JavaScript

# Protocols
1) BLE (Thingy52 → Raspberry Pi)
2) MQTT (Raspberry Pi → Web UI)
