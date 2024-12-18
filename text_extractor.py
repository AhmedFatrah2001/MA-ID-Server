import cv2
import pytesseract
import os

# Configure the path to Tesseract OCR executable
pytesseract.pytesseract_cmd = '/bin/tesseract'


class OCRProcessor:
    def __init__(self, debug=False, debug_output_dir="ocr_debug", use_filters=False):
        """
        Initialize the OCRProcessor with predefined language mappings.

        :param debug: If True, saves debug images for each OCR region.
        :param debug_output_dir: Directory to save debug images.
        :param use_filters: If True, applies preprocessing filters (e.g., binarization).
        """
        self.language_map = {
            "ar": "ara",  # Arabic
            "fr": "fra",  # French
        }
        self.debug = debug
        self.debug_output_dir = debug_output_dir
        self.use_filters = use_filters

        if self.debug and not os.path.exists(self.debug_output_dir):
            os.makedirs(self.debug_output_dir)

    def extract_text_from_zones(self, image, zones):
        """
        Extract text from image regions defined by zones.

        :param image: A numpy array representing the image (input from ZoneDetector).
        :param zones: A dictionary containing zone information from ZoneDetector.
                      Format: {label: {"bbox": [x1, y1, x2, y2], "confidence": float}, ...}
        :return: A dictionary with labels as keys and extracted text as values.
                 Format: {label: {"text": str, "confidence": float}, ...}
        """
        ocr_results = {}

        for label, zone in zones.items():
            bbox = zone["bbox"]
            x1, y1, x2, y2 = bbox

            # Crop the region of interest (ROI)
            roi = image[y1:y2, x1:x2]

            # Convert to grayscale (necessary for OCR)
            processed_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

            # Apply optional preprocessing filters
            if self.use_filters:
                processed_roi = cv2.adaptiveThreshold(
                    processed_roi, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
                )

            # Debug: Save or display the ROI being processed
            if self.debug:
                debug_path = os.path.join(self.debug_output_dir, f"{label}_roi.jpg")
                cv2.imwrite(debug_path, processed_roi)
                print(f"[DEBUG] Saved ROI for label '{label}' to: {debug_path}")

            # Determine the OCR language based on the label suffix
            language_suffix = label.split("_")[-1]  # Extract suffix (e.g., 'ar' or 'fr')
            ocr_language = self.language_map.get(language_suffix, "eng")  # Default to English if not found

            # Perform OCR on the region
            extracted_text = pytesseract.image_to_string(processed_roi, config="--oem 3 --psm 10 ", lang=ocr_language).strip()

            # Store the results
            ocr_results[label] = {
                "text": extracted_text,
                "confidence": zone["confidence"],
            }

        return ocr_results
