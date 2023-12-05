import cv2
import numpy as np

### START SETUP

# Background Subtractor settings
BG_SUB_HISTORY = 500
BG_SUB_VAR_THRESHOLD = 10
BG_SUB_DETECT_SHADOWS = False

# Minimum area threshold for a valid moving object
MIN_CONTOUR_AREA = 40000

# Smoothing factor for the dot's movement (adjust as needed)
SMOOTHING_FACTOR = 0.1

KSIZE = (7, 7)

### END SETUP

# Create a background subtractor object
bg_subtractor = cv2.createBackgroundSubtractorMOG2(
    history=BG_SUB_HISTORY,
    varThreshold=BG_SUB_VAR_THRESHOLD,
    detectShadows=BG_SUB_DETECT_SHADOWS
)

cap = cv2.VideoCapture(0)

last_contour = None
smoothed_center = None


def get_new_center(bounding_rect, prev_smoothed_center=None):
    x, y, w, h = bounding_rect

    center_x = x + w // 2
    center_y = y + h // 2

    if prev_smoothed_center is None:
        return (center_x, center_y)
    else:
        return (
            int((1 - SMOOTHING_FACTOR) * prev_smoothed_center[0] + SMOOTHING_FACTOR * center_x),
            int((1 - SMOOTHING_FACTOR) * prev_smoothed_center[1] + SMOOTHING_FACTOR * center_y)
        )


while True:
    # Read a frame from the video feed
    ret, frame = cap.read()
    if not ret:
        break

    # Apply the background subtractor to get the foreground mask
    fg_mask_raw = bg_subtractor.apply(frame)

    # Apply some morphological operations to reduce noise
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, KSIZE)
    fg_mask = cv2.morphologyEx(fg_mask_raw, cv2.MORPH_OPEN, kernel)
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)

    # Find contours in the foreground mask
    contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter contours based on minimum area
    valid_contours = [contour for contour in contours if cv2.contourArea(contour) > MIN_CONTOUR_AREA]

    # Find the contour with the maximum area
    max_contour = max(valid_contours, key=cv2.contourArea, default=None)

    if max_contour is not None:
        last_contour = max_contour

    active_contour = last_contour

    if active_contour is not None:
        # Calculate the center of the bounding area
        x, y, w, h = cv2.boundingRect(active_contour)

        # Smooth the movement of the dot
        smoothed_center = get_new_center((x, y, w, h), smoothed_center)

        # Draw stuff
        cv2.circle(frame, smoothed_center, radius=10, color=(0, 0, 255), thickness=-1)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    ### DRAW RESULT

    height, width, channels = frame.shape
    empty_image = np.zeros((height, width, channels), dtype=np.uint8)

    display_img = np.vstack((
        np.hstack((
            cv2.cvtColor(fg_mask_raw, cv2.COLOR_GRAY2BGR),
            cv2.cvtColor(fg_mask, cv2.COLOR_GRAY2BGR),
        )),
        np.hstack((
            frame,
            empty_image,
        ))
    ))

    # Display the result frame with the largest moving object rectangle
    cv2.imshow("Moving Object Detection", display_img)

    # Break the loop when 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close all windows
cap.release()
cv2.destroyAllWindows()
