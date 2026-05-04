# Vision-Guided Robotic Picking System : Project Report



**Author:** Farhad Hoseyni
**Date:** May 2026
**Status:** 🟡 In Progress : Design Phase
**Audience:** Project Supervisor



***



## Project Overview



This project integrates a real-time vision system into a modular robotic cell powered by a Universal Robots (UR) collaborative arm. The goal is to enable flexible, precise, and reliable pick-and-place operations for battery components, starting with **cells and holders**, by removing the hard dependency on fixed, predefined part positions.



The system will detect part location and orientation in real time, validate their presence, and dynamically correct robot waypoints before each pick or place action. The architecture is designed to scale from a structured semi-known setup (Phase 1 MVP) toward full random bin-picking (Phase 2+).



> **Scope of this report:** Phase 1 MVP only. Subsequent phases are referenced for context and architectural continuity.



***



## Challenges



| # | Challenge | Impact | Phase |
|---|-----------|--------|-------|
| C1 | Locating and rigidly mounting the static camera on the Vention station | Miscalibration, vibration drift, FOV mismatch if poorly positioned | 1 |
| C2 | Slight X/Y/Yaw displacement of source holder in workspace | Missed picks without vision correction | 1 |
| C3 | Slight X/Y/Yaw displacement of destination holder | Misplaced parts without vision correction | 1 |
| C4 | Detecting cell position within the holder to validate occupancy | False picks or unsafe robot motion | 1 |
| C5 | Textureless, reflective surfaces (battery cells, plastic holders) | Unstable edge/contour detection | 1 |
| C6 | Hand-eye calibration accuracy and long-term stability | Systematic positional offset errors | 1 |
| C7 | Communicating vision offsets to UR Teach Pendant with minimal custom code | Integration complexity and cycle time | 1 |
| C8 | Scaling to strips and housings with different geometries | Increased pipeline complexity | 2 |
| C9 | Random 3D bin picking with unknown orientations and depth | Full 6-DoF pose estimation required | 2 |



***


## Open Decisions



| ID | Decision | Status | Notes |
|----|----------|--------|-------|
| D1 | Camera type: 2D RGB | ✅ Decided | Sufficient for X/Y/Yaw in Phase 1; RGBD not needed until Phase 3 bin picking |
| D2 | Camera mounting: static overhead on Vention frame | ✅ Decided | See rationale below |
| D3 | Vision algorithm for holder pose estimation | 🔴 Open | Candidates: Canny+contour+solvePnP, template matching, feature matching (ORB/SIFT) |
| D4 | Vision algorithm for cell occupancy validation | 🔴 Open | Candidates: blob detection, thresholding+contour, simple ROI intensity check |
| D5 | Communication protocol: Vision PC to UR | 🔴 Open | None |
| D6 | Lighting solution | 🔴 Open | None |
| D7 | Camera model and lens focal length | 🔴 Open | None |
| D8 | Camera mounting height and exact position on station frame | 🔴 Open | None |
| D9 | Part expansion beyond cells + holders | 🟡 Planned | For Phase 2 |



### D1 Rationale: 2D RGB Camera



A standard 2D RGB camera is sufficient for Phase 1 because the required correction is only **X, Y, and Yaw**, all recoverable from a single top-down image using known holder geometry. Depth (Z) and 3D tilt (pitch/roll) are not needed when the holder sits flat on a known surface. RGBD adds cost and complexity that only becomes necessary in Phase 3 when batteries are in unknown 3D orientations inside a bin.



### D2 Rationale: Static Overhead Camera



A fixed, top-down camera was selected for Phase 1 because:
- Image plane is parallel to the holder's top face, so X/Y measurement is direct with no perspective correction needed
- Yaw (Z-axis rotation) appears as clean in-plane rotation, giving the simplest angle extraction regardless of algorithm choice
- No arm occlusion: the UR arm approaches from the side, fully outside the camera's line of sight
- One-time calibration (T_cam to base) is stable and requires no runtime recomputation
- Mounting on top of the Vention station frame provides a natural, rigid, vibration-isolated position directly above the workspace with no additional gantry required



***



Before committing to algorithms in M2, a brief evaluation sprint is recommended during M1 using captured real images. The following candidates apply:



### D3: Holder Pose Estimation



> *(To be decided.)*



### D4: Cell Occupancy Validation



> *(To be decided.)*



### D5: Communication Protocol



> *(To be decided.)*



***



## System Architecture (Phase 1)



> *(To be defined after D3, D4, D5 decisions are finalised in M1.)*



***


## Milestones & Subtasks



### Milestone 1: Hardware Setup, Calibration and Proof-of-Concept Pick
> All physical and geometric groundwork is laid in this milestone. The camera is installed in its final position on the Vention frame, optics and lighting are locked in, and both intrinsic and hand-eye calibrations are completed and validated. A brief algorithm evaluation sprint run on real captured images closes the three remaining open decisions (D3, D4, D5). The milestone ends with a first end-to-end vision-guided pick: unpolished and not yet reliable, but sufficient to prove the full pipeline is connected and operational.


| Task | Description | Deliverable |
|------|-------------|-------------|
| T1.1 | Measure the workspace and calculate the FOV and lens focal length needed to cover both holders and all cell slots | Lens specification |
| T1.2 | Source and procure the camera and lens; physically confirm full workspace coverage before permanent mounting | Hardware confirmed |
| T1.3 | Identify the optimal mounting position on the Vention top frame and bolt the camera rigidly to prevent any shift | Camera installed |
| T1.4 | Evaluate lighting options and select the solution that produces stable, glare-free images of the holders and cells | Stable image quality |
| T1.5 | Install Python and OpenCV on the Vision PC and verify that the socket connection to the UR controller is active | Configured environment |
| T1.6 | Perform camera intrinsic calibration using a ChArUco board across 20 or more images to remove lens distortion | `camera_intrinsics.json` |
| T1.7 | Attach a calibration board to the robot TCP, collect 12 to 15 arm poses, and compute the camera-to-base transform | `hand_eye_calibration.json` |
| T1.8 | Send the robot to a vision-computed target point and measure the positional residual to confirm calibration accuracy | Accuracy report (target: < 1 mm) |
| T1.9 | Capture real images of holders and cells and run a focused evaluation sprint to select algorithms for D3, D4, and D5 | Algorithm and protocol decisions recorded |
| T1.10 | Build a minimal prototype pick using the selected algorithm and protocol to confirm the pipeline runs end-to-end | First vision-guided pick demonstrated |


**Exit criteria:** Camera rigidly mounted, full workspace in FOV. Reprojection error < 0.5 px. Hand-eye reach error < 1 mm. D3, D4, D5 decisions recorded. At least one successful vision-guided pick demonstrated (not yet reliable).



***



### Milestone 2: Full Vision Pipeline and Pick and Place Integration
> This milestone builds and validates the complete vision-to-motion pipeline. The holder pose estimation and cell occupancy algorithms are implemented, tested offline against ground truth, and then connected to the live robot. Pick and place motions are each validated in isolation under deliberate positional offsets before being combined into a full cycle. By the end of this milestone the system can reliably complete a vision-guided pick-and-place operation, with the robot halting safely whenever the cell occupancy check fails.


| Task | Description | Deliverable |
|------|-------------|-------------|
| T2.1 | Project the STL geometry of both holders into 2D and extract reference keypoints that will anchor the pose estimation | Keypoint reference set |
| T2.2 | Implement the holder pose estimation algorithm selected in D3 to recover delta X, delta Y, and delta Yaw from each image | Pose estimation module |
| T2.3 | Test source holder detection across 20 placements with deliberate offsets and confirm accuracy is within 0.5 mm and 0.5 degrees | Source holder validation report |
| T2.4 | Repeat the same detection and validation process for the destination holder using its own STL reference | Destination holder validation report |
| T2.5 | Derive the expected cell region of interest for each slot directly from the holder STL dimensions | ROI mask per slot |
| T2.6 | Implement the cell occupancy algorithm selected in D4 and compute how far the detected centroid deviates from the expected slot center | Cell occupancy module |
| T2.7 | Determine the deviation threshold that triggers a cell fault, implement the cell_ok flag, and verify the fault-stop response | Threshold config and test report |
| T2.8 | Implement the communication protocol selected in D5 and wrap the full detection pipeline into a single callable function | `vision_pipeline.py` and comms module |
| T2.9 | Teach the nominal pick waypoints on the Teach Pendant and add the socket receive block and the cell_ok halt condition | TP pick program |
| T2.10 | Apply pose_add with the source offset to the nominal pick waypoint and confirm the robot moves to the corrected position | Corrected pick motion |
| T2.11 | Run 30 pick cycles with deliberate source holder offsets of up to 10 mm and 5 degrees and log the success rate | Pick validation report |
| T2.12 | Teach the nominal place waypoints and apply pose_add with the destination offset to correct the place position | Corrected place motion |
| T2.13 | Run 30 place cycles with deliberate destination holder offsets and log the success rate | Place validation report |
| T2.14 | Run a 50-cycle end-to-end pick-and-place test with offsets applied to both holders and log success rate and any fault types | End-to-end validation report |


**Exit criteria:** Holder pose within ±0.5 mm / ±0.5° across 20 test cases per holder. Cell occupancy correct in 100% of test cases. Pipeline latency < 500 ms per frame. ≥ 95% pick and place success over respective 30-cycle tests. End-to-end ≥ 95% over 50 cycles. `cell_ok = 0` triggers a clean halt in all fault cases.



***



### Milestone 3: Pick Robustness and Stress Testing
> A 95% success rate under controlled lab offsets is a promising result, but not a deployable one. This milestone pushes the pick step beyond the comfortable test envelope to expose the remaining failure modes, whether they originate in vision instability, timing, grasp mechanics, or edge-case geometry. Each identified failure mode is addressed systematically until the pick reaches a reliability level suitable for continuous production use. Place robustness is covered in the endurance test of M4.


| Task | Description | Deliverable |
|------|-------------|-------------|
| T3.1 | Review the M2 end-to-end test logs to categorise pick failures by root cause: vision error, grasp failure, or timing issue | Failure mode analysis |
| T3.2 | Adjust the D3 algorithm parameters and detection thresholds to maintain stable detection across realistic lighting variation | Tuned vision config |
| T3.3 | Implement a retry mechanism that re-captures the image when the detection confidence falls below a defined threshold | Retry module |
| T3.4 | Run pick tests across an extended offset envelope of 15 mm and 7 degrees to verify behaviour at the boundary of the workspace | Extended pick stress report |
| T3.5 | Trigger all defined cell_ok fault scenarios including missing cell, displaced cell, and wrong orientation, and confirm clean halts | Fault scenario test report |
| T3.6 | Measure the full cycle time from image capture to completed pick motion and confirm it meets the throughput requirement | Cycle time report |


**Exit criteria:** Pick success ≥ 98% over 100 cycles covering the full extended offset envelope. All `cell_ok` fault scenarios produce a clean halt with no unsafe robot motion. Cycle time within agreed throughput target.



***



### Milestone 4: Endurance, Fault Hardening and Documentation
> With a validated and stress-tested pick-and-place pipeline in hand, this milestone shifts focus to long-term operational reliability. Continuous operation uncovers failure modes such as hardware dropouts, calibration drift, and edge-case software states that short validation cycles cannot catch. Every fault path is handled explicitly, and the system is formally documented so that it can be maintained, re-calibrated, and handed over without relying on undocumented knowledge. Phase 2 planning is prepared in parallel.


| Task | Description | Deliverable |
|------|-------------|-------------|
| T4.1 | Implement handlers for all known fault conditions: camera disconnection, socket timeout, detection failure, and holder not found | Fault handling module |
| T4.2 | Run a 200-cycle endurance test under normal operating conditions and record fault rate, fault types, and any calibration drift | Endurance test report |
| T4.3 | Write a re-calibration procedure that specifies when recalibration is needed, how to perform it, and how to verify the result | Re-calibration SOP |
| T4.4 | Produce an operator manual covering the system startup sequence, fault recovery steps, and daily pre-run checks | Operations manual |
| T4.5 | Draft a Phase 2 scope document covering the addition of strips and housings, the RGBD camera upgrade, and bin picking architecture | Phase 2 planning document |


**Exit criteria:** < 2% fault rate over 200 cycles. All faults handled without crash or unsafe robot motion. Documentation reviewed and accepted by supervisor.



***



## Project Agenda and Follow-Up



| Milestone | Key Deliverable | Target Date | Status | Owner |
|-----------|----------------|-------------|--------|-------|
| **M1** Hardware Setup and Calibration | Camera mounted, calibrated, D3/D4/D5 decided, basic pick demonstrated | __________ | 🔴 Not started | Farhad |
| **M2** Vision Pipeline and Pick and Place | Holder pose and cell validated, pick and place above 95%, end-to-end passed | __________ | 🔴 Not started | Farhad |
| **M3** Pick Robustness | Pick above 98% over 100 cycles, all fault scenarios clean, cycle time confirmed | __________ | 🔴 Not started | Farhad |
| **M4** Endurance and Docs | 200-cycle endurance passed, fault handling complete, manuals accepted | __________ | 🔴 Not started | Farhad |



***



## Phase Roadmap



| Phase | Scope | Vision Method | Camera |
|-------|-------|--------------|--------|
| **Phase 1 MVP** *(current)* | Cells and holders | TBD after M1 evaluation (D3/D4) | 2D RGB, static overhead |
| **Phase 2** | Strips and housings added | Extended pipeline per part geometry | 2D RGB (same setup) |
| **Phase 3** | Random bin picking | ICP / LINEMOD, 6-DoF pose estimation | RGBD, eye-in-hand option |



***



## Key Risks



| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Camera position on frame gives insufficient FOV or edge distortion | High (pre-M1) | Calculate FOV analytically before mounting; validate with test images in T1.1 to T1.3 |
| Specular reflections degrade contour/blob detection | High | Finalise lighting in T1.4 before the algorithm evaluation sprint in T1.9 |
| Chosen algorithm (D3) fails on textureless holder surfaces | Medium | Evaluate LINEMOD as fallback during T1.9 |
| Camera mount vibration shifts calibration over time | Medium | Rigid bolt mount; re-calibration SOP defined in M4 |
| solvePnP degeneracy if holder lacks sufficient distinct keypoints | Medium | Pre-validate keypoint set from STL files in T2.1 before M2 begins |
| Protocol latency adds unacceptable cycle time overhead | Low | Benchmark during T2.14 end-to-end test and T3.6 cycle time report |
| Phase 1 scope creep toward strips/housings | Low | Milestone exit criteria enforce scope boundaries |



***

