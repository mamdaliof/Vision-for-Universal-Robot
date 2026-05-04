import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

def load_image(image_path):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at {image_path}")
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Failed to load image at {image_path}")
    return img

def clean_background(img):
    """
    Isolates the largest dark object (the surface) by creating a mask.
    Sets everything outside this object to black.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Threshold to find dark regions (inverted binary)
    # Background is likely light, surface is dark
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return img
        
    # Find the largest contour (the dark surface)
    largest_contour = max(contours, key=cv2.contourArea)
    
    # Create a black mask of the same size as the image
    mask = np.zeros(gray.shape, dtype=np.uint8)
    
    # Draw the largest contour filled with white (255) on the mask
    cv2.drawContours(mask, [largest_contour], -1, 255, thickness=cv2.FILLED)
    
    # Apply the mask to the original image
    cleaned_img = cv2.bitwise_and(img, img, mask=mask)
    
    return cleaned_img

def preprocess_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    return blurred

def find_board_contour(blurred_img):
    # Use Otsu's thresholding for bimodal distribution (light board, dark background)
    _, thresh = cv2.threshold(blurred_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return None, thresh
        
    # Find largest contour by area
    largest_contour = max(contours, key=cv2.contourArea)
    
    # Apply Convex Hull
    hull = cv2.convexHull(largest_contour)
    
    return hull, thresh

def extract_corners(hull):
    def unique_points(pts, eps=1.0):
        unique = []
        for p in pts:
            if not unique:
                unique.append(p)
            else:
                dists = [np.linalg.norm(p - q) for q in unique]
                if all(d > eps for d in dists):
                    unique.append(p)
        return np.array(unique, dtype=np.float32)

    def reduce_to_quad(pts):
        """
        Iteratively remove the point that is most collinear with its two
        neighbors (i.e., contributes the smallest cross-product area),
        until we have exactly 4 points.
        """
        pts = list(pts)
        while len(pts) > 4:
            min_area = float('inf')
            min_idx = -1
            n = len(pts)
            for i in range(n):
                # Triangle formed by previous, current, next point
                prev_p = np.array(pts[(i - 1) % n])
                curr_p = np.array(pts[i])
                next_p = np.array(pts[(i + 1) % n])
                # Area of triangle via cross product
                area = abs(np.cross(curr_p - prev_p, next_p - prev_p)) / 2.0
                if area < min_area:
                    min_area = area
                    min_idx = i
            pts.pop(min_idx)
        return np.array(pts, dtype=np.float32)

    # Approximate polygon
    epsilon = 0.02 * cv2.arcLength(hull, True)
    approx = cv2.approxPolyDP(hull, epsilon, True)  # shape (N,1,2)

    # Flatten to (N,2) and float32
    approx = approx.reshape(-1, 2).astype("float32")

    # Remove near-duplicate points
    approx_unique = unique_points(approx, eps=2.0)

    # Case 1: exactly 4 -> use them directly
    if len(approx_unique) == 4:
        return approx_unique

    # Case 2: more than 4 (e.g. pentagon) -> reduce by removing the most
    # collinear vertex until we have 4
    if len(approx_unique) > 4:
        return reduce_to_quad(approx_unique)

    # Case 3: fewer than 4 -> fall back to minAreaRect
    rect = cv2.minAreaRect(hull)
    box = cv2.boxPoints(rect)
    box_unique = unique_points(box, eps=2.0)

    if len(box_unique) == 4:
        return box_unique

    return None

def order_points(pts):
    pts = np.array(pts, dtype="float32")
    if pts.shape[0] != 4:
        raise ValueError(f"order_points expects 4 points, got {pts.shape[0]}")

    # Compute centroid
    cx, cy = pts[:, 0].mean(), pts[:, 1].mean()

    # Sort by angle from centroid (atan2 gives clockwise order starting from top-right)
    def angle_from_centroid(p):
        return np.arctan2(p[1] - cy, p[0] - cx)

    sorted_pts = sorted(pts, key=angle_from_centroid)
    sorted_pts = np.array(sorted_pts, dtype="float32")

    # sorted_pts are in clockwise order starting from the point most to the right
    # Re-arrange to: top-left, top-right, bottom-right, bottom-left
    # Find the top-left: point with minimum sum (x+y)
    s = sorted_pts.sum(axis=1)
    tl_idx = np.argmin(s)

    # Rotate the array so top-left is first
    ordered = np.roll(sorted_pts, -tl_idx, axis=0)

    return ordered  # [top-left, top-right, bottom-right, bottom-left]


def warp_perspective(
    img,
    ordered_corners,
    mode="static",
    width_mm=29*10,
    height_mm=20*10,
    px_per_mm=2.0
):
    (tl, tr, br, bl) = ordered_corners

    if mode == "static":
        # Measure the projected width and height of the detected quad
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        projected_width = (widthA + widthB) / 2.0

        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        projected_height = (heightA + heightB) / 2.0

        # Assign long side as width, short side as height
        long_mm  = max(width_mm, height_mm)
        short_mm = min(width_mm, height_mm)

        if projected_width >= projected_height:
            # Board is landscape in image -> width_mm stays as width
            target_width  = int(long_mm  * px_per_mm)
            target_height = int(short_mm * px_per_mm)
        else:
            # Board is portrait in image -> swap so long side is still width
            target_width  = int(short_mm * px_per_mm)
            target_height = int(long_mm  * px_per_mm)

        dst = np.array([
            [0, 0],
            [target_width - 1, 0],
            [target_width - 1, target_height - 1],
            [0, target_height - 1]
        ], dtype="float32")

        M = cv2.getPerspectiveTransform(ordered_corners, dst)
        warped = cv2.warpPerspective(img, M, (target_width, target_height))
        return warped

    else:
        # --- DYNAMIC mode: unchanged ---
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))

        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))

        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]
        ], dtype="float32")

        M = cv2.getPerspectiveTransform(ordered_corners, dst)
        warped = cv2.warpPerspective(img, M, (maxWidth, maxHeight))
        return warped

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "Data")
    results_dir = os.path.join(script_dir, "results")
    
    # Create results folder if it doesn't exist
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
        print(f"Created directory: {results_dir}")

    image_extensions = (".jpg", ".jpeg", ".png", ".bmp")
    image_files = [f for f in os.listdir(data_dir) if f.lower().endswith(image_extensions)]
    
    if not image_files:
        print(f"No images found in {data_dir}")
    else:
        print(f"Processing {len(image_files)} images...")

    for filename in image_files:
        img_path = os.path.join(data_dir, filename)
        print(f"Processing {filename}...", end=" ")
        
        try:
            img = load_image(img_path)
            img = clean_background(img)
            processed = preprocess_image(img)
            hull, mask = find_board_contour(processed)
            
            if hull is not None:
                corners = extract_corners(hull)
                ordered_corners = order_points(corners)
                warped_img = warp_perspective(img, ordered_corners)
                
                # Prepare visualization
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                warped_rgb = cv2.cvtColor(warped_img, cv2.COLOR_BGR2RGB)
                
                annotated_img = img_rgb.copy()
                cv2.drawContours(annotated_img, [hull], -1, (0, 255, 0), 2)
                for point in ordered_corners:
                    x, y = int(point[0]), int(point[1])
                    cv2.circle(annotated_img, (x, y), 10, (255, 0, 0), -1)
                
                fig, axs = plt.subplots(2, 2, figsize=(12, 10))
                axs[0, 0].imshow(annotated_img)
                axs[0, 0].set_title('Original with Hull & Corners')
                axs[0, 0].axis('off')
                
                axs[0, 1].imshow(mask, cmap='gray')
                axs[0, 1].set_title('Thresholded Mask')
                axs[0, 1].axis('off')
                
                hull_canvas = np.zeros_like(mask)
                cv2.drawContours(hull_canvas, [hull], -1, 255, thickness=cv2.FILLED)
                axs[1, 0].imshow(hull_canvas, cmap='gray')
                axs[1, 0].set_title('Convex Hull Region')
                axs[1, 0].axis('off')
                
                axs[1, 1].imshow(warped_rgb)
                axs[1, 1].set_title('Warped Top-Down View')
                axs[1, 1].axis('off')
                
                plt.tight_layout()
                output_name = f"result_{os.path.splitext(filename)[0]}.png"
                output_path = os.path.join(results_dir, output_name)
                plt.savefig(output_path)
                plt.close(fig) # Close to free memory
                print(f"Saved to {output_name}")
            else:
                print("No contours found.")
                
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    print("\nBatch processing complete.")
