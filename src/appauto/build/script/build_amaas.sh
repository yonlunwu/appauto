#!/bin/bash

set -e

work_dir=`pwd`

tag=$VERSION
if [ "$VERSION" == "" ]; then
  tag="latest"
fi

chmod 600 ssh/id_rsa

docker build -f dockerfile/zhiwen-ames.Dockerfile \
  --build-arg FT_BRANCH_NAME=$FT_BRANCH_NAME \
  --build-arg KT_BRANCH_NAME=$KT_BRANCH_NAME \
  --build-arg AMES_BRANCH_NAME=$AMES_BRANCH_NAME \
  --build-arg NUMA_FLAG=$NUMA_FLAG \
  --build-arg ZHIWEN_BASE_TAG=$ZHIWEN_BASE_TAG \
  --build-arg AMES_RUNTIME_RAG=$AMES_RUNTIME_RAG \
  --build-arg DEPENDS_HOST=$DEPENDS_HOST \
  --no-cache \
  --network host \
  -t zhiwen-ames:$tag .
