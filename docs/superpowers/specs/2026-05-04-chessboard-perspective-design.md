# Spec: Chessboard Perspective Correction

## Goal
Implement a generic perspective correction tool that detects a rectangular surface (like a chessboard) against a dark background and warps it to a top-down view.

## Implementation Details

### 1. Image Loading
- Load image from `src/vision/calibration/Data/`.
- Process one image (e.g., `image_1.jpg`) as a demonstration.

### 2. Detection Pipeline
- **Grayscale Conversion**: Simplify image data.
- **Noise Reduction**: Apply Gaussian Blur.
- **Thresholding**: Use Adaptive Thresholding to separate the light board from the dark background.
- **Contour Extraction**: Find the largest contour by area.
- **Convex Hull**: Apply `cv2.convexHull` to the largest contour to ensure a clean exterior boundary.
- **Corner Extraction**: Use `cv2.approxPolyDP` on the hull or find extreme points to isolate exactly 4 corners.
- **Corner Sorting**: Ensure corners are consistently ordered: [Top-Left, Top-Right, Bottom-Right, Bottom-Left].

### 3. Transformation
- **Homography**: Calculate `M = cv2.getPerspectiveTransform(src_pts, dst_pts)`.
- **Warping**: Apply `cv2.warpPerspective` to obtain the top-down view.

### 4. Visualization
- Use Matplotlib to show a 2x2 grid:
  - (0,0): Original Image with detected corners.
  - (0,1): Thresholded Binary Mask.
  - (1,0): Convex Hull visualization.
  - (1,1): Final Warped Perspective.

## Success Criteria
- Successfully identifies the 4 corners of the board in at least one sample image.
- Produces a square/rectangular top-down view of the board.
- The pipeline is general and does not use `findChessboardCorners`.
