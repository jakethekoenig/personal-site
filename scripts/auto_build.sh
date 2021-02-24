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
	python3 ../src/scripts/local_server.py > /dev/null &
	inotifywait -r --event modify $watch
	kill %1
	cd ../src
	#TODO: fit the auto_card script into the rest of the build process.
	#python3 scripts/my_auto_card.py temp.html content/blog/khm.html
	./scripts/build_live.sh
	cd ../live
	MYWINDOW=$(xdotool getactivewindow)
	xdotool search --onlyvisible --class Chrome windowfocus key ctrl+r
	xdotool windowfocus --sync ${MYWINDOW}
done
