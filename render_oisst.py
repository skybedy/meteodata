from pathlib import Path

import matplotlib.pyplot as plt
import xarray as xr

INPUT_PATH = Path("data/oisst.nc")
OUTPUT_DIR = Path("output")
OUTPUT_PATH = OUTPUT_DIR / "canary_sst_2024-03-01.png"

LAT_MIN, LAT_MAX = 24, 32
LON_MIN, LON_MAX = 340, 350


def main() -> None:
    ds = xr.open_dataset(INPUT_PATH)
    sst = ds["sst"].isel(time=0, zlev=0)

    # NOAA OISST longitudes are in 0..360.
    sst_canary = sst.sel(lat=slice(LAT_MIN, LAT_MAX), lon=slice(LON_MIN, LON_MAX))

    print(f"shape: {sst_canary.shape}")
    print(f"lat range: {float(sst_canary.lat.min().values):.3f} .. {float(sst_canary.lat.max().values):.3f}")
    print(f"lon range: {float(sst_canary.lon.min().values):.3f} .. {float(sst_canary.lon.max().values):.3f}")
    print(f"min °C: {float(sst_canary.min().values):.3f}")
    print(f"max °C: {float(sst_canary.max().values):.3f}")
    print(f"mean °C: {float(sst_canary.mean().values):.3f}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8, 6))
    im = plt.pcolormesh(sst_canary.lon, sst_canary.lat, sst_canary, cmap="turbo", vmin=16, vmax=22)
    plt.title("Sea Surface Temperature - Canary Islands - 2024-03-01")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    cbar = plt.colorbar(im)
    cbar.set_label("Sea surface temperature (°C)")
    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, dpi=150)
    plt.close()


if __name__ == "__main__":
    main()
