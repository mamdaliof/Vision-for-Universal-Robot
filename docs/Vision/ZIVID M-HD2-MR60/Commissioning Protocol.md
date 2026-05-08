---
component: System Commissioning & Calibration
category: procedures
type: protocol
project: "[[Vision_Guided_Robotic_Cell]]"
tags:
  - calibration
  - ZIVID-M-HD2-MR60
  - safety
---

# Commissioning & Calibration Protocol

## 1. Physical Verification & Safety Checks
* **Mounting Height:** Ensure the Pickit M-HD2-MR60 is securely mounted in #to_be_deterdmined above the picking area. This ensures operations remain within the functional 300 - 1100 mm working distance [[attachments/pickit_datasheets-M-HD2-MR60.pdf|🔗]].
* **Safety Boundaries:** Before running active robot programs, explicitly define Cartesian safety zones (or virtual walls) in the robot controller. The camera volume must be restricted to prevent mechanical collisions due to unoptimized path planning. #how

## 2. Network Initialization & Component Discovery
* **Processor Boot:** Power on the Pickit Processor 3.0-A.
* **Web Interface Access:** Connect the commissioning PC to the `YOUR PC` port. Navigate to `http://192.168.66.1` in a supported browser.
* **Camera Verification:** If low-level diagnostics are needed, ping the internal Zivid sensor at IP `172.28.60.5` (Subnet Mask: `255.255.255.0`). You can also use the `ZividListCameras` CLI command from the local network to confirm the sensor is broadcasting.

## 3. Hand-Eye Calibration (Fixed/Stationary Mount) #later
* **Calibration Type:** Since the camera is stationary, you will perform a **Fixed Camera to Robot Base** calibration. This computes the mathematical transformation between the camera's optical frame and the robot's kinematic origin.
* **Execution:**
  1. Securely mount the Pickit calibration plate to the robot's end-effector (TCP).
  2. From the Pickit web interface, initiate the Hand-Eye calibration sequence.
  3. Manually jog the robot to present the calibration plate to the camera at various orientations and heights within its 570 x 460 mm field of view [[attachments/pickit_datasheets-M-HD2-MR60.pdf|🔗]].
  4. Allow the system to capture the points and compute the transformation matrix.
* **Validation:** Perform a test pick or point validation to ensure the calculated coordinates accurately translate to the robot's physical coordinate system.

## 4. Final Lock-Down
* Document the final calibration translation and rotation parameters for disaster recovery.
* Physically torque-mark and lock the camera mount to prevent accidental shifts; even millimeter-level bumps will necessitate a complete recalibration.