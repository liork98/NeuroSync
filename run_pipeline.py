#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Creative Foraging – Analysis Pipeline Runner (without game execution)

Flow (run these in order, game is run separately):
2) recognize_start_time_1.py   -> reads: game.mp4 ; writes: cut_video.mp4
3) middle_turns_frames_2.py    -> reads: logsByGame.csv + cut_video.mp4 ; writes: frames/
   (also supports the mis-typed name: middle_truns_frames_2.py)
4) create_logs_table_3.py      -> reads: frames/ + logsByGame.csv ; writes: logs.csv
5) create_video_with_subs_4.py -> reads: cut_video.mp4 + logs.csv ; writes: ./output/video_with_subs.mp4

Notes:
- Step 4 likely requires an OpenAI API key (export OPENAI_API_KEY=...).
- Step 5 prompts for two player names; this runner can auto-feed them.
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path

DEFAULTS = {
    "start_time_script":   "recognize_start_time_1.py",
    "frames_variants":     ["middle_turns_frames_2.py", "middle_truns_frames_2.py"],
    "logs_table_script":   "create_logs_table_3.py",
    "video_with_subs":     "create_video_with_subs_4.py",
    "game_video":          "game.mp4",              # input to step 2
    "cut_video":           "cut_video.mp4",         # output of 2; input to 3 & 5
    "logs_by_game_csv":    "logsByGame.csv",        # input to 3 & 4
    "frames_dir":          "frames",                # output of 3
    "logs_csv":            "logs.csv",              # output of 4
    "output_dir":          "output",
    "output_video":        "video_with_subs.mp4"    # output of 5 (inside output/)
}

def check_exists(path: Path, kind: str = "file", required: bool = True) -> bool:
    ok = path.is_file() if kind == "file" else path.is_dir()
    if required and not ok:
        raise FileNotFoundError(f"Required {kind} not found: {path}")
    return ok

def run_script(py_file: Path, args=None, input_text: str | None = None):
    cmd = [sys.executable, str(py_file)]
    if args:
        cmd.extend(args)
    print(f"\n=== Running: {' '.join(cmd)} ===")
    try:
        res = subprocess.run(
            cmd,
            input=(input_text.encode("utf-8") if input_text else None),
            check=True
        )
        return res.returncode
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Step failed: {py_file} (exit={e.returncode})")
        raise

def pick_frames_script(candidates: list[str]) -> Path:
    for name in candidates:
        p = Path(name)
        if p.is_file():
            return p
    raise FileNotFoundError(f"Could not find frames script. Tried: {', '.join(candidates)}")

def main():
    ap = argparse.ArgumentParser(description="Run Creative Foraging analysis pipeline (steps 2-5).")
    ap.add_argument("--workdir", default=".", help="Directory containing the scripts and data files.")
    ap.add_argument("--players", nargs=2, metavar=("LEFT", "RIGHT"),
                    default=["player1", "player2"],
                    help="Player names for subtitles (left, right). Default: player1 player2")
    ap.add_argument("--skip-names-feed", action="store_true",
                    help="Do NOT auto-feed names to step 5 (let it prompt interactively).")
    ap.add_argument("--env-api-key", default="api_key",
                    help="Env var name that holds the OpenAI API key for step 4 (default: api_key).")

    args = ap.parse_args()
    wd = Path(args.workdir).resolve()
    os.chdir(wd)

    # Resolve scripts
    start_time_script      = wd / DEFAULTS["start_time_script"]
    frames_script          = pick_frames_script(DEFAULTS["frames_variants"])
    logs_table_script      = wd / DEFAULTS["logs_table_script"]
    video_with_subs_script = wd / DEFAULTS["video_with_subs"]

    # Check presence of expected inputs before starting
    game_video   = wd / DEFAULTS["game_video"]
    logs_by_game = wd / DEFAULTS["logs_by_game_csv"]

    check_exists(start_time_script)
    check_exists(frames_script)
    check_exists(logs_table_script)
    check_exists(video_with_subs_script)

    # Step 2 expects game.mp4
    check_exists(game_video)

    # Step 3 & 4 expect logsByGame.csv
    check_exists(logs_by_game)

    # === Step 2: recognize_start_time_1.py -> cut_video.mp4
    run_script(start_time_script)
    cut_video = wd / DEFAULTS["cut_video"]
    check_exists(cut_video)

    # === Step 3: middle_*_frames_2.py -> frames/
    run_script(frames_script)
    frames_dir = wd / DEFAULTS["frames_dir"]
    check_exists(frames_dir, kind="dir")

    # === Step 4: create_logs_table_3.py -> logs.csv
    run_script(logs_table_script)
    logs_csv = wd / DEFAULTS["logs_csv"]
    check_exists(logs_csv)

    # === Step 5: create_video_with_subs_4.py -> ./output/video_with_subs.mp4
    if args.skip_names_feed:
        run_script(video_with_subs_script)  # will prompt for names
    else:
        left, right = args.players
        # Feed two lines (left, right) to stdin for the script's input()
        run_script(video_with_subs_script, input_text=f"{left}\n{right}\n")

    final_video = wd / DEFAULTS["output_dir"] / DEFAULTS["output_video"]
    if final_video.is_file():
        print(f"\n✅ Done! Final video created: {final_video}")
    else:
        print("\n[WARN] Step 5 finished, but final video not found where expected. Check ffmpeg output/logs.")

if __name__ == "__main__":
    main()
