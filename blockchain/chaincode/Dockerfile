FROM node:lts AS builder

WORKDIR /usr/src/app

COPY --chown=node:node . /usr/src/app
ENV npm_config_cache=/usr/src/app
RUN npm ci && npm run prepublishOnly

FROM node:lts AS production
ARG CC_SERVER_PORT

RUN apt-get update && apt-get install -y tini && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app
COPY --chown=node:node --from=builder /usr/src/app/dist ./dist
COPY --chown=node:node --from=builder /usr/src/app/package.json /usr/src/app/package-lock.json ./
COPY --chown=node:node docker/docker-entrypoint.sh /usr/src/app/docker-entrypoint.sh
RUN chmod +x /usr/src/app/docker-entrypoint.sh

RUN npm ci --omit=dev && npm cache clean --force

ENV PORT $CC_SERVER_PORT
EXPOSE $CC_SERVER_PORT
ENV NODE_ENV=production

USER node
ENTRYPOINT [ "/usr/bin/tini", "--", "/usr/src/app/docker-entrypoint.sh" ]
