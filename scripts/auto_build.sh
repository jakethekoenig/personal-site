#!/bin/bash
# This is a script to run build_live when a specified file is modified. It's intent is to save clicks.
# If no file to watch is specified than it simply watches the whole project.

watch=""
case "$1" in
	"")
		watch="./*";;
	*)
		echo watching $1;;
esac

while true
do
	inotifywait --event modify $watch
	./scripts/build_live.sh
done
