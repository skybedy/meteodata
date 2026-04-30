from __future__ import annotations

import argparse
import subprocess
from datetime import date, timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

LAT_MIN, LAT_MAX = 24, 32
LON_MIN, LON_MAX = 340, 350
VMIN, VMAX = 16, 20.5


def to_west_longitudes(lon: xr.DataArray) -> np.ndarray:
    return ((lon.to_numpy() + 180) % 360) - 180


def march_dates_2026() -> list[date]:
    start = date(2026, 3, 1)
    return [start + timedelta(days=offset) for offset in range(31)]


def expected_daily_filename(day: date) -> str:
    # NOAA naming convention for daily OISST files.
    return f"oisst-avhrr-v02r01.{day:%Y%m%d}.nc"


def render_frame(input_path: Path, output_path: Path, day: date) -> None:
    with xr.open_dataset(input_path) as ds:
        sst = ds["sst"].isel(time=0, zlev=0)
        sst_canary = sst.sel(lat=slice(LAT_MIN, LAT_MAX), lon=slice(LON_MIN, LON_MAX))

        lon_west = to_west_longitudes(sst_canary.lon)
        lat = sst_canary.lat.to_numpy()
        values = np.ma.masked_invalid(sst_canary.to_numpy())

    cmap = plt.get_cmap("RdYlBu_r").copy()
    cmap.set_bad("#303030")

    fig, ax = plt.subplots(figsize=(9, 7), dpi=160)
    ax.set_facecolor("#303030")
    im = ax.imshow(
        values,
        extent=[lon_west.min(), lon_west.max(), lat.min(), lat.max()],
        origin="lower",
        cmap=cmap,
        vmin=VMIN,
        vmax=VMAX,
        interpolation="bicubic",
        aspect="auto",
    )
    ax.set_title(f"Sea Surface Temperature - Canary Islands - {day:%Y-%m-%d}", pad=12)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.grid(color="#6f6f6f", linestyle="--", linewidth=0.5, alpha=0.35)
    ax.set_xlim(lon_west.min(), lon_west.max())
    ax.set_ylim(lat.min(), lat.max())

    cbar = fig.colorbar(im, ax=ax, extend="both", fraction=0.046, pad=0.04)
    cbar.set_label("Sea surface temperature (°C)")

    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)


def compose_video(frames_dir: Path, output_mp4: Path, fps: int) -> None:
    cmd = [
        "ffmpeg",
        "-y",
        "-framerate",
        str(fps),
        "-i",
        str(frames_dir / "frame_%Y-%m-%d.png"),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(output_mp4),
    ]
    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Render daily SST frames for March 2026 from NOAA OISST daily NetCDF files and compose MP4."
        )
    )
    parser.add_argument("--daily-dir", type=Path, default=Path("data/daily"))
    parser.add_argument("--frames-dir", type=Path, default=Path("frames/march_2026"))
    parser.add_argument("--output-mp4", type=Path, default=Path("output/canary_sst_march_2026.mp4"))
    parser.add_argument("--fps", type=int, default=12)
    args = parser.parse_args()

    args.frames_dir.mkdir(parents=True, exist_ok=True)
    args.output_mp4.parent.mkdir(parents=True, exist_ok=True)

    missing_files: list[Path] = []
    rendered = 0

    for day in march_dates_2026():
        daily_file = args.daily_dir / expected_daily_filename(day)
        frame_path = args.frames_dir / f"frame_{day:%Y-%m-%d}.png"

        if not daily_file.exists():
            missing_files.append(daily_file)
            continue

        print(f"Rendering {day:%Y-%m-%d} from {daily_file} -> {frame_path}")
        render_frame(daily_file, frame_path, day)
        rendered += 1

    print(f"Rendered frames: {rendered}")

    if missing_files:
        print("Missing daily files:")
        for path in missing_files:
            print(f"  - {path}")

    if rendered == 0:
        print("No frames were rendered, skipping MP4 composition.")
        return

    compose_video(args.frames_dir, args.output_mp4, args.fps)
    print(f"Animation created: {args.output_mp4}")


if __name__ == "__main__":
    main()
