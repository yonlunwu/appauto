#!/bin/bash

set -e

work_dir=`pwd`

function build_web() {
  tag=$VERSION
  if [ "$VERSION" == "" ]; then
    tag="latest"
  fi
  docker build -f dockerfile/zhiwen-$2-web.Dockerfile \
    --build-arg WEB_BRANCH_NAME=$1 \
    --build-arg ZHIWEN_PNPM_TAG=$ZHIWEN_PNPM_TAG \
    --no-cache \
    --network host \
    -t zhiwen-$2-web:$tag .
}

build_tag=$1

if [ $# == 0 ]; then
  build_tag="all"
fi

chmod 600 ssh/id_rsa

if [ "$build_tag" == "all" ]; then
  (build_web $KLLM_WEB_BRANCH_NAME "ames") &
  (build_web $ZHIWEN_WEB_BRANCH_NAME "rag") &
  wait
elif [ "$build_tag" == "rag"  ]; then
  build_web $ZHIWEN_WEB_BRANCH_NAME "rag" &
elif [ "$build_tag" == "ames" ]; then
  build_web $KLLM_WEB_BRANCH_NAME "ames" &
else
  echo "params error： $*"
  exit 2
fi

wait
