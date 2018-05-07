#!/bin/bash

DIR=$(cd $(dirname $BASH_SOURCE[0]) && pwd)
cd $DIR

set -e

echo "--- Changing to correct directory ---"
cd ../
echo ${PWD}

echo "--- copying build/DockerPublish to Dockerfile ---"
cp build/Dockerfile Dockerfile
echo "--- copying build/.dockerignore to .dockerignore ---"
cp build/.dockerignore .dockerignore
echo "-_- copying start.sh to ./ ---"
cp build/start.sh .

echo "--- building app ---"
docker build --pull --tag slap:latest .

echo "--- cleaning up artifacts ---"
rm Dockerfile
rm .dockerignore
rm start.sh