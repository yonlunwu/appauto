#!/bin/bash

set -e

harbor_ip="zhiwen.com"
work_dir=`pwd`

tag=$VERSION
if [ "$VERSION" == "" ]; then
  tag="latest"
fi


function build_base_builder() {
  docker build -f dockerfile/zhiwen-base.Dockerfile --no-cache \
  --build-arg DEPENDS_HOST=$DEPENDS_HOST \
  --network host -t zhiwen-base:$tag .
}

function build_web_builder() {
    docker build -f dockerfile/zhiwen-pnpm.Dockerfile --no-cache \
    --build-arg DEPENDS_HOST=$DEPENDS_HOST \
    --network host -t zhiwen-pnpm:$tag .
}

function build_rag_runtime() {
  docker build -f dockerfile/zhiwen-rag-runtime.Dockerfile --no-cache \
  --build-arg DEPENDS_HOST=$DEPENDS_HOST \
  --network host -t zhiwen-rag-runtime:$tag .
}

function build_ames_runtime() {
  docker build -f dockerfile/zhiwen-ames-runtime.Dockerfile --no-cache \
  --build-arg DEPENDS_HOST=$DEPENDS_HOST \
  --network host -t zhiwen-ames-runtime:$tag .
}

build_tag=$1

if [ $# == 0 ]; then
  build_tag="all"
fi

if [ "$build_tag" == "all" ]; then
  build_base_builder &
  build_web_builder &
  build_ames_runtime &
  build_rag_runtime &
  wait
elif [ "$build_tag" == "base"  ]; then
  build_base_builder &
  wait
elif [ "$build_tag" == "web" ]; then
  build_web_builder &
  wait
elif [ "$build_tag" == "rag" ]; then
  build_rag_runtime &
  wait
elif [ "$build_tag" == "ames" ]; then
  build_ames_runtime &
  wait
else
  echo "params error： $*"
  exit 2
fi
