# Step 1: Install required packages
!apt-get install tesseract-ocr -y
!apt-get install tesseract-ocr-heb -y
!pip install pytesseract
!pip install opencv-python

# Step 2: Import libraries
import cv2
import pytesseract
import numpy as np
from matplotlib import pyplot as plt

# Step 3: Configs
video_path = "/content/fullVideo.mp4"
custom_config = r'-l heb --psm 6'
ocr_data_config = r'-l heb --psm 6 --oem 3'
pixel_diff_threshold = 0.04

# Step 4: Helper
def inflate_box(x, y, w, h, image_shape, inflate_ratio=0.2):
    dw = int(w * inflate_ratio / 2)
    dh = int(h * inflate_ratio / 2)
    x_new = max(0, x - dw)
    y_new = max(0, y - dh)
    x2_new = min(image_shape[1], x + w + dw)
    y2_new = min(image_shape[0], y + h + dh)
    return x_new, y_new, x2_new - x_new, y2_new - y_new

# Step 5: Initialize
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    raise IOError("Cannot open video")

fps = cap.get(cv2.CAP_PROP_FPS)
frame_interval = int(fps * 0.5)
frame_number = 0

crop_box = None
reference_crop = None
reference_crop_gray = None
start_processing = False

last_matching_frame_number = None
last_matching_crop = None

# -------- Phase 1: Fast Scan (every 0.5s) --------
while cap.isOpened():
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    if not start_processing:
        data = pytesseract.image_to_data(frame_rgb, config=ocr_data_config, output_type=pytesseract.Output.DICT)
        words = data["text"]
        text_combined = " ".join(words).strip()

        if "תרגול" in text_combined and "המשחק" in text_combined:
            print(f"\n🟢 First match at frame {frame_number}")
            boxes = []
            for i, word in enumerate(words):
                if word in ["תרגול", "המשחק"]:
                    x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
                    boxes.append((x, y, w, h))

            if len(boxes) == 2:
                x_vals = [b[0] for b in boxes]
                y_vals = [b[1] for b in boxes]
                x2_vals = [b[0] + b[2] for b in boxes]
                y2_vals = [b[1] + b[3] for b in boxes]
                x_min, y_min = min(x_vals), min(y_vals)
                x_max, y_max = max(x2_vals), max(y2_vals)
                w, h = x_max - x_min, y_max - y_min

                crop_box = inflate_box(x_min, y_min, w, h, frame_rgb.shape, 0.2)
                x, y, w, h = crop_box
                reference_crop = frame_rgb[y:y+h, x:x+w]
                reference_crop_gray = cv2.cvtColor(reference_crop, cv2.COLOR_RGB2GRAY)
                start_processing = True

                last_matching_crop = reference_crop.copy()
                last_matching_frame_number = frame_number

                plt.imshow(reference_crop)
                plt.axis('off')
                plt.title(f"Frame {frame_number} (First Match)")
                plt.show()
    else:
        x, y, w, h = crop_box
        current_crop = frame_rgb[y:y+h, x:x+w]
        current_crop_gray = cv2.cvtColor(current_crop, cv2.COLOR_RGB2GRAY)

        resized_ref = cv2.resize(reference_crop_gray, (w, h))
        diff = cv2.absdiff(current_crop_gray, resized_ref)
        mean_diff = np.mean(diff) / 255

        if mean_diff <= pixel_diff_threshold:
            print(f"\n✅ Frame {frame_number} (Assumed match — diff {mean_diff:.3f})")
            plt.imshow(current_crop)
            plt.axis('off')
            plt.title(f"Frame #{frame_number} (Assumed Match)")
            plt.show()
            last_matching_crop = current_crop.copy()
            last_matching_frame_number = frame_number
        else:
            # Confirm with OCR
            text = pytesseract.image_to_string(current_crop, config=custom_config)
            if "תרגול" in text and "המשחק" in text:
                print(f"\n✅ Frame {frame_number} (OCR confirmed after diff {mean_diff:.3f})")
                plt.imshow(current_crop)
                plt.axis('off')
                plt.title(f"Frame #{frame_number}")
                plt.show()
                print("📝 OCR Output:")
                print(text)
                last_matching_crop = current_crop.copy()
                last_matching_frame_number = frame_number
            else:
                # ❌ Mismatch: Show mismatched frame clearly
                print(f"\n⛔ Mismatch at frame {frame_number} (diff {mean_diff:.3f}) — stopping fast scan")
                plt.imshow(current_crop)
                plt.axis('off')
                plt.title(f"Mismatch Frame #{frame_number}")
                plt.show()
                print("📝 OCR Output:")
                print(text)
                break

    frame_number += frame_interval

cap.release()

# -------- Phase 2: Refined Frame-by-Frame Search --------
print(f"\n🔍 Starting refined search from frame {last_matching_frame_number}")
refined_cap = cv2.VideoCapture(video_path)
refined_frame_number = last_matching_frame_number
last_good_frame = None
last_good_frame_number = None

while refined_cap.isOpened():
    refined_cap.set(cv2.CAP_PROP_POS_FRAMES, refined_frame_number)
    ret, frame = refined_cap.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    x, y, w, h = crop_box
    current_crop = frame_rgb[y:y+h, x:x+w]
    current_crop_gray = cv2.cvtColor(current_crop, cv2.COLOR_RGB2GRAY)

    resized_ref = cv2.resize(reference_crop_gray, (w, h))
    diff = cv2.absdiff(current_crop_gray, resized_ref)
    mean_diff = np.mean(diff) / 255

    if mean_diff <= pixel_diff_threshold:
        last_good_frame = current_crop.copy()
        last_good_frame_number = refined_frame_number
        refined_frame_number += 1
    else:
        print(f"\n⛔ Refined search stopped at frame {refined_frame_number} (diff {mean_diff:.3f})")
        plt.imshow(current_crop)
        plt.axis('off')
        plt.title(f"Mismatch in Refined Search Frame #{refined_frame_number}")
        plt.show()
        break

refined_cap.release()

if last_good_frame is not None:
    print(f"\n✅ Last matching frame in refined search: {last_good_frame_number}")
    plt.imshow(last_good_frame)
    plt.axis('off')
    plt.title(f"Refined Last Frame #{last_good_frame_number}")
    plt.show()
else:
    print("\n⚠️ No matching frame found in refined search.")
