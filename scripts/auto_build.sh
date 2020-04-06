#!/bin/bash
# This is a script to run build_live when a specified file is modified. It's intent is to save clicks

while true
do
	inotifywait --event modify $1
	echo test
	./scripts/build_live.sh
done
