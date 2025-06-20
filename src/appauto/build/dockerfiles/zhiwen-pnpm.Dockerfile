FROM ubuntu:22.04

ENV TZ=Asia/Shanghai
#设置时区
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo '$TZ' > /etc/timezone


# 安装pnpm
RUN apt update && apt install curl git wget  -y
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
RUN . $HOME/.nvm/nvm.sh && /bin/bash -i -c "nvm -v"
RUN /bin/bash -i -c "nvm -v && nvm install 22 && npm config set registry https://registry.npmmirror.com &&  \
    npm config get registry; npm install -g pnpm"
