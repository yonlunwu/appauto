ARG ZHIWEN_BASE_TAG
ARG AMES_RUNTIME_RAG

FROM zhiwen-base:${ZHIWEN_BASE_TAG} AS ames-build

ARG FT_BRANCH_NAME
ARG KT_BRANCH_NAME
ARG AMES_BRANCH_NAME
ARG NUMA_FLAG
ARG DEPENDS_HOST

WORKDIR /app
COPY ssh /root/.ssh

RUN /bin/bash -c "cd /app; GIT_SSH_COMMAND='ssh -o StrictHostKeyChecking=no' git clone -b ${FT_BRANCH_NAME} git@github.com:kvcache-ai/ftransformers.git && \
    git clone -b ${KT_BRANCH_NAME} git@github.com:kvcache-ai/ktransformers-dev.git ktransformers && \
    git clone -b ${AMES_BRANCH_NAME} git@github.com:kvcache-ai/AMES.git && \
    cd /app/ktransformers && git submodule update --init --recursive"

# 编译安装 ktransformers
RUN /bin/bash -i -c "cd /app/ktransformers; \
    mamba create --name ktransformers python=3.11 -y && \
    mamba activate ktransformers; mamba install -c conda-forge libstdcxx-ng cmake -y; \
    cd /app/ktransformers; mamba activate ktransformers; pip install -r requirements-local_chat.txt --no-index --find-links=/depends/kt; \
     pip install -r ktransformers/server/requirements.txt --no-index --find-links=http://${DEPENDS_HOST}/py-depends/kt --trusted-host ${DEPENDS_HOST};  \
    env TORCH_CUDA_ARCH_LIST=\"8.0;8.6;8.7;8.9;9.0+PTX\" USE_BALANCE_SERVE=1 ${NUMA_FLAG}  bash ./install.sh; \
    rm -rf .clang-format  .clangd .devcontainer .flake8  .git  .github .gitignore .gitmodules .pylintrc"

# 编译安装AMES
RUN /bin/bash -i -c "cd /app/AMES; mamba create --name ames python=3.11 -y && mamba activate ames &&  \
    pip install -r requirements.txt --no-index --find-links=http://${DEPENDS_HOST}/py-depends/ames --trusted-host ${DEPENDS_HOST}; pip install -r requirements.txt"
RUN /bin/bash -i -c "cd /data; wget -cnv http://${DEPENDS_HOST}/third_depends/AMES_third_party.tar.gz && tar -zxf AMES_third_party.tar.gz;  \
    cp -r bin /root/miniforge3/envs/ames/lib/python3.11/site-packages/gpustack/third_party/; cp -r bin /app/AMES/AMES/third_party/; \
    rm -rf  .git .gitignore"

# 编译安装ftransformers
RUN /bin/bash -i -c "cd /app/ftransformers;  mamba activate ames;  pip install -e \"python[all]\" --no-index --find-links=http://${DEPENDS_HOST}/py-depends/ft --trusted-host ${DEPENDS_HOST}; \
    pip install -e \"python[all]\" --find-links https://flashinfer.ai/whl/cu124/torch2.5/flashinfer-python; rm -rf /root/.ssh"

# 编译二进制ames执行包
RUN /bin/bash -i -c "cd /app/AMES; mamba activate ames; pyinstaller run_server.spec"

RUN /bin/bash -i -c "rm -rf root/miniforge3/envs/ames"

FROM zhiwen-ames-runtime:${AMES_RUNTIME_RAG}
WORKDIR /app

COPY --from=ames-build /root /root
COPY --from=ames-build /app/ftransformers /app/ftransformers
COPY --from=ames-build /app/ktransformers /app/ktransformers
COPY --from=ames-build /app/AMES/dist/ames /app/AMES

ENTRYPOINT ["/bin/bash", "-i", "-c", "cd /app/AMES && ./supervisor & ./worker & wait"]