FROM node:22.19.0-alpine AS dependencies
ENV PNPM_HOME=/pnpm
ENV PATH=$PNPM_HOME:$PATH
RUN corepack enable
WORKDIR /workspace
COPY package.json pnpm-workspace.yaml pnpm-lock.yaml tsconfig.base.json ./
COPY apps/web/package.json apps/web/package.json
COPY packages/contracts/package.json packages/contracts/package.json
RUN pnpm install --filter @autodev/web... --frozen-lockfile

FROM dependencies AS builder
ENV AUTODEV_STANDALONE=true
COPY apps/web apps/web
COPY packages/contracts packages/contracts
RUN pnpm --filter @autodev/web build

FROM node:22.19.0-alpine AS runtime
ENV NODE_ENV=production
RUN addgroup --system --gid 10001 app && adduser --system --uid 10001 --ingroup app app
WORKDIR /app
COPY --from=builder --chown=app:app /workspace/apps/web/.next/standalone ./
COPY --from=builder --chown=app:app /workspace/apps/web/.next/static ./apps/web/.next/static
USER app
EXPOSE 3000
CMD ["node", "apps/web/server.js"]
