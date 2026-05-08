---
component: Pickit Vision System Network
category: architecture
type: network_topology
project: "[[Vision_Guided_Robotic_Cell]]"
tags:
  - configuration
  - pickit-processor
  - network-topology
  - ZIVID-M-HD2-MR60
---
# System Architecture & Network Topology

## 1. Current Local Network State
The system is currently configured on a localized, standalone network to ensure isolated and reliable traffic between the vision components.

* **Pickit Web Interface:** The external PC is connected to the Ethernet port labeled `YOUR PC` on the Pickit processor. The PC is dynamically assigned an IP address by the Pickit system, and the primary web interface is accessed via `http://192.168.66.1`.
* **Camera Data Connection:** The Pickit M-HD2-MR60 camera physically connects to the Pickit processor utilizing an M12-8 Ethernet connection (TCP/IP over Ethernet) for high-bandwidth point cloud transmission [[attachments/pickit_datasheets-M-HD2-MR60.pdf|🔗]]. 
* **Zivid Camera Backend:** Following a factory reset, the camera's internal Zivid sensor defaults to an IP address of `172.28.60.5` with a Subnet Mask of `255.255.255.0`. This IP is accessible via both the Pickit and Zivid applications.
* **Diagnostic Tools:** The camera's direct network presence can be verified directly from the PC LAN using the `ZividListCameras` command-line utility.

## 2. Future Integration (Robot Controller)
* **Robot Connection:** The robot controller is planned to interface with the Pickit processor via the `ROBOT` Ethernet port. Specific IP configurations, subnetting, and socket connection details are pending confirmation of the robot's make, model, and controller version.