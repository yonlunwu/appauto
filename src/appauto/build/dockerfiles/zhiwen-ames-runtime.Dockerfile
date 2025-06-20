FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/nvidia/cuda:12.4.1-devel-ubuntu22.04
WORKDIR /app

RUN apt-get update && apt-get install -y libnuma-dev libtbb-dev libssl-dev libcurl4-openssl-dev libaio1  \
    libaio-dev libgflags-dev zlib1g-dev libfmt-dev libhwloc-dev