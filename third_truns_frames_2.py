import math
import os
import cv2
import pandas as pd


def extract_frame_at_time(video_path, time_sec, output_dir):
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
    df = pd.read_csv(csv_filename, delimiter=';')
    extracted_files = []

    for idx, row in df.iterrows():
        start, end = float(row['start_time']), float(row['end_time'])
        if math.isnan(start) or math.isnan(end):
            continue

        # Divide the interval into 4 parts and pick the 3 middle points
        times = [start + (end - start) * i / 4 for i in range(1, 4)]
        for time in times:
            extracted_files.append(extract_frame_at_time(video_filename, time, output_dir))

    return extracted_files


def main():
    csv_filename = 'logsByGame.csv'
    video_filename = 'cut_video.mp4'
    output_dir = 'frames'

    extracted_files = extract_frames_from_csv(csv_filename, video_filename, output_dir)
    print(f"Extracted {len(extracted_files)} frames:")
    for f in extracted_files:
        print(f"  {f}")


if __name__ == '__main__':
    main()
