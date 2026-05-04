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

if __name__ == "__main__":
    # Get absolute path to Data folder relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(script_dir, "Data", "image_1.jpg")
    
    try:
        img = load_image(img_path)
        processed = preprocess_image(img)
        hull, mask = find_board_contour(processed)
        
        if hull is not None:
            corners = extract_corners(hull)
            ordered_corners = order_points(corners)
            print("Ordered corners:\n", ordered_corners)
        else:
            print("No contours found.")
            
    except Exception as e:
        print(f"Error: {e}")
