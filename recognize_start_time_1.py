import cv2
import easyocr

# Initialize EasyOCR reader (English)
reader = easyocr.Reader(['en'])

def recognize_text_from_frame(frame):
    results = reader.readtext(frame)
    plain_text = " ".join([text for (_, text, _) in results])
    return plain_text.lower()

video_path = "game.mp4"
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    raise IOError("Error opening video file")

fps = cap.get(cv2.CAP_PROP_FPS)
frame_interval = int(fps * 0.5)  # every 0.5 seconds
frame_number = 0
first_frame_with_text = None

while cap.isOpened():
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    text = recognize_text_from_frame(frame_rgb)

    if "welcome" in text:
        first_frame_with_text = frame_number
        print(f"'welcome' found at frame {frame_number}, time {frame_number/fps:.2f} seconds")
        break

    frame_number += frame_interval

cap.release()

if first_frame_with_text is None:
    print("Text not found in video")
else:
    # Cut video from this frame to end
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, first_frame_with_text)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter("cut_video.mp4", fourcc, fps, (width, height))

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)

    cap.release()
    out.release()
    print("Video saved as cut_video.mp4")
