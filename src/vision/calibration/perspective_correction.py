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
    # Approximate polygon
    epsilon = 0.02 * cv2.arcLength(hull, True)
    approx = cv2.approxPolyDP(hull, epsilon, True)
    
    if len(approx) == 4:
        return approx.reshape(4, 2)
    else:
        # Fallback: find corners based on bounding box extremes
        rect = cv2.minAreaRect(hull)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        return box

def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    pts = np.array(pts, dtype="float32")
    
    # top-left point has smallest sum, bottom-right has largest sum
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    
    # top-right point has smallest difference, bottom-left has largest difference
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    
    return rect

def warp_perspective(img, ordered_corners):
    (tl, tr, br, bl) = ordered_corners
    
    # Compute the width of the new image
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    
    # Compute the height of the new image
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    
    # Create target points based on max dimensions
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]
    ], dtype="float32")
    
    # Calculate the perspective transform matrix and warp
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
