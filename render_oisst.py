from pathlib import Path

import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

INPUT_PATH = Path("data/oisst.nc")
OUTPUT_DIR = Path("output")
OUTPUT_PATH = OUTPUT_DIR / "canary_sst_2024-03-01.png"
TITLE_DATE = "2024-03-01"

LAT_MIN, LAT_MAX = 24, 32
LON_MIN, LON_MAX = 340, 350
VMIN, VMAX = 16, 20.5
CARTOPY_DATA_DIR = Path("data/cartopy")


def to_west_longitudes(lon: xr.DataArray) -> np.ndarray:
    return ((lon.to_numpy() + 180) % 360) - 180


def main() -> None:
    if not INPUT_PATH.exists():
        print("Chyba: chybí vstupní NetCDF soubor data/oisst.nc")
        print("Vlož prosím NOAA OISST soubor do data/oisst.nc a spusť skript znovu.")
        return

    ds = xr.open_dataset(INPUT_PATH)
    sst = ds["sst"].isel(time=0, zlev=0)

    # NOAA OISST longitudes are in 0..360.
    sst_canary = sst.sel(lat=slice(LAT_MIN, LAT_MAX), lon=slice(LON_MIN, LON_MAX))
    lon_west = to_west_longitudes(sst_canary.lon)
    lat = sst_canary.lat.to_numpy()
    values = np.ma.masked_invalid(sst_canary.to_numpy())

    print(f"shape: {sst_canary.shape}")
    print(f"lat range: {float(sst_canary.lat.min().values):.3f} .. {float(sst_canary.lat.max().values):.3f}")
    print(f"lon range: {float(sst_canary.lon.min().values):.3f} .. {float(sst_canary.lon.max().values):.3f}")
    print(f"min °C: {float(sst_canary.min().values):.3f}")
    print(f"max °C: {float(sst_canary.max().values):.3f}")
    print(f"mean °C: {float(sst_canary.mean().values):.3f}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CARTOPY_DATA_DIR.mkdir(parents=True, exist_ok=True)
    cartopy.config["data_dir"] = str(CARTOPY_DATA_DIR.resolve())

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

    ax.set_title(f"Sea Surface Temperature - Canary Islands - {TITLE_DATE}", pad=12)
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
    fig.savefig(OUTPUT_PATH, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
