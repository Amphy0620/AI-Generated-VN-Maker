import cv2
import numpy as np
from scipy import ndimage
import sys
import os

def trimWhitespace(imgPath):
    if not os.path.exists(imgPath):
        print(f"Can't find image at {os.path.abspath(imgPath)}")
        return

    # Load the image and convert to RGBA
    img = cv2.imread(imgPath, cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f"Failed to load image at {os.path.abspath(imgPath)}")
        return

    if img.shape[2] != 4:
        print("Image is not in RGBA format.")
        return

    # Define the threshold for considering a pixel as "sufficiently white"
    white_threshold = 240

    # Create a mask for sufficiently white pixels
    white_mask = (img[:, :, :3] > white_threshold).all(axis=2) & (img[:, :, 3] > 0)

    # Create a transparency mask initialized with False (all opaque)
    transparency_mask = np.zeros(white_mask.shape, dtype=bool)

    # Process edges first
    transparency_mask[0, :] = white_mask[0, :]
    transparency_mask[-1, :] = white_mask[-1, :]
    transparency_mask[:, 0] = white_mask[:, 0]
    transparency_mask[:, -1] = white_mask[:, -1]

    # Create a structure to check 4-connectivity (N, S, E, W neighbors)
    structure = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=bool)

    # Iterate until no new pixels are made transparent
    while True:
        new_transparency_mask = white_mask & ndimage.binary_dilation(transparency_mask, structure=structure)
        if np.array_equal(transparency_mask, new_transparency_mask):
            break
        transparency_mask = new_transparency_mask

    # Apply the transparency mask to the image
    img[transparency_mask, 3] = 0

    # Save the modified image
    outputPath = imgPath.replace(".png", "_trimmed.png")
    cv2.imwrite(outputPath, img)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        imgPath = sys.argv[1]
        trimWhitespace(imgPath)
    else:
        print("Please provide the image path as a command-line argument.")

