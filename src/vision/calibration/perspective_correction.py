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

if __name__ == "__main__":
    # Get absolute path to Data folder relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(script_dir, "Data", "image_1.jpg")
    
    try:
        img = load_image(img_path)
        processed = preprocess_image(img)
        print("Preprocessing successful. Image shape:", img.shape)
    except Exception as e:
        print(f"Error: {e}")
