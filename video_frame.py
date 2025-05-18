import math

import cv2
import os
import pandas as pd

def extract_frame_at_time(video_path, time_sec, output_dir):
    # Open the video file
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError(f"Error opening video file: {video_path}")

    # Set the position (in milliseconds)
    cap.set(cv2.CAP_PROP_POS_MSEC, time_sec * 1000)

    # Read the frame
    success, frame = cap.read()

    if not success:
        raise ValueError(f"Could not read frame at {time_sec} seconds.")

    # Make sure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Define output file path
    output_filename = f"frame_at_{int(time_sec)}s.jpg"
    output_path = os.path.join(output_dir, output_filename)

    # Save the frame as JPEG
    cv2.imwrite(output_path, frame)

    cap.release()
    return output_path

# Example usage:

df = pd.read_csv('999 (2025-05-15 14-47-47).csv', delimiter=';')
time_frames = []
start_times = df['start_time'].tolist()
end_times = df['end_time'].tolist()
for start, end in zip(start_times, end_times):
    time_frames.append((float(start) + float(end)) / 2)

print(time_frames)


for time in time_frames:
    if not math.isnan(time):
        extract_frame_at_time('full_example_video.mp4', time, 'frames')

# for time in time_frames:
#     extract_frame_at_time('full_example_video.mp4', time, 'frames')