import math
import os
import cv2
import pandas as pd


def extract_frame_at_time(video_path, time_sec, output_dir):
    """
    Extracts a frame from the video at the specified time (in seconds)
    and saves it as a JPEG in the output directory.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Error opening video file: {video_path}")

    cap.set(cv2.CAP_PROP_POS_MSEC, time_sec * 1000)
    success, frame = cap.read()

    if not success:
        raise ValueError(f"Could not read frame at {time_sec} seconds.")

    os.makedirs(output_dir, exist_ok=True)
    output_filename = f"frame_at_{int(time_sec)}s.jpg"
    output_path = os.path.join(output_dir, output_filename)

    cv2.imwrite(output_path, frame)
    cap.release()
    return output_path


def extract_frames_from_csv(csv_filename, video_filename, output_dir='frames'):
    """
    Reads a CSV file with 'start_time' and 'end_time' columns,
    calculates midpoints, and extracts frames from the video.
    """
    df = pd.read_csv(csv_filename, delimiter=';')
    time_frames = [(float(start) + float(end)) / 2
                   for start, end in zip(df['start_time'], df['end_time'])]

    extracted_files = []
    for time in time_frames:
        if not math.isnan(time):
            extracted_files.append(extract_frame_at_time(video_filename, time, output_dir))

    return extracted_files


def main():
    csv_filename = 'logsByGame.csv'  # Change this to your CSV file
    video_filename = 'cut_video.mp4'  # Change this to your video file
    output_dir = 'frames'  # Optional: change output directory

    extracted_files = extract_frames_from_csv(csv_filename, video_filename, output_dir)
    print(f"Extracted {len(extracted_files)} frames:")
    for f in extracted_files:
        print(f"  {f}")


if __name__ == '__main__':
    main()
