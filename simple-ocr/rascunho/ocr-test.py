import cv2
import pytesseract


# Load image
image = cv2.imread("output_images/page_3.jpg")

# Convert to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Increase contrast and reduce background noise
gray = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)

# Apply adaptive threshold to get crisp black/white text
thresh = cv2.adaptiveThreshold(
    gray, 255,
    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    cv2.THRESH_BINARY,
    35, 11
)

# Optional: small dilation + erosion to strengthen text lines
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
thresh = cv2.dilate(thresh, kernel, iterations=1)
thresh = cv2.erode(thresh, kernel, iterations=1)

# Run Tesseract on the preprocessed image
custom_config = r'--oem 3 --psm 6'  # good for block text
text = pytesseract.image_to_string(thresh, config=custom_config)

print(text)

# Optional: Save processed image for inspection
cv2.imwrite("processed_page_3.jpg", thresh)
