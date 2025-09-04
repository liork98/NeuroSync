import base64
import csv
import pandas as pd
from openai import OpenAI
from pathlib import Path
import re

client = OpenAI(api_key="")

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Function to get GPT response
def analyze_frame(image_path):
    base64_image = encode_image(image_path)

    response = client.responses.create(
        model="gpt-4.1",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "who touches the screen: the person on the left, the person on the right, or none? explain. write: first line - left or right or neither, then second line explain"
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{base64_image}",
                    },
                ],
            }
        ],
    )

    output = response.output_text.strip().split("\n", 1)
    answer = output[0].strip() if len(output) > 0 else ""
    explanation = output[1].strip() if len(output) > 1 else ""

    return explanation, answer


# Extract numeric timestamp from frame filename (e.g., frame_000123.jpg → 123)
def extract_frame_time(filename):
    match = re.search(r"(\d+)", filename)
    return int(match.group(1)) if match else None


# Paths
frames_folder = Path("frames")
frame_files = sorted(frames_folder.glob("*.jpg"))  # Adjust extension if needed
csv_file = "logs.csv"
logs_by_game_file = "logsByGame.csv"

# Load logsByGame
logs_df = pd.read_csv(logs_by_game_file, sep=';')


# Ensure required columns exist
required_cols = {"start_time", "end_time", "type"}
if not required_cols.issubset(logs_df.columns):
    raise ValueError(f"logsByGame.csv must have columns: {required_cols}")

# Convert times to numeric (if needed)
logs_df["start_time"] = pd.to_numeric(logs_df["start_time"], errors="coerce")
logs_df["end_time"] = pd.to_numeric(logs_df["end_time"], errors="coerce")

# Writing CSV header
with open(csv_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["frame", "explanation", "answer", "start_time", "end_time", "action_type"])

    for frame_path in frame_files:
        frame_time = extract_frame_time(frame_path.stem)  # numeric frame index/time
        explanation, answer = analyze_frame(frame_path)

        # Find all matching log rows by time interval
        matching_rows = logs_df[(logs_df["start_time"] <= frame_time) & (frame_time < logs_df["end_time"])]

        if not matching_rows.empty:
            # Write one row per matching log (avoids skipping any)
            for _, log_row in matching_rows.iterrows():
                writer.writerow([
                    frame_path.name,
                    explanation,
                    answer,
                    log_row["start_time"],
                    log_row["end_time"],
                    log_row["type"]
                ])
                print(f"Processed {frame_path.name}: {answer}, action={log_row['type']}")
        else:
            # No matching log interval
            writer.writerow([frame_path.name, explanation, answer, "", "", "none"])
            print(f"Processed {frame_path.name}: {answer}, action=none")
