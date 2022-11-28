#!/bin/bash
docker rm $(docker ps -a -f 'name=3850_assignment_$1*' -q)