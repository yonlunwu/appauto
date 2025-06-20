FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/nvidia/cuda:12.4.1-devel-ubuntu22.04

ARG DEPENDS_HOST
ENV TZ=Asia/Shanghai
#设置时区
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo '$TZ' > /etc/timezone

# 复制依赖程序到容器中
WORKDIR /data

# 更新apt
RUN apt-get update && apt-get install -y build-essential libxml2 tar libnuma-dev git  \
    libtbb-dev libssl-dev libcurl4-openssl-dev libaio1 libaio-dev libgflags-dev zlib1g-dev ffmpeg libsm6  \
    libxext6 libgl1 fonts-noto-cjk wkhtmltopdf pandoc libfmt-dev patchelf wget libhwloc-dev pkg-config

RUN wget -cnv http://${DEPENDS_HOST}/third_depends/Miniforge3-24.11.3-2-Linux-x86_64.sh
# 安装anaconda软件，并配置环境变量
RUN bash Miniforge3-24.11.3-2-Linux-x86_64.sh -u -b -p "/root/miniforge3" && /root/miniforge3/bin/mamba init

RUN rm -rf /data
