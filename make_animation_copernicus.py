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
import matplotlib.patheffects as pe
import numpy as np
import xarray as xr

REGION_BBOXES: dict[str, tuple[float, float, float, float]] = {
    "canary": (24.0, 32.0, -20.0, -10.0),
    "tenerife": (27.9, 28.7, -17.1, -16.0),
}
DEFAULT_VMIN, DEFAULT_VMAX = 17, 26
CARTOPY_DATA_DIR = Path("data/cartopy")

SST_CANDIDATES = ("analysed_sst", "thetao", "sst")
LAT_CANDIDATES = ("latitude", "lat")
LON_CANDIDATES = ("longitude", "lon")
DEFAULT_COPERNICUS_DATASET_ID = "cmems_mod_glo_phy-thetao_anfc_0.083deg_P1D-m"

ISLAND_LABELS = [
    ("La Palma", -17.86, 28.68, -18.85, 29.42),
    ("El Hierro", -17.99, 27.73, -18.95, 27.20),
    ("La Gomera", -17.25, 28.09, -18.95, 28.05),
    ("Gran Canaria", -15.60, 27.96, -16.95, 27.35),
    ("Fuerteventura", -14.03, 28.36, -15.25, 29.05),
    ("Lanzarote", -13.64, 29.04, -14.90, 29.85),
]


def generate_dates(start_date: date, end_date: date) -> list[date]:
    delta = end_date - start_date
    return [start_date + timedelta(days=i) for i in range(delta.days + 1)]


def parse_month_arg(month_arg: str, parser: argparse.ArgumentParser) -> tuple[date, date]:
    try:
        year, month = map(int, month_arg.split("-"))
        start_date = date(year, month, 1)
    except ValueError:
        parser.error("--month must be in YYYY-MM format.")
    _, last_day = calendar.monthrange(start_date.year, start_date.month)
    end_date = date(start_date.year, start_date.month, last_day)
    return start_date, end_date


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


def open_sst_subset(input_path: Path, lat_min: float, lat_max: float, lon_min: float, lon_max: float) -> xr.DataArray:
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

        return sst.sel(latitude=slice(lat_min, lat_max), longitude=slice(lon_min, lon_max)).load()


def resolve_copernicus_credentials(username: str | None, password: str | None) -> tuple[str | None, str | None]:
    resolved_username = username or os.getenv("COPERNICUSMARINE_SERVICE_USERNAME") or os.getenv("CMEMS_USERNAME")
    resolved_password = password or os.getenv("COPERNICUSMARINE_SERVICE_PASSWORD") or os.getenv("CMEMS_PASSWORD")
    return resolved_username, resolved_password


def download_copernicus_file(
    day: date,
    daily_dir: Path,
    filename: str,
    lat_min: float,
    lat_max: float,
    lon_min: float,
    lon_max: float,
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
            minimum_longitude=lon_min,
            maximum_longitude=lon_max,
            minimum_latitude=lat_min,
            maximum_latitude=lat_max,
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


def add_map_labels(ax: plt.Axes, africa_label: str) -> None:
    text_effects = [pe.withStroke(linewidth=2.2, foreground="#111111")]
    extent = ax.get_extent(crs=ccrs.PlateCarree())
    lon_min, lon_max, lat_min, lat_max = extent

    for name, lon, lat, tx, ty in ISLAND_LABELS:
        # Only draw if the target island coordinates are within the current view
        if lon_min <= lon <= lon_max and lat_min <= lat <= lat_max:
            ax.annotate(
                name,
                xy=(lon, lat),
                xytext=(tx, ty),
                xycoords=ccrs.PlateCarree()._as_mpl_transform(ax),
                textcoords=ccrs.PlateCarree()._as_mpl_transform(ax),
                fontsize=8.5,
                color="#f3efe6",
                weight="semibold",
                ha="left",
                va="center",
                path_effects=text_effects,
                arrowprops={
                    "arrowstyle": "-",
                    "color": "#1f2933",
                    "lw": 1.0,
                    "alpha": 0.95,
                },
                zorder=6,
            )

    if lon_max > -14.0:
        ax.text(
            -12.2,
            26.6,
            africa_label,
            transform=ccrs.PlateCarree(),
            fontsize=14,
            color="#ffffff",
            weight="bold",
            ha="center",
            va="center",
            alpha=0.95,
            path_effects=text_effects,
            zorder=6,
        )


def add_watermark(ax: plt.Axes, text: str, alpha: float) -> None:
    if not text:
        return
    ax.text(
        0.98,
        0.02,
        text,
        transform=ax.transAxes,
        fontsize=11.5,
        color="#ffffff",
        weight="semibold",
        ha="right",
        va="bottom",
        alpha=alpha,
        path_effects=[pe.withStroke(linewidth=2.0, foreground="#111111")],
        zorder=7,
    )


def render_frame(
    input_path: Path,
    output_path: Path,
    day: date,
    lat_min: float,
    lat_max: float,
    lon_min: float,
    lon_max: float,
    region_label: str,
    upscale_factor: int,
    add_labels: bool,
    africa_label: str,
    watermark_text: str,
    watermark_alpha: float,
    vmin: float,
    vmax: float,
) -> None:
    sst_subset = open_sst_subset(input_path, lat_min=lat_min, lat_max=lat_max, lon_min=lon_min, lon_max=lon_max)
    sst_filled = fill_nearshore_gaps(sst_subset)
    sst_render = upscale_grid(sst_filled, upscale_factor)

    lon = sst_render.longitude.to_numpy()
    lat = sst_render.latitude.to_numpy()
    values = np.ma.masked_invalid(sst_render.to_numpy())

    cmap = plt.get_cmap("RdYlBu_r").copy()
    cmap.set_bad("#303030")

    fig = plt.figure(figsize=(9, 6), dpi=160)
    ax = fig.add_axes([0.08, 0.12, 0.78, 0.82], projection=ccrs.PlateCarree())
    ax.set_facecolor("#303030")
    im = ax.pcolormesh(
        lon,
        lat,
        values,
        transform=ccrs.PlateCarree(),
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        shading="auto",
    )

    land = cfeature.NaturalEarthFeature(
        "physical",
        "land",
        "10m",
        edgecolor="face",
        facecolor="#252525",
    )
    ax.add_feature(land, linewidth=0.55, zorder=3)
    ax.add_feature(cfeature.COASTLINE.with_scale("10m"), linewidth=0.35, edgecolor="#f5f0e6", zorder=4)
    ax.set_title(
        f"Sea Surface Temperature - {region_label} - {day:%Y-%m-%d} - Data: Copernicus Marine",
        pad=10,
        fontsize=13,
        weight="semibold",
    )
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
    if add_labels:
        add_map_labels(ax, africa_label)
    add_watermark(ax, watermark_text, watermark_alpha)

    cbar_ax = fig.add_axes([0.88, 0.15, 0.02, 0.7])
    cbar = fig.colorbar(im, cax=cbar_ax, extend="both")
    cbar.set_label("Sea surface temperature (°C)")
    
    fig.savefig(output_path)

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
        "--speed-factor",
        type=float,
        default=1.0,
        help="Playback speed multiplier for output video (e.g. 2.0 = half duration).",
    )
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
    parser.add_argument(
        "--region",
        type=str,
        default="canary",
        choices=sorted(REGION_BBOXES.keys()),
        help="Map region extent preset.",
    )
    parser.add_argument(
        "--labels",
        action="store_true",
        help="Draw island labels and Africa label on the map.",
    )
    parser.add_argument(
        "--africa-label",
        type=str,
        default="Africa",
        help="Label text for the African mainland.",
    )
    parser.add_argument(
        "--watermark-text",
        type=str,
        default="",
        help="Optional watermark text shown in the lower-right dark mainland area.",
    )
    parser.add_argument(
        "--watermark-alpha",
        type=float,
        default=0.78,
        help="Watermark opacity from 0 to 1.",
    )
    parser.add_argument(
        "--vmin",
        type=float,
        default=DEFAULT_VMIN,
        help="Minimum temperature for the color scale (°C).",
    )
    parser.add_argument(
        "--vmax",
        type=float,
        default=DEFAULT_VMAX,
        help="Maximum temperature for the color scale (°C).",
    )
    parser.add_argument(
        "--export-metadata",
        action="store_true",
        help="Export metadata.json with date-to-frame mapping in the frames directory.",
    )
    args = parser.parse_args()

    if args.fps <= 0:
        parser.error("--fps must be greater than 0.")
    if args.speed_factor <= 0:
        parser.error("--speed-factor must be greater than 0.")
    if args.upscale_factor <= 0:
        parser.error("--upscale-factor must be greater than 0.")
    if "{date}" not in args.filename_template:
        parser.error("--filename-template must include {date}.")
    if args.download and not args.dataset_id:
        parser.error("--dataset-id is required when --download is used.")
    if not (0 <= args.watermark_alpha <= 1):
        parser.error("--watermark-alpha must be between 0 and 1.")

    if args.month:
        start_date, end_date = parse_month_arg(args.month, parser)
        default_frames_dir = Path(f"frames/{start_date:%Y_%m}_{args.region}_copernicus")
        default_output_mp4 = Path(f"output/{args.region}_sst_{start_date:%Y_%m}_copernicus.mp4")
    elif args.start_date and args.end_date:
        start_date = args.start_date
        end_date = args.end_date
        default_frames_dir = Path(f"frames/{start_date:%Y%m%d}_{end_date:%Y%m%d}_{args.region}_copernicus")
        default_output_mp4 = Path(f"output/{args.region}_sst_{start_date:%Y%m%d}_{end_date:%Y%m%d}_copernicus.mp4")
    else:
        parser.error("Either --month or both --start-date and --end-date must be provided.")

    if end_date < start_date:
        parser.error("--end-date must be after --start-date")

    frames_dir = args.frames_dir or default_frames_dir
    output_mp4 = args.output_mp4 or default_output_mp4
    lat_min, lat_max, lon_min, lon_max = REGION_BBOXES[args.region]

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
    metadata_entries = []
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
                    lat_min=lat_min,
                    lat_max=lat_max,
                    lon_min=lon_min,
                    lon_max=lon_max,
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
        render_frame(
            daily_file,
            frame_path,
            day,
            upscale_factor=args.upscale_factor,
            lat_min=lat_min,
            lat_max=lat_max,
            lon_min=lon_min,
            lon_max=lon_max,
            region_label=args.region.capitalize(),
            add_labels=args.labels,
            africa_label=args.africa_label,
            watermark_text=args.watermark_text,
            watermark_alpha=args.watermark_alpha,
            vmin=args.vmin,
            vmax=args.vmax,
        )
        metadata_entries.append({"date": day.isoformat(), "frame": frame_path.name})
        rendered += 1

    print(f"Rendered frames: {rendered}")
    if missing:
        print("Missing daily files:")
        for path in missing:
            print(f"  - {path}")

    if args.export_metadata and metadata_entries:
        import json

        metadata_path = frames_dir / "metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump({"region": args.region, "vmin": args.vmin, "vmax": args.vmax, "frames": metadata_entries}, f, indent=2)
        print(f"Metadata exported: {metadata_path}")

    if rendered == 0:
        print("No frames were rendered, skipping MP4 composition.")
        return

    effective_fps = max(1, int(round(args.fps * args.speed_factor)))
    print(f"Composing MP4 at {effective_fps} fps (base {args.fps} * speed-factor {args.speed_factor}).")
    compose_video(frames_dir, output_mp4, effective_fps)
    print(f"Animation created: {output_mp4}")


if __name__ == "__main__":
    main()
