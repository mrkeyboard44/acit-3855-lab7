#!/bin/bash
found_containers=`docker ps -a -f "expose=$1" -q`
docker rm "$found_containers"