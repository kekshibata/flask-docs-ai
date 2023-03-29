FROM node:16-alpine

WORKDIR /app
COPY ../../frontend/ .
RUN yarn global add @vue/cli && yarn global add @vue/cli-init

RUN yarn
