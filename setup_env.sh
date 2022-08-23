#!/bin/bash

DL_ENV=${1:-"katazero"}
NOTEBOOK_PORT=${2:-8888}
VISDOM_PORT=${3:-8097}
IMAGE=katazero:0.1.1-py3-gpu

if [ ${DL_ENV}=="katazero" ]; then
    if [[ ! $(docker images -q ${IMAGE}) ]]; then
           docker build . -t ${IMAGE} -f ./docker/Dockerfile
    fi
    # this should run a notebook container
    docker run --runtime=nvidia --shm-size 8G -v `pwd`:/workspace -p ${NOTEBOOK_PORT}:8888 -p ${VISDOM_PORT}:8097 --name katazero_notebook ${IMAGE}
    docker exec katazero_notebook jupyter notebook list
else
    exit 1
fi

