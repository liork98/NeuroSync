import base64
import csv
import re
from pathlib import Path

import numpy as np
import pandas as pd
from openai import OpenAI

client = OpenAI(api_key="")

# ---------- Helpers ----------
def encode_image(image_path: Path) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def analyze_frame(image_path: Path):
    base64_image = encode_image(image_path)
    response = client.responses.create(
        model="gpt-4.1",
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text",
                 "text": "who touches the screen: the person on the left, the person on the right, or none? explain. write: first line - left or right or neither, then second line explain"},
                {"type": "input_image",
                 "image_url": f"data:image/jpeg;base64,{base64_image}"},
            ],
        }],
    )
    output = response.output_text.strip().split("\n", 1)
    answer = output[0].strip() if len(output) > 0 else ""
    explanation = output[1].strip() if len(output) > 1 else ""
    return explanation, answer

# Extract numeric timestamp from filename (e.g., frame_000123.jpg → 123, or 17.3)
def extract_frame_time(filename_stem: str):
    m = re.search(r"(?i)(\d+)h(\d+)\.(\d+)(?:\.(\d+))?", filename_stem)  # 18h11.58.511
    if m:
        h = int(m.group(1)); mm = int(m.group(2)); ss = int(m.group(3)); ms = int(m.group(4)) if m.group(4) else 0
        return h*3600 + mm*60 + ss + ms/1000.0
    m = re.search(r"(\d+(?:\.\d+)?)s\b", filename_stem)  # ...5.36s
    if m:
        return float(m.group(1))
    nums = re.findall(r"\d+(?:\.\d+)?", filename_stem)
    return float(nums[-1]) if nums else None

# ---------- Paths ----------
frames_folder = Path("frames")
frame_files = sorted(frames_folder.glob("*.jpg"))  # עדכני סיומת אם צריך
csv_file = "logs.csv"
logs_by_game_file = "logsByGame.csv"

# ---------- Load game logs (;) ----------
logs_df = pd.read_csv(logs_by_game_file, sep=';')

# Validate columns
required_cols = {"start_time", "end_time", "type"}
if not required_cols.issubset(logs_df.columns):
    raise ValueError(f"logsByGame.csv must have columns: {required_cols}")

# Numeric times
logs_df["start_time"] = pd.to_numeric(logs_df["start_time"], errors="coerce")
logs_df["end_time"]   = pd.to_numeric(logs_df["end_time"],   errors="coerce")

# Precompute floored/ceil times for matching
logs_df["_start_floor"] = np.floor(logs_df["start_time"])
logs_df["_end_ceil"]    = np.ceil(logs_df["end_time"])

# Split to interval rows vs. point events (no end_time)
interval_rows = logs_df[~logs_df["end_time"].isna()].copy()
point_rows    = logs_df[ logs_df["end_time"].isna()].copy()

# ---------- Write output ----------
with open(csv_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["frame", "t_seconds", "explanation", "answer",
                     "start_time", "end_time", "action"])

    for frame_path in frame_files:
        # time from filename
        t = extract_frame_time(frame_path.stem)
        t_sec = None if t is None else float(t)
        # bin to integer second (floor)
        frame_sec = None if t_sec is None else int(np.floor(t_sec))

        explanation, answer = analyze_frame(frame_path)

        start_out, end_out, action_out = "", "", ""

        if frame_sec is not None:
            # 1) interval match with floor/ceil bounds
            hit = interval_rows[
                (interval_rows["_start_floor"] <= frame_sec) &
                (frame_sec < interval_rows["_end_ceil"])
            ]

            if not hit.empty:
                row = hit.iloc[0]
                action_type = str(row["type"]).strip().lower()
                if action_type == "moveblock":
                    action_out = "move block"
                elif action_type == "added shape to gallery":
                    action_out = "added shape to gallery"
                else:
                    action_out = row["type"]

                start_out = row["start_time"]
                end_out   = row["end_time"]

            else:
                # 2) point events: match when floor(start_time) == frame_sec
                pts = point_rows[np.floor(point_rows["start_time"]).astype("Int64") == frame_sec]
                if not pts.empty:
                    row = pts.iloc[0]
                    action_type = str(row["type"]).strip().lower()
                    action_out = "added shape to gallery" if action_type == "added shape to gallery" else row["type"]
                    start_out = row["start_time"]
                    end_out   = ""  # no end_time

                else:
                    # 3) fallback: nearest interval by integer distance
                    if not interval_rows.empty:
                        tmp = interval_rows.copy()
                        # distance in integer-second space
                        tmp["_dist"] = tmp.apply(
                            lambda r: 0 if (r["_start_floor"] <= frame_sec < r["_end_ceil"])
                            else min(abs(frame_sec - r["_start_floor"]), abs(frame_sec - r["_end_ceil"])),
                            axis=1
                        )
                        row = tmp.sort_values("_dist").iloc[0]
                        action_type = str(row["type"]).strip().lower()
                        if action_type == "moveblock":
                            action_out = "move block"
                        elif action_type == "added shape to gallery":
                            action_out = "added shape to gallery"
                        else:
                            action_out = row["type"]
                        start_out = row["start_time"]
                        end_out   = row["end_time"]

        # write row
        writer.writerow([frame_path.name, t_sec, explanation, answer, start_out, end_out, action_out])
        print(f"Processed {frame_path.name}: answer={answer}, action={action_out}, t={t_sec}, sec={frame_sec}")