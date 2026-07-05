# syntax=docker/dockerfile:1.7
FROM node:22-alpine

WORKDIR /app

# pnpm은 corepack으로 활성화 (node:20에 내장)
# lockfile은 pnpm 9로 작성됨 (lockfileVersion 9.0). 11의 minimumReleaseAge 정책 회피 겸 재현성 확보.
RUN corepack enable && corepack prepare pnpm@9 --activate

# 의존성 레이어 캐시
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

# 소스 (dev에서는 volume이 덮어씀)
COPY next.config.mjs tsconfig.json postcss.config.mjs tailwind.config.ts next-env.d.ts ./
COPY src ./src

EXPOSE 3000

# Docker Desktop 파일 감지가 불안정한 환경에서도 hot reload 되도록 polling
ENV WATCHPACK_POLLING=true \
    CHOKIDAR_USEPOLLING=true

CMD ["pnpm", "dev"]
