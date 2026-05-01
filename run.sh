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

MONTH="${1:-2026-03}"
shift || true

exec .venv/bin/python make_animation_copernicus.py \
  --month "${MONTH}" \
  --download \
  --clean-frames \
  --fps 3 \
  --upscale-factor 2 \
  "$@"
