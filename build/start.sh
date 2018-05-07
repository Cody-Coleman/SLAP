#!/bin/sh

DIR=$(cd $(dirname $BASH_SOURCE[0]) && pwd)
cd $DIR

set -e

echo "--start.sh-- ${PWD}"

cd $DIR

echo "--start.sh-- waiting"

while :
do
    sleep 30
done
