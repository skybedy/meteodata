from __future__ import annotations

import argparse
import calendar
import os
import subprocess
from datetime import date, datetime, timedelta
from pathlib import Path

import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import copernicusmarine
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

LAT_MIN, LAT_MAX = 24, 32
LON_MIN, LON_MAX = -20, -10
VMIN, VMAX = 16, 20.5
CARTOPY_DATA_DIR = Path("data/cartopy")

SST_CANDIDATES = ("analysed_sst", "thetao", "sst")
LAT_CANDIDATES = ("latitude", "lat")
LON_CANDIDATES = ("longitude", "lon")
DEFAULT_COPERNICUS_DATASET_ID = "cmems_mod_glo_phy-thetao_anfc_0.083deg_P1D-m"


def generate_dates(start_date: date, end_date: date) -> list[date]:
    delta = end_date - start_date
    return [start_date + timedelta(days=i) for i in range(delta.days + 1)]


def select_existing_name(names: tuple[str, ...], available: list[str], label: str) -> str:
    for name in names:
        if name in available:
            return name
    raise KeyError(f"No supported {label} found. Supported names: {names}; available: {available}")


def fill_nearshore_gaps(sst_subset: xr.DataArray) -> xr.DataArray:
    filled = sst_subset.interpolate_na(dim="longitude", method="nearest", fill_value="extrapolate")
    filled = filled.interpolate_na(dim="latitude", method="nearest", fill_value="extrapolate")
    return filled


def upscale_grid(sst_subset: xr.DataArray, factor: int) -> xr.DataArray:
    if factor <= 1:
        return sst_subset
    lat_new = np.linspace(
        float(sst_subset.latitude.min()),
        float(sst_subset.latitude.max()),
        sst_subset.sizes["latitude"] * factor,
    )
    lon_new = np.linspace(
        float(sst_subset.longitude.min()),
        float(sst_subset.longitude.max()),
        sst_subset.sizes["longitude"] * factor,
    )
    return sst_subset.interp(latitude=lat_new, longitude=lon_new, method="linear")


def open_sst_subset(input_path: Path) -> xr.DataArray:
    with xr.open_dataset(input_path) as ds:
        var_name = select_existing_name(SST_CANDIDATES, list(ds.data_vars), "SST variable")
        lat_name = select_existing_name(LAT_CANDIDATES, list(ds.coords), "latitude coordinate")
        lon_name = select_existing_name(LON_CANDIDATES, list(ds.coords), "longitude coordinate")

        field = ds[var_name]
        for dim in ("time", "depth", "zlev"):
            if dim in field.dims:
                field = field.isel({dim: 0})

        sst = field.rename({lat_name: "latitude", lon_name: "longitude"})
        if float(sst.longitude.max()) > 180:
            sst = sst.assign_coords(longitude=((sst.longitude + 180) % 360) - 180).sortby("longitude")

        return sst.sel(latitude=slice(LAT_MIN, LAT_MAX), longitude=slice(LON_MIN, LON_MAX)).load()


def resolve_copernicus_credentials(username: str | None, password: str | None) -> tuple[str | None, str | None]:
    resolved_username = username or os.getenv("COPERNICUSMARINE_SERVICE_USERNAME") or os.getenv("CMEMS_USERNAME")
    resolved_password = password or os.getenv("COPERNICUSMARINE_SERVICE_PASSWORD") or os.getenv("CMEMS_PASSWORD")
    return resolved_username, resolved_password


def download_copernicus_file(
    day: date,
    daily_dir: Path,
    filename: str,
    dataset_id: str,
    dataset_version: str | None,
    username: str | None,
    password: str | None,
) -> bool:
    start_dt = datetime(day.year, day.month, day.day, 0, 0, 0)
    end_dt = start_dt + timedelta(hours=23, minutes=59, seconds=59)

    daily_dir.mkdir(parents=True, exist_ok=True)

    try:
        copernicusmarine.subset(
            dataset_id=dataset_id,
            dataset_version=dataset_version,
            variables=["thetao"],
            minimum_longitude=LON_MIN,
            maximum_longitude=LON_MAX,
            minimum_latitude=LAT_MIN,
            maximum_latitude=LAT_MAX,
            start_datetime=start_dt.isoformat(),
            end_datetime=end_dt.isoformat(),
            output_directory=str(daily_dir),
            output_filename=filename,
            file_format="netcdf",
            username=username,
            password=password,
            overwrite=True,
            disable_progress_bar=True,
        )
        return True
    except Exception as e:
        print(f"Failed to download Copernicus data for {day:%Y-%m-%d}: {e}")
        dest_path = daily_dir / filename
        if dest_path.exists():
            dest_path.unlink()
        return False


def render_frame(input_path: Path, output_path: Path, day: date, upscale_factor: int) -> None:
    sst_subset = open_sst_subset(input_path)
    sst_filled = fill_nearshore_gaps(sst_subset)
    sst_render = upscale_grid(sst_filled, upscale_factor)

    lon = sst_render.longitude.to_numpy()
    lat = sst_render.latitude.to_numpy()
    values = np.ma.masked_invalid(sst_render.to_numpy())

    cmap = plt.get_cmap("RdYlBu_r").copy()
    cmap.set_bad("#303030")

    fig = plt.figure(figsize=(9, 7), dpi=160)
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_facecolor("#303030")
    im = ax.pcolormesh(
        lon,
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
    ax.set_extent([float(lon.min()), float(lon.max()), float(lat.min()), float(lat.max())], ccrs.PlateCarree())

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
        "-pattern_type",
        "glob",
        "-i",
        str(frames_dir / "frame_*.png"),
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
    parser = argparse.ArgumentParser(description="Render SST animation from Copernicus daily NetCDF files.")
    parser.add_argument("--month", type=str, help="Month to render in YYYY-MM format")
    parser.add_argument("--start-date", type=date.fromisoformat, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=date.fromisoformat, help="End date (YYYY-MM-DD)")
    parser.add_argument("--daily-dir", type=Path, default=Path("data/copernicus/daily"))
    parser.add_argument(
        "--filename-template",
        type=str,
        default="copernicus_sst_{date}.nc",
        help="Template using {date} placeholder in YYYYMMDD format.",
    )
    parser.add_argument("--frames-dir", type=Path, help="Override default frames dir")
    parser.add_argument("--output-mp4", type=Path, help="Override default output mp4")
    parser.add_argument("--fps", type=int, default=3)
    parser.add_argument(
        "--upscale-factor",
        type=int,
        default=2,
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
        help="Automatically download missing Copernicus daily NetCDF files.",
    )
    parser.add_argument(
        "--dataset-id",
        type=str,
        default=DEFAULT_COPERNICUS_DATASET_ID,
        help="Copernicus dataset id used for --download.",
    )
    parser.add_argument(
        "--dataset-version",
        type=str,
        default=None,
        help="Optional Copernicus dataset version for --download.",
    )
    parser.add_argument(
        "--copernicus-username",
        type=str,
        default=None,
        help="Copernicus username (or use COPERNICUSMARINE_SERVICE_USERNAME / CMEMS_USERNAME).",
    )
    parser.add_argument(
        "--copernicus-password",
        type=str,
        default=None,
        help="Copernicus password (or use COPERNICUSMARINE_SERVICE_PASSWORD / CMEMS_PASSWORD).",
    )
    args = parser.parse_args()

    if args.fps <= 0:
        parser.error("--fps must be greater than 0.")
    if args.upscale_factor <= 0:
        parser.error("--upscale-factor must be greater than 0.")
    if "{date}" not in args.filename_template:
        parser.error("--filename-template must include {date}.")
    if args.download and not args.dataset_id:
        parser.error("--dataset-id is required when --download is used.")

    if args.month:
        year, month = map(int, args.month.split("-"))
        start_date = date(year, month, 1)
        _, last_day = calendar.monthrange(year, month)
        end_date = date(year, month, last_day)
        default_frames_dir = Path(f"frames/{start_date:%Y_%m}_copernicus")
        default_output_mp4 = Path(f"output/canary_sst_{start_date:%Y_%m}_copernicus.mp4")
    elif args.start_date and args.end_date:
        start_date = args.start_date
        end_date = args.end_date
        default_frames_dir = Path(f"frames/{start_date:%Y%m%d}_{end_date:%Y%m%d}_copernicus")
        default_output_mp4 = Path(f"output/canary_sst_{start_date:%Y%m%d}_{end_date:%Y%m%d}_copernicus.mp4")
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

    resolved_username: str | None = None
    resolved_password: str | None = None
    if args.download:
        resolved_username, resolved_password = resolve_copernicus_credentials(
            args.copernicus_username,
            args.copernicus_password,
        )
        if not resolved_username or not resolved_password:
            parser.error(
                "Copernicus credentials are required for --download. "
                "Use --copernicus-username/--copernicus-password "
                "or set COPERNICUSMARINE_SERVICE_USERNAME and COPERNICUSMARINE_SERVICE_PASSWORD."
            )

    rendered = 0
    missing: list[Path] = []
    for day in generate_dates(start_date, end_date):
        filename = args.filename_template.format(date=f"{day:%Y%m%d}")
        daily_file = args.daily_dir / filename
        frame_path = frames_dir / f"frame_{day:%Y-%m-%d}.png"

        if not daily_file.exists():
            if args.download:
                print(f"Downloading missing Copernicus data for {day:%Y-%m-%d}...")
                if not download_copernicus_file(
                    day=day,
                    daily_dir=args.daily_dir,
                    filename=filename,
                    dataset_id=args.dataset_id,
                    dataset_version=args.dataset_version,
                    username=resolved_username,
                    password=resolved_password,
                ):
                    missing.append(daily_file)
                    continue
            else:
                missing.append(daily_file)
                continue

        print(f"Rendering {day:%Y-%m-%d}: {daily_file}")
        render_frame(daily_file, frame_path, day, args.upscale_factor)
        rendered += 1

    print(f"Rendered frames: {rendered}")
    if missing:
        print("Missing daily files:")
        for path in missing:
            print(f"  - {path}")

    if rendered == 0:
        print("No frames were rendered, skipping MP4 composition.")
        return

    compose_video(frames_dir, output_mp4, args.fps)
    print(f"Animation created: {output_mp4}")


if __name__ == "__main__":
    main()
