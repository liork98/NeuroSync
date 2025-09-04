import pandas as pd
import os
import shutil
import subprocess

# === Helper to format time for SRT ===
def format_time(t):
    if isinstance(t, pd.Timestamp):
        t = t.time()
    if isinstance(t, str):
        t = t.replace('.', ',')
        if ',' not in t:
            t += ',000'
        return t
    elif isinstance(t, (int, float)):
        hours = int(t // 3600)
        minutes = int((t % 3600) // 60)
        seconds = int(t % 60)
        milliseconds = int((t % 1) * 1000)
        return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"
    return str(t)


def create_subtitles(player_left, player_right,
                     csv_path="logs.csv",
                     video_path="cut_video.mp4",
                     srt_path="subtitles.srt",
                     output_video_path="video_with_subs.mp4",
                     destination_dir="./output"):

    os.makedirs(destination_dir, exist_ok=True)

    # === Read CSV ===
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=["start_time", "end_time"])
    df["text"] = df["answer"].map({
        "left": f"{player_left}'s Turn",
        "right": f"{player_right}'s Turn",
        "neither": "Can't recognize action"
    })
    df = df.sort_values(by="start_time").reset_index(drop=True)

    # === Write .srt file ===
    srt_full_path = os.path.join(destination_dir, srt_path)
    with open(srt_full_path, 'w', encoding='utf-8') as f:
        for idx, row in df.iterrows():
            start = format_time(row["start_time"])
            end = format_time(row["end_time"])
            f.write(f"{idx + 1}\n{start} --> {end}\n{row['text']}\n\n")

    # === Burn subtitles into the video using FFmpeg ===
    output_full_path = os.path.join(destination_dir, output_video_path)
    ffmpeg_cmd = [
        "ffmpeg",
        "-y",  # overwrite if exists
        "-i", video_path,
        "-vf", f"subtitles={srt_full_path}",
        "-c:a", "copy",
        output_full_path
    ]
    subprocess.run(ffmpeg_cmd, check=True)


def main():
    # User can type names here or use defaults
    player_left = input("Enter name for left player: ") or "Or"
    player_right = input("Enter name for right player: ") or "Daniel"

    create_subtitles(player_left, player_right)


if __name__ == "__main__":
    main()
