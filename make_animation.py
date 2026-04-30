from __future__ import annotations

import argparse
import calendar
import subprocess
import urllib.request
from datetime import date, timedelta
from pathlib import Path

import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

LAT_MIN, LAT_MAX = 24, 32
LON_MIN, LON_MAX = 340, 350
VMIN, VMAX = 16, 20.5
CARTOPY_DATA_DIR = Path("data/cartopy")
NOAA_URL_TEMPLATE = "https://www.ncei.noaa.gov/data/sea-surface-temperature-optimum-interpolation/v2.1/access/avhrr/{year:04d}{month:02d}/oisst-avhrr-v02r01.{year:04d}{month:02d}{day:02d}.nc"


def to_west_longitudes(lon: xr.DataArray) -> np.ndarray:
    return ((lon.to_numpy() + 180) % 360) - 180


def generate_dates(start_date: date, end_date: date) -> list[date]:
    delta = end_date - start_date
    return [start_date + timedelta(days=i) for i in range(delta.days + 1)]


def expected_daily_filename(day: date) -> str:
    # NOAA naming convention for daily OISST files.
    return f"oisst-avhrr-v02r01.{day:%Y%m%d}.nc"


def download_noaa_file(day: date, dest_path: Path) -> bool:
    url = NOAA_URL_TEMPLATE.format(year=day.year, month=day.month, day=day.day)
    try:
        urllib.request.urlretrieve(url, str(dest_path))
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        if dest_path.exists():
            dest_path.unlink()
        return False


def fill_nearshore_gaps(sst_subset: xr.DataArray) -> xr.DataArray:
    """
    Fill small coastal/mask gaps by nearest-neighbour interpolation
    along both lon and lat directions.
    """
    filled = sst_subset.interpolate_na(dim="lon", method="nearest", fill_value="extrapolate")
    filled = filled.interpolate_na(dim="lat", method="nearest", fill_value="extrapolate")
    return filled


def upscale_grid(sst_subset: xr.DataArray, factor: int) -> xr.DataArray:
    if factor <= 1:
        return sst_subset

    lat_new = np.linspace(float(sst_subset.lat.min()), float(sst_subset.lat.max()), sst_subset.sizes["lat"] * factor)
    lon_new = np.linspace(float(sst_subset.lon.min()), float(sst_subset.lon.max()), sst_subset.sizes["lon"] * factor)
    return sst_subset.interp(lat=lat_new, lon=lon_new, method="linear")


def render_frame(input_path: Path, output_path: Path, day: date, upscale_factor: int) -> None:
    with xr.open_dataset(input_path) as ds:
        sst = ds["sst"].isel(time=0, zlev=0)
        sst_canary = sst.sel(lat=slice(LAT_MIN, LAT_MAX), lon=slice(LON_MIN, LON_MAX))
        sst_filled = fill_nearshore_gaps(sst_canary)
        sst_render = upscale_grid(sst_filled, upscale_factor)

        lon_west = to_west_longitudes(sst_render.lon)
        lat = sst_render.lat.to_numpy()
        values = np.ma.masked_invalid(sst_render.to_numpy())

    cmap = plt.get_cmap("RdYlBu_r").copy()
    cmap.set_bad("#303030")

    fig = plt.figure(figsize=(9, 7), dpi=160)
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_facecolor("#303030")
    im = ax.pcolormesh(
        lon_west,
        lat,
        values,
        transform=ccrs.PlateCarree(),
        cmap=cmap,
        vmin=VMIN,
        vmax=VMAX,
        shading="auto",
    )

    land = cfeature.NaturalEarthFeature(
        "physical",
        "land",
        "10m",
        facecolor="#303030",
        edgecolor="#f5f0e6",
    )
    ax.add_feature(land, linewidth=0.55, zorder=3)
    ax.add_feature(cfeature.COASTLINE.with_scale("10m"), linewidth=0.35, edgecolor="#f5f0e6", zorder=4)

    ax.set_title(f"Sea Surface Temperature - Canary Islands - {day:%Y-%m-%d}", pad=12)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.gridlines(
        crs=ccrs.PlateCarree(),
        draw_labels=False,
        linewidth=0.45,
        color="#6f6f6f",
        linestyle="--",
        alpha=0.35,
    )
    ax.set_extent([float(lon_west.min()), float(lon_west.max()), float(lat.min()), float(lat.max())], ccrs.PlateCarree())

    cbar = fig.colorbar(im, ax=ax, extend="both", fraction=0.046, pad=0.04)
    cbar.set_label("Sea surface temperature (°C)")

    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)


def compose_video(frames_dir: Path, output_mp4: Path, fps: int) -> None:
    frame_glob = str(frames_dir / "frame_*.png")
    cmd = [
        "ffmpeg",
        "-y",
        "-framerate",
        str(fps),
        "-pattern_type",
        "glob",
        "-i",
        frame_glob,
        "-vf",
        "pad=ceil(iw/2)*2:ceil(ih/2)*2",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(output_mp4),
    ]
    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render daily SST frames from NOAA OISST daily NetCDF files and compose MP4."
    )
    parser.add_argument("--month", type=str, help="Month to render in YYYY-MM format")
    parser.add_argument("--start-date", type=date.fromisoformat, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=date.fromisoformat, help="End date (YYYY-MM-DD)")
    parser.add_argument("--daily-dir", type=Path, default=Path("data/daily"))
    parser.add_argument("--frames-dir", type=Path, help="Override default frames dir")
    parser.add_argument("--output-mp4", type=Path, help="Override default output mp4")
    parser.add_argument("--fps", type=int, default=3)
    parser.add_argument(
        "--upscale-factor",
        type=int,
        default=4,
        help="Upscale SST grid before rendering (1 disables upscaling).",
    )
    parser.add_argument(
        "--clean-frames",
        action="store_true",
        help="Delete existing frame_*.png files in frames dir before rendering.",
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Automatically download missing NOAA OISST daily NetCDF files.",
    )
    args = parser.parse_args()

    if args.fps <= 0:
        parser.error("--fps must be greater than 0.")
    if args.upscale_factor <= 0:
        parser.error("--upscale-factor must be greater than 0.")

    if args.month:
        year, month = map(int, args.month.split("-"))
        start_date = date(year, month, 1)
        _, last_day = calendar.monthrange(year, month)
        end_date = date(year, month, last_day)
        default_frames_dir = Path(f"frames/{start_date:%Y_%m}")
        default_output_mp4 = Path(f"output/canary_sst_{start_date:%Y_%m}.mp4")
    elif args.start_date and args.end_date:
        start_date = args.start_date
        end_date = args.end_date
        default_frames_dir = Path(f"frames/{start_date:%Y%m%d}_{end_date:%Y%m%d}")
        default_output_mp4 = Path(f"output/canary_sst_{start_date:%Y%m%d}_{end_date:%Y%m%d}.mp4")
    else:
        parser.error("Either --month or both --start-date and --end-date must be provided.")

    if end_date < start_date:
        parser.error("--end-date must be after --start-date")

    frames_dir = args.frames_dir or default_frames_dir
    output_mp4 = args.output_mp4 or default_output_mp4

    frames_dir.mkdir(parents=True, exist_ok=True)
    output_mp4.parent.mkdir(parents=True, exist_ok=True)
    CARTOPY_DATA_DIR.mkdir(parents=True, exist_ok=True)
    cartopy.config["data_dir"] = str(CARTOPY_DATA_DIR.resolve())

    if args.clean_frames:
        for old_frame in sorted(frames_dir.glob("frame_*.png")):
            old_frame.unlink()

    missing_files: list[Path] = []
    rendered = 0

    for day in generate_dates(start_date, end_date):
        daily_file = args.daily_dir / expected_daily_filename(day)
        frame_path = frames_dir / f"frame_{day:%Y-%m-%d}.png"

        if not daily_file.exists():
            if args.download:
                print(f"Downloading missing data for {day:%Y-%m-%d}...")
                args.daily_dir.mkdir(parents=True, exist_ok=True)
                if not download_noaa_file(day, daily_file):
                    missing_files.append(daily_file)
                    continue
            else:
                missing_files.append(daily_file)
                continue

        print(f"Rendering {day:%Y-%m-%d} from {daily_file} -> {frame_path}")
        render_frame(daily_file, frame_path, day, args.upscale_factor)
        rendered += 1

    print(f"Rendered frames: {rendered}")

    if missing_files:
        print("Missing daily files:")
        for path in missing_files:
            print(f"  - {path}")

    if rendered == 0:
        print("No frames were rendered, skipping MP4 composition.")
        return

    compose_video(frames_dir, output_mp4, args.fps)
    print(f"Animation created: {output_mp4}")


if __name__ == "__main__":
    main()
