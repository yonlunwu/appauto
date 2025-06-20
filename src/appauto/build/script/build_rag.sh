#!/bin/bash
set -e

work_dir=`pwd`

tag=$VERSION
if [ "$VERSION" == "" ]; then
  tag="latest"
fi

chmod 600 ssh/id_rsa

docker build -f dockerfile/zhiwen-rag.Dockerfile \
  --build-arg RAG_BRANCH_NAME=$RAG_BRANCH_NAME \
  --build-arg ZHIWEN_BASE_TAG=$ZHIWEN_BASE_TAG \
  --build-arg RAG_RUNTIME_TAG=$RAG_RUNTIME_TAG \
  --build-arg DEPENDS_HOST=$DEPENDS_HOST \
  --no-cache \
  --network host \
  -t zhiwen-rag:$tag .
