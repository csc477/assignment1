#!/usr/bin/env bash
# Fully tear down a wall-following sim run.
#
# Kills the Gazebo server/GUI, the Clearpath nodes, rviz2, any controller, AND
# the ros_gz parameter_bridge processes. The bridges matter: they do not die
# with the launch process group, and an orphan re-attaches to the next Gazebo
# you start and duplicates every topic (see the troubleshooting section of
# ros2/docs/lab_setup.md).
#
# Re-run until it reports no survivors, then relaunch.
set -uo pipefail

PAT='ign gazebo|ruby|parameter_bridge|rviz2|wall_follower|twist_mux|ekf_node'
PAT="$PAT"'|robot_state_publisher|marker_server|teleop_node|joy_linux'
PAT="$PAT"'|ros2 launch|static_transform'

# The self-exclusions are the fiddly part. The pattern above appears in this
# script's own command line and in the `grep -E` that scans for it, so without
# filtering, a naive `pkill -f` kills the shell running the teardown (leaving
# the job half done) and this function reports its own pipeline as a survivor.
# Excluded: zombies (already dead, unreapable here), this script, the scanning
# pipeline itself, and this shell.
survivors() {
  ps -eo pid,stat,args \
    | grep -E "$PAT" \
    | grep -v ' Z ' \
    | grep -Ev 'teardown|grep -E|ps -eo' \
    | awk -v self="$$" '$1 != self {print $1}'
}

for _ in 1 2 3; do
  pids="$(survivors)"
  [ -z "$pids" ] && break
  # shellcheck disable=SC2086
  kill -9 $pids 2>/dev/null
  sleep 3
done

remaining="$(survivors)"
if [ -n "$remaining" ]; then
  echo "WARNING: processes still alive:" >&2
  ps -o pid,args -p "$(echo "$remaining" | tr '\n' ',' | sed 's/,$//')" >&2
  exit 1
fi

echo "teardown complete: no survivors"
