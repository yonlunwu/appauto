
ARG ZHIWEN_PNPM_TAG

FROM zhiwen-pnpm:${ZHIWEN_PNPM_TAG} AS rag-web-builder

ARG WEB_BRANCH_NAME

WORKDIR /data
COPY ssh /root/.ssh

RUN GIT_SSH_COMMAND='ssh -o StrictHostKeyChecking=no' git clone -b ${WEB_BRANCH_NAME} git@github.com:kvcache-ai/zhiwen.git;

# 编译zhiwen前端代码
RUN /bin/bash -i -c "cd /data/zhiwen && pnpm i && pnpm build"

# nginx代理前端代码和后端接口转发
FROM nginx:latest AS rag-web

WORKDIR /app
RUN mkdir -p /app/zhiwen && sed -i '7a     application/javascript                mjs;' /etc/nginx/mime.types
COPY --from=rag-web-builder /data/zhiwen/dist /app/zhiwen
