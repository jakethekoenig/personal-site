#!/bin/bash
# This is a script to run build_live when a specified file is modified. It's intent is to save clicks.
# If no file to watch is specified than it simply watches the whole project.

RUN_DIR=$(pwd)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LIVE="$RUN_DIR/../live"
trap "kill 0" EXIT

watch=""
case "$1" in
	"")
		watch="$RUN_DIR/*";;
	*)
		echo watching $1
		watch=$1;;
esac

mkdir $LIVE
cd $LIVE

while true
do
	python3 $SCRIPT_DIR/local_server.py > /dev/null &
	inotifywait -r --event modify $watch
	kill %1
	cd $RUN_DIR
	#TODO: fit the auto_card script into the rest of the build process.
	#python3 scripts/my_auto_card.py temp.html content/blog/khm.html
	$SCRIPT_DIR/build_live.sh
	cd $LIVE
	MYWINDOW=$(xdotool getactivewindow)
	xdotool search --onlyvisible --class Chrome windowfocus key ctrl+r
	xdotool windowfocus --sync ${MYWINDOW}
done
