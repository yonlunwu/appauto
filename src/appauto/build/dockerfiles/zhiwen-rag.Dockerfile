
ARG ZHIWEN_BASE_TAG
ARG RAG_RUNTIME_TAG

FROM zhiwen-base:${ZHIWEN_BASE_TAG} AS rag-build

ARG RAG_BRANCH_NAME
ARG DEPENDS_HOST

WORKDIR /app
COPY ssh /root/.ssh

RUN /bin/bash -c "GIT_SSH_COMMAND='ssh -o StrictHostKeyChecking=no' git clone -b ${RAG_BRANCH_NAME} git@github.com:kvcache-ai/RAG-dev.git"

RUN /bin/bash -i -c "mamba create --name rag python=3.11 -y && mamba activate rag  \
    && cd /app/RAG-dev; pip install -r requirements.txt --no-index --find-links=http://${DEPENDS_HOST}/py-depends/rag --trusted-host ${DEPENDS_HOST} && pip install -r requirements.txt;  \
    rm -rf .git .gitattributes .github .gitignore /root/.ssh"

RUN /bin/bash -i -c "mkdir -p /data && cd /data && wget -cnv http://${DEPENDS_HOST}/third_depends/nltk_data.tar.gz && tar -zxf nltk_data.tar.gz"

RUN /bin/bash -i -c "mkdir -p /tmp/data-gym-cache && cd /tmp/data-gym-cache &&  wget -cnv http://${DEPENDS_HOST}/third_depends/data-gym-cache/9b5ad71b2ce5302211f9c61530b329a4922fc6a4"

RUN /bin/bash -i -c "cd /data && wget -cnv http://${DEPENDS_HOST}/third_depends/deepdoc.tar.gz && tar -zxf deepdoc.tar.gz && cp -r deepdoc/* /app/RAG-dev/rag/res/"

RUN /bin/bash -i -c "cd /app/RAG-dev; mamba activate rag && mamba install -y openssl=3.0.16 && pyinstaller run_server.spec"

FROM zhiwen-rag-runtime:${RAG_RUNTIME_TAG}
WORKDIR /app

COPY --from=rag-build /app/RAG-dev/dist/rag /app
COPY --from=rag-build /app/RAG-dev/resource/testcase /app/resource/testcase
COPY --from=rag-build /data/nltk_data /root/nltk_data
COPY --from=rag-build /tmp/data-gym-cache /tmp/data-gym-cache

ENTRYPOINT ["/bin/bash",  "-i", "-c", "cd /app; ./api & ./task & wait"]
