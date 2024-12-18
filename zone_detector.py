import cv2
from ultralytics import YOLO

class ZoneDetector:
    def __init__(self):
        
        """
        Initialize the ZoneDetector with a YOLO model and class names.
        """
        class_names = [
            "fn_ar",  # 0
            "ln_ar",  # 1
            "fn_fr",  # 2
            "ln_fr",  # 3
            "bd_fr",  # 4
            "bp_ar",  # 5
            "bp_fr",  # 6
            "vd_fr",  # 7
            "cin_fr"  # 8
        ]
        self.model = YOLO("weights/best.pt")
        self.class_names = class_names

    def detect_zones(self, image):
        """
        Detect zones in the image using the YOLO model and return unique zones.

        :param image: Input image as a numpy array (e.g., from an HTTP request).
        :return: Dictionary with unique zones and their labels.
        """
        # Run inference
        results = self.model.predict(source=image, save=False, show=False, verbose=False)
        
        # Prepare data for processing
        unique_zones = {}
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Extract bounding box coordinates and class ID
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                cls = int(box.cls[0])

                # Map class ID to class name
                label = self.class_names[cls]

                # Check if the label already exists, keep only the first occurrence
                if label not in unique_zones:
                    unique_zones[label] = {
                        "bbox": [x1, y1, x2, y2],
                        "confidence": conf
                    }

        return unique_zones

