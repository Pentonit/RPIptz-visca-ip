#!/usr/bin/env bash
# Quick re-download script for RPIptz-visca-ip
# Removes the existing project directory, clones fresh from GitHub, and runs run.sh

set -euo pipefail

REPO_URL=${REPO_URL:-"https://github.com/Pentonit/RPIptz-visca-ip.git"}

# Usage: redownload.sh [target_dir] [branch]
TARGET_DIR=${1:-}
BRANCH=${2:-main}

if ! command -v git >/dev/null 2>&1; then
  echo "git is required but not installed. Please install git and re-run." >&2
  exit 1
fi

# Resolve default target dir
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_PARENT_DIR="$(dirname "$SCRIPT_DIR")"
DEFAULT_REPO_NAME="RPIptz-visca-ip"
if [[ -z "${TARGET_DIR}" ]]; then
  TARGET_DIR="${DEFAULT_PARENT_DIR}/${DEFAULT_REPO_NAME}"
fi

echo "Repo URL : ${REPO_URL}"
echo "Branch   : ${BRANCH}"
echo "Target   : ${TARGET_DIR}"

# If running from inside the target repo, clone to a temp dir, then swap
if [[ "$SCRIPT_DIR" == "$TARGET_DIR" ]]; then
  TMP_DIR="${TARGET_DIR}.tmp.$RANDOM"
  echo "Cloning fresh copy to ${TMP_DIR}..."
  git clone --depth 1 --branch "$BRANCH" "$REPO_URL" "$TMP_DIR"
  echo "Removing old directory: ${TARGET_DIR}"
  rm -rf "$TARGET_DIR"
  echo "Moving fresh copy into place..."
  mv "$TMP_DIR" "$TARGET_DIR"
else
  echo "Removing old directory: ${TARGET_DIR} (if exists)"
  rm -rf "$TARGET_DIR"
  echo "Cloning fresh copy to ${TARGET_DIR}..."
  git clone --depth 1 --branch "$BRANCH" "$REPO_URL" "$TARGET_DIR"
fi

cd "$TARGET_DIR"
chmod +x run.sh || true
echo "Starting application..."
./run.sh


