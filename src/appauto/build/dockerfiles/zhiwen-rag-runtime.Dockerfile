FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/nvidia/cuda:12.4.1-devel-ubuntu22.04
ARG DEPENDS_HOST

ENV TZ=Asia/Shanghai
#设置时区
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo '$TZ' > /etc/timezone

WORKDIR /data

RUN apt update && apt install -y wget ffmpeg libsm6 libxext6 libgl1 fonts-noto-cjk wkhtmltopdf pandoc