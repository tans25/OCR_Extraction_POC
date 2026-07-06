"""
ocr.py - takes in the raw image bytes uploaded by the user, loads the image, runs the image processing steps,
followed by extraction of raw text from the image. 
The original uploaded image and raw extracted text is returned in a dictionary:
"""

import cv2 
from PIL import Image 
import pytesseract 
import numpy as np


def load_image(uploaded_image):
    """
    Takes the uploaded image and decodes it using openCV 

    Args: 
    uploaded_image: Bytes of the image uploaded by the user 

    Output:
    image: Numpy n-dimensional array of decoded image  
    """
    try:
        file = np.frombuffer(uploaded_image.read(), dtype=np.uint8)
        uploaded_image.seek(0)
        image = cv2.imdecode(file, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("Could not decode uploaded image.")
        return image 
    except Exception as e:
        print("Error in loading image: ", e)
        return np.empty([])


def _deskew(image):
    """
    Detect skew angles and rotate to correct it 
    """
    try:
        # find coordinates of all non-zero (text) pixels
        coords = np.column_stack(np.where(image < 128))
        
        if len(coords) < 50:
            return image  # not enough text pixels to estimate skew
        
        # get the minimum area bounding rectangle
        angle = cv2.minAreaRect(coords)[-1]
    
        # normalize the angle
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
    
        # only correct if skew is meaningful (> 0.5 degrees) but not extreme
        if abs(angle) < 0.5 or abs(angle) > 15:
            return image
    
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            image, M, (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )
        return rotated
    except Exception as e:
        print("Error in deskewing", e)
        return np.empty([])



def preprocess_image(image):
    """
    Preprocessing the image to improve OCR accuracy.  

    Steps:
        1. Convert to grayscale
        2. Resize if too small 
        3. Denoise with bilateral filter 
        4. Sharpen to make text edges crisper
        5. Adaptive thresholding for uneven lighting
        6. Morphological close to fix broken/touching characters
        7. Deskew based on detected text angle
        8. Border padding so text doesn't touch image edges
    """
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # convert to grayscale 
        height, width = gray.shape 

        # scaling small images
        if height < 1000:
            scale = 1500 / height 
            gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        
        # removing noise pixels from the image 
        denoised = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # sharpening the edges 
        sharpen_kernel = np.array([[0, -1, 0],
                                   [-1, 5, -1],
                                   [0, -1, 0]])
        sharpened = cv2.filter2D(denoised, -1, sharpen_kernel)

        # adaptive thresholding to convert images to binary 
        thresh = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 11)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
        morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)


        # deskew 
        deskewed = _deskew(morph)

        padded = cv2.copyMakeBorder(deskewed, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=255)

        return padded 
    
    except Exception as e:
        print("Error in preprocessing images", e)
        return np.empty([])

def extract_text(processed_image):
    """
    Run Tesseract OCR on a preprocessed image.
    
    Uses --psm 6 (assume a single uniform block of text) which works well
    for prescription layouts.
    """
    text = ''
    try:
        config = r"--oem 3 --psm 6"
        text = pytesseract.image_to_string(processed_image, config=config)
    except Exception as e:
        print("Error in extracting text from image: ", e)
    return text 


def run_ocr(uploaded_file):
    """
    Run the OCR pipeline from loading the image to image processing and text extraction 
    """
    # Load image 
    image = load_image(uploaded_file)
    original_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    
    # Preprocess 
    preprocess_img = preprocess_image(image)

    # Extract text 
    raw_text = extract_text(preprocess_img)
    
    result = {
        "original": original_img, 
        "raw_text": raw_text
    }
    return result 