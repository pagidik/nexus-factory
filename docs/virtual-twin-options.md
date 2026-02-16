# Virtual Twin Options For Manufacturing POC

Last validated: February 16, 2026

This list focuses on options you can use quickly for a manufacturing assistant proof of concept.

## 1) ARIAC (NIST) with ROS 2 + Gazebo
- Type: Open simulation environment
- Good for: Industrial robotics workflows, competition-style task simulation, ROS-native integration
- Notes: Official docs target ROS 2 Iron on Ubuntu 22.04.
- Link: https://pages.nist.gov/ARIAC_docs/en/2024.1.0/installation.html

## 2) IFRA ConveyorBelt (ROS 2 Gazebo Plugin)
- Type: Open-source ROS 2 package
- Good for: Fast conveyor-based virtual line setup with distance sensor/camera simulation
- Notes: Includes service-based speed and control commands for conveyor behavior.
- Link: https://github.com/IFRA-Cranfield/IFRA_ConveyorBelt

## 3) OpenFactoryTwin
- Type: Open-source framework
- Good for: Industry 4.0 digital twin experiments across production and logistics
- Notes: Supports demonstrator use cases (including warehouse-style flows) and cloud deployment.
- Link: https://github.com/OpenFactoryTwin/ofact

## 4) AnyLogic Demo Models + AnyLogic Cloud
- Type: Commercial tool with demo model library
- Good for: Quickly sharing and running manufacturing simulations in a browser
- Notes: Demo models can be opened in AnyLogic; cloud-hosted demos are available in AnyLogic Cloud.
- Link: https://anylogic.help/anylogic/introduction/demo-models.html

## 5) Factory I/O
- Type: Commercial 3D factory simulation software
- Good for: PLC/automation-style digital factory scenes and controls testing
- Notes: Official site advertises a 30-day free trial.
- Link: https://factoryio.com/

## Recommended Sequence
1. Start with `ARIAC` or `IFRA ConveyorBelt` for open ROS-aligned setup.
2. Connect your POC parser to simulator outputs and generate bottleneck alerts.
3. Add ROS sensor streams for one pilot flow.
4. Move to real line signals only after interview validation and baseline metrics.
