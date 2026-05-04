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

if __name__ == "__main__":
    # Get absolute path to Data folder relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(script_dir, "Data", "image_1.jpg")
    
    try:
        img = load_image(img_path)
        processed = preprocess_image(img)
        hull, mask = find_board_contour(processed)
        
        if hull is not None:
            print(f"Found hull with {len(hull)} points.")
        else:
            print("No contours found.")
            
    except Exception as e:
        print(f"Error: {e}")
