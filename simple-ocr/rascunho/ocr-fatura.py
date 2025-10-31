import pytesseract
import argparse
import cv2
from pdf2image import convert_from_path
import os

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True,
    help="path to input PDF or image file to be OCR'd")
ap.add_argument("-o", "--output", default="output_images",
    help="directory to save intermediate JPEG images")
args = vars(ap.parse_args())

input_path = args["input"]
output_dir = args["output"]

os.makedirs(output_dir, exist_ok=True)
text = ""

if input_path.lower().endswith(".pdf"):
    # Convert PDF to images (list of PIL Image objects)
    images = convert_from_path(input_path)

    for i, page in enumerate(images):
        # Define JPEG output path
        image_path = os.path.join(output_dir, f"page_{i+1}.jpg")

        # Save as JPEG
        page.save(image_path, "JPEG")
        print(f"[INFO] Saved: {image_path}")

        # Load saved image with OpenCV
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Perform OCR
        text += f"\n--- Page {i+1} ---\n"
        text += pytesseract.image_to_string(image)

else:
    # Handle single image input
    image = cv2.imread(input_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(image)

print(text)
