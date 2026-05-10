from __future__ import annotations

import json
from datetime import date
from pathlib import Path
import sys


def validate(manifest_path: Path) -> int:
    with manifest_path.open("r", encoding="utf-8") as f:
        manifest = json.load(f)

    frames = manifest.get("frames", [])
    if manifest.get("frameCount") != len(frames):
        print("frameCount does not match frames length")
        return 1

    dates = []
    base_dir = manifest_path.parent
    for i, frame in enumerate(frames):
        for key in ("date", "file", "label"):
            if key not in frame:
                print(f"Frame {i} missing key: {key}")
                return 1
        frame_date = date.fromisoformat(frame["date"])
        dates.append(frame_date)
        if not (base_dir / frame["file"]).exists():
            print(f"Missing frame file: {frame['file']}")
            return 1

    if dates != sorted(dates):
        print("Frames are not sorted by date")
        return 1

    if "video" in manifest and not (base_dir / manifest["video"]).exists():
        print(f"Manifest references missing video file: {manifest['video']}")
        return 1

    print("Manifest is valid")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python validate_manifest.py /path/to/manifest.json")
        raise SystemExit(2)
    raise SystemExit(validate(Path(sys.argv[1])))
