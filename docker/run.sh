#!/usr/bin/env bash
# Run the CSC477 wall-following stack (ROS 2 Humble / Gazebo Fortress) in a
# container, with GUI on the host's X display and hardware rendering via
# /dev/dri. Use this on hosts that aren't Ubuntu 22.04.
#
#   ./run.sh build    build (or rebuild) the image
#   ./run.sh up       start the long-lived container in the background
#   ./run.sh shell    open a shell in it (starting it first if needed)
#   ./run.sh down     stop and remove it
#
# The repository is bind-mounted at ~/csc477_ws/src/assignment1 inside the
# container (the same layout as on the lab machines), so edits on the host are
# immediately visible inside; colcon's build/install/log live in ./ws on the
# host and survive `down`.
set -euo pipefail

DOCKER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$DOCKER_DIR/.." && pwd)"
HOST_WS="$DOCKER_DIR/ws"
IMAGE=csc477:humble
CONTAINER=csc477

build() {
  docker build -t "$IMAGE" "$DOCKER_DIR"
}

# Grant the container's X client a cookie for the host display. Copied rather
# than mounted in place because the compositor's auth file is mode 0600 and
# named unpredictably (mutter randomizes the suffix on each session).
prepare_xauth() {
  local xauth="$DOCKER_DIR/.xauth"
  rm -f "$xauth"
  touch "$xauth"
  # FamilyWild (ffff) so the cookie matches regardless of how the container
  # resolves the display's hostname.
  xauth nlist "${DISPLAY:-:0}" | sed -e 's/^..../ffff/' | xauth -f "$xauth" nmerge - 2>/dev/null
  chmod 644 "$xauth"
  echo "$xauth"
}

up() {
  if docker ps -a --format '{{.Names}}' | grep -qx "$CONTAINER"; then
    docker start "$CONTAINER" > /dev/null
    return
  fi

  mkdir -p "$HOST_WS/src"
  local xauth
  xauth="$(prepare_xauth)"

  docker run -d --name "$CONTAINER" \
    --network host \
    --ipc host \
    --device /dev/dri \
    -e "DISPLAY=${DISPLAY:-:0}" \
    -e XAUTHORITY=/root/.Xauthority \
    -e QT_X11_NO_MITSHM=1 \
    -e LIBGL_ALWAYS_SOFTWARE=0 \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    -v "$xauth:/root/.Xauthority:rw" \
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
