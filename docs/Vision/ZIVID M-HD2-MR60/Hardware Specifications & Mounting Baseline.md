---
component: Pickit M-HD2-MR60 & Processor 3.0-A
category: vision_system
vendor: Pickit
type: hardware_specification
project: "[[Vision_Guided_Robotic_Cell]]"
tags:
  - ZIVID-M-HD2-MR60
  - configuration
  - pickit-processor
---
# Hardware Specifications & Mounting Baseline

## 1. Camera Specifications: Pickit M-HD2-MR60
* **Technology:** Structured light [[attachments/pickit_datasheets-M-HD2-MR60.pdf|🔗]].
* **Resolution:** 2448 x 2048 (5.0 MPx) [[attachments/pickit_datasheets-M-HD2-MR60.pdf|🔗]].
* **Working Distance:** 300 - 1100 mm [[attachments/pickit_datasheets-M-HD2-MR60.pdf|🔗]].
* **Field of View:** 570 x 460 mm @600mm [[attachments/pickit_datasheets-M-HD2-MR60.pdf|🔗]].
* **Durability:** IP65 rating, 5G Random / 15G Shock vibrations [[attachments/pickit_datasheets-M-HD2-MR60.pdf|🔗]].
* **Weight:** 1000 g [[attachments/pickit_datasheets-M-HD2-MR60.pdf|🔗]].

## 2. Processor Specifications: Pickit 3.0-A
* **Processor:** 6 cores (12 threads) at 3.2 Ghz [[attachments/pickit_datasheet-Processor_3.0A.pdf|🔗]].
* **Power Profile:** 40W (Idle) up to 90W (Heavy processing) [[attachments/pickit_datasheet-Processor_3.0A.pdf|🔗]].
* **Input Power:** 12 V DC (10 A) [[attachments/pickit_datasheet-Processor_3.0A.pdf|🔗]].

## 3. Mounting Baseline & Safety

+ **Configuration:** Stationary mount, positioned ___TO BE MEASURED___above the target area. This is highly optimal as it falls securely within the camera's 300 - 1100 mm working distance.
+ **Safety Consideration:** Due to the known risk of robot collisions, it is strongly advised to implement physical crash guards around the camera or establish strict software-level Cartesian safety zones. While the camera can handle 15G shocks [[attachments/pickit_datasheets-M-HD2-MR60.pdf|🔗]], collisions risk altering extrinsic calibration.


