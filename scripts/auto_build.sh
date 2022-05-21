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
	wait %1
	cd $RUN_DIR
	$SCRIPT_DIR/build_live.sh
	cd $LIVE
done
