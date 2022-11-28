#!/bin/bash
found_containers=`docker ps -a -f 'name=3850_assignment_$1*' -q`
echo `docker ps -a -f 'name=3850_assignment_$1*' -q`
docker rm $found_containers