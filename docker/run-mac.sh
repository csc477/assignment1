#!/usr/bin/env bash
# macOS variant of run.sh: run the CSC477 wall-following stack (ROS 2 Humble /
# Gazebo Fortress) in a container, with the GUI shown through XQuartz.
#
#   ./run-mac.sh build    build (or rebuild) the image
#   ./run-mac.sh up       start the long-lived container in the background
#   ./run-mac.sh shell    open a shell in it (starting it first if needed)
#   ./run-mac.sh down     stop and remove it
#
# Needs Docker Desktop and XQuartz (https://www.xquartz.org). The first run
# switches on XQuartz's "Allow connections from network clients" setting and
# restarts XQuartz; after that the script only starts XQuartz if needed and
# allows local clients with xhost.
#
# Differences from run.sh (Linux):
#   - X11 goes over TCP to XQuartz on the host (DISPLAY=host.docker.internal:0)
#     instead of a mounted Unix socket and cookie;
#   - no GPU passthrough: everything renders in software (LIBGL_ALWAYS_SOFTWARE),
#     which is slower but sufficient for this assignment;
#   - no --network host / --ipc host (not supported by Docker Desktop);
#   - Apple Silicon builds a native arm64 image, Intel Macs amd64.
#
# The repository is bind-mounted at ~/csc477_ws/src/assignment1 inside the
# container (same layout as on the lab machines); colcon's build/install/log
# live in ./ws on the host and survive `down`.
set -euo pipefail

DOCKER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$DOCKER_DIR/.." && pwd)"
HOST_WS="$DOCKER_DIR/ws"
IMAGE=csc477:humble
CONTAINER=csc477
XHOST=/opt/X11/bin/xhost

die() { echo "run-mac.sh: $*" >&2; exit 1; }

require_docker() {
  command -v docker > /dev/null 2>&1 \
    || die "docker not found. Install Docker Desktop: https://docs.docker.com/desktop/setup/install/mac-install/"
  docker info > /dev/null 2>&1 \
    || die "the Docker daemon is not running. Start Docker Desktop and retry."
  # Gazebo + rviz2 + colcon build want a few GB. Docker Desktop's default is
  # often too small; the limit lives in Settings > Resources.
  local mem
  mem="$(docker info --format '{{.MemTotal}}' 2> /dev/null || echo 0)"
  if [ "${mem:-0}" -gt 0 ] && [ "$mem" -lt $((6 * 1024 * 1024 * 1024)) ]; then
    echo "warning: Docker Desktop has $((mem / 1024 / 1024 / 1024)) GB of memory;" \
         "give it at least 6 GB (Settings > Resources) if builds or Gazebo get killed." >&2
  fi
}

build() {
  require_docker
  docker build -t "$IMAGE" "$DOCKER_DIR"
}

# Make sure XQuartz is installed, accepts TCP connections, is running, and
# allows clients from this machine (which is where Docker Desktop's port
# forwarding makes the container's connections appear to come from).
prepare_xquartz() {
  [ -x "$XHOST" ] \
    || die "XQuartz not found. Install it from https://www.xquartz.org (or 'brew install --cask xquartz'), log out and back in, then retry."

  if [ "$(defaults read org.xquartz.X11 nolisten_tcp 2> /dev/null || echo 1)" != "0" ]; then
    defaults write org.xquartz.X11 nolisten_tcp -bool false
    echo "Enabled 'Allow connections from network clients' in XQuartz (one-time); restarting it."
    osascript -e 'quit app "XQuartz"' > /dev/null 2>&1 || true
    sleep 2
  fi

  open -a XQuartz   # no-op if it is already running

  # launchd normally exports DISPLAY for XQuartz; fall back to the usual
  # names if this shell predates the XQuartz install.
  local d
  for _ in $(seq 1 30); do
    for d in "${DISPLAY:-}" :0 localhost:0; do
      [ -n "$d" ] || continue
      if DISPLAY="$d" "$XHOST" > /dev/null 2>&1; then
        export DISPLAY="$d"
        DISPLAY="$d" "$XHOST" +localhost > /dev/null
        DISPLAY="$d" "$XHOST" +127.0.0.1 > /dev/null
        return
      fi
    done
    sleep 1
  done
  die "XQuartz did not come up (xhost cannot reach it). Start XQuartz by hand, then retry."
}

up() {
  require_docker
  if docker ps -a --format '{{.Names}}' | grep -qx "$CONTAINER"; then
    prepare_xquartz
    docker start "$CONTAINER" > /dev/null
    return
  fi

  docker image inspect "$IMAGE" > /dev/null 2>&1 \
    || die "image $IMAGE not found; run './run-mac.sh build' first."
  prepare_xquartz
  mkdir -p "$HOST_WS/src"

  docker run -d --name "$CONTAINER" \
    --shm-size=1g \
    -e DISPLAY=host.docker.internal:0 \
    -e LIBGL_ALWAYS_SOFTWARE=1 \
    -e QT_X11_NO_MITSHM=1 \
    -v "$HOST_WS:/root/csc477_ws:rw" \
    -v "$REPO_DIR:/root/csc477_ws/src/assignment1:rw" \
    "$IMAGE" sleep infinity > /dev/null
}

shell() {
  up
  docker exec -it "$CONTAINER" bash
}

down() {
  docker rm -f "$CONTAINER" 2> /dev/null || true
}

case "${1:-shell}" in
  build) build ;;
  up)    up ;;
  shell) shell ;;
  down)  down ;;
  *) echo "usage: $0 {build|up|shell|down}" >&2; exit 1 ;;
esac
