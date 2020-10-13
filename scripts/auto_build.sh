#!/bin/bash
# This is a script to run build_live when a specified file is modified. It's intent is to save clicks.
# If no file to watch is specified than it simply watches the whole project.

trap "kill 0" EXIT

watch=""
case "$1" in
	"")
		watch="../src/*";;
	*)
		echo watching $1
		watch=$1;;
esac

cd ../live

while true
do
	# TODO: update to python3.8 to use the --directory flag.
	python3 -m http.server 8080 > ../src/scripts/error &
	inotifywait -r --event modify $watch
	kill %1
	cd ../src
	./scripts/build_live.sh
	cd ../live
	xdotool search --onlyvisible --class Chrome windowfocus key ctrl+r && xdotool search --onlyvisible --class Terminal windowfocus
done
