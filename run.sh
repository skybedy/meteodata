#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [[ ! -f ".venv/bin/python" ]]; then
  echo "Missing .venv. Create it and install dependencies first:"
  echo "  python3 -m venv .venv"
  echo "  source .venv/bin/activate"
  echo "  pip install -r requirements.txt"
  exit 1
fi

if [[ -f ".env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source ".env"
  set +a
fi

if [[ -z "${COPERNICUSMARINE_SERVICE_USERNAME:-}" || -z "${COPERNICUSMARINE_SERVICE_PASSWORD:-}" ]]; then
  echo "Missing Copernicus credentials."
  echo "Set COPERNICUSMARINE_SERVICE_USERNAME and COPERNICUSMARINE_SERVICE_PASSWORD in .env."
  exit 1
fi

MONTH=""
if [[ $# -gt 0 && "${1}" != --* ]]; then
  MONTH="${1}"
  shift
fi

HAS_DATE_RANGE=0
for arg in "$@"; do
  if [[ "${arg}" == "--start-date" || "${arg}" == "--end-date" ]]; then
    HAS_DATE_RANGE=1
    break
  fi
done

MONTH_ARGS=()
DATE_RANGE_ARGS=()
if [[ -n "${MONTH}" ]]; then
  MONTH_ARGS=(--month "${MONTH}")
elif [[ "${HAS_DATE_RANGE}" -eq 0 ]]; then
  FIRST_FILE="$(ls -1 data/copernicus/daily/copernicus_sst_*.nc 2>/dev/null | head -n 1 || true)"
  LAST_FILE="$(ls -1 data/copernicus/daily/copernicus_sst_*.nc 2>/dev/null | tail -n 1 || true)"

  if [[ -n "${FIRST_FILE}" && -n "${LAST_FILE}" ]]; then
    FIRST_BASENAME="$(basename "${FIRST_FILE}")"
    LAST_BASENAME="$(basename "${LAST_FILE}")"
    START_DATE="${FIRST_BASENAME#copernicus_sst_}"
    START_DATE="${START_DATE%.nc}"
    END_DATE="${LAST_BASENAME#copernicus_sst_}"
    END_DATE="${END_DATE%.nc}"
    DATE_RANGE_ARGS=(
      --start-date "${START_DATE:0:4}-${START_DATE:4:2}-${START_DATE:6:2}"
      --end-date "${END_DATE:0:4}-${END_DATE:4:2}-${END_DATE:6:2}"
    )
    echo "No month/date provided, using available history: ${DATE_RANGE_ARGS[1]} -> ${DATE_RANGE_ARGS[3]}"
  else
    MONTH_ARGS=(--month "$(date +%Y-%m)")
    echo "No history files found, falling back to current month: ${MONTH_ARGS[1]}"
  fi
fi

exec .venv/bin/python make_animation_copernicus.py \
  "${MONTH_ARGS[@]}" \
  "${DATE_RANGE_ARGS[@]}" \
  --download \
  --clean-frames \
  --fps 3 \
  --upscale-factor 2 \
  --labels \
  --africa-label "Africa" \
  --watermark-text "https://tene.life" \
  --watermark-alpha 0.95 \
  "$@"
