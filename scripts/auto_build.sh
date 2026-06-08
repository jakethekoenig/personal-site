#!/bin/bash
# This is a script to run build_live when a specified file is modified. Its intent is to save clicks.
# If no file to watch is specified then it watches the whole project.

RUN_DIR=$(pwd)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LIVE="$RUN_DIR/../live"
SERVER_PID=""
WATCH_PID=""

cleanup() {
	trap - EXIT INT TERM
	if [ -n "$WATCH_PID" ] && kill -0 "$WATCH_PID" 2>/dev/null; then
		kill "$WATCH_PID" 2>/dev/null
		wait "$WATCH_PID" 2>/dev/null
	fi
	if [ -n "$SERVER_PID" ] && kill -0 "$SERVER_PID" 2>/dev/null; then
		kill "$SERVER_PID" 2>/dev/null
		wait "$SERVER_PID" 2>/dev/null
	fi
}

trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

case "$1" in
	"")
		watch="$RUN_DIR";;
	*)
		echo "watching $1"
		case "$1" in
			/*)
				watch="$1";;
			*)
				watch="$RUN_DIR/$1";;
		esac;;
esac

if command -v inotifywait >/dev/null 2>&1; then
	watch_for_change() {
		inotifywait -r --event modify,create,delete,move "$watch" >/dev/null
	}
elif command -v fswatch >/dev/null 2>&1; then
	watch_for_change() {
		fswatch -1 -r "$watch" >/dev/null
	}
else
	echo "auto_build requires inotifywait on Linux or fswatch on macOS."
	echo "On macOS, install fswatch with: brew install fswatch"
	exit 1
fi

mkdir -p "$LIVE"
cd "$LIVE" || exit 1

python3 "$SCRIPT_DIR/local_server.py" > /dev/null &
SERVER_PID=$!
while true
do
	watch_for_change &
	WATCH_PID=$!
	wait "$WATCH_PID"
	watch_status=$?
	WATCH_PID=""
	if [ "$watch_status" -ne 0 ]; then
		exit "$watch_status"
	fi
	cd "$RUN_DIR" || exit 1
	"$SCRIPT_DIR/build_live.sh"
	cd "$LIVE" || exit 1
done
