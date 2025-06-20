
ARG ZHIWEN_PNPM_TAG

FROM zhiwen-pnpm:${ZHIWEN_PNPM_TAG} AS ames-web-builder

ARG WEB_BRANCH_NAME

WORKDIR /data
COPY ssh /root/.ssh

RUN GIT_SSH_COMMAND='ssh -o StrictHostKeyChecking=no' git clone -b ${WEB_BRANCH_NAME} git@github.com:kvcache-ai/KLLM-Admin.git

# 编译ames前端代码
RUN /bin/bash -i -c "cd /data/KLLM-Admin && pnpm i && pnpm build"

# nginx代理前端代码和后端接口转发
FROM nginx:latest AS ames-web

WORKDIR /app

RUN mkdir -p /app/ames && sed -i '7a     application/javascript                mjs;' /etc/nginx/mime.types
COPY --from=ames-web-builder /data/KLLM-Admin/dist /app/ames
