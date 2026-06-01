FROM node:20-alpine

RUN corepack enable

WORKDIR /workspace

COPY package.json pnpm-workspace.yaml turbo.json ./
COPY apps/web/package.json apps/web/package.json

RUN pnpm install --filter @smartcommutex/web... --frozen-lockfile=false

COPY apps/web ./apps/web

WORKDIR /workspace/apps/web

EXPOSE 3000

CMD ["pnpm", "dev"]

