#!/bin/bash
# This is a script to run build_live when a specified file is modified. Its intent is to save clicks.
# If no file to watch is specified then it watches the whole project.

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"
cd "$REPO_ROOT" || exit 1
LIVE="$(python3 -c 'import json; print(json.load(open("config.json"))["live"])')"
case "$LIVE" in
	/*) ;;
	*) LIVE="$REPO_ROOT/$LIVE";;
esac
SERVER_PID=""
WATCH_PID=""
CHANGES_FILE="$(mktemp "${TMPDIR:-/tmp}/auto_build_changes.XXXXXX")" || exit 1

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
	rm -f "$CHANGES_FILE"
}

trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

case "$1" in
	"")
		watch="$REPO_ROOT";;
	*)
		echo "watching $1"
		case "$1" in
			/*)
				watch="$1";;
			*)
				watch="$REPO_ROOT/$1";;
		esac;;
esac

WATCH_EXCLUDE='(^|/)(node_modules|\.git)(/|$)'
if command -v inotifywait >/dev/null 2>&1; then
	watch_for_change() {
		inotifywait --quiet --recursive \
			--exclude "$WATCH_EXCLUDE" \
			--event modify,create,delete,move \
			--format '%w%f' \
			"$watch"
	}
elif command -v fswatch >/dev/null 2>&1; then
	watch_for_change() {
		fswatch -1 -r -E --exclude "$WATCH_EXCLUDE" "$watch"
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
	: > "$CHANGES_FILE"
	watch_for_change > "$CHANGES_FILE" &
	WATCH_PID=$!
	wait "$WATCH_PID"
	watch_status=$?
	WATCH_PID=""
	if [ "$watch_status" -ne 0 ]; then
		exit "$watch_status"
	fi
	echo "Rebuilding after changes to:"
	sort -u "$CHANGES_FILE" | while IFS= read -r changed
	do
		case "$changed" in
			"$REPO_ROOT"/*) changed="${changed#"$REPO_ROOT"/}";;
		esac
		printf '  %s\n' "$changed"
	done
	cd "$REPO_ROOT" || exit 1
	"$SCRIPT_DIR/build_live.sh"
        echo "Build complete"
	cd "$LIVE" || exit 1
done
