# syntax=docker/dockerfile:1
# Multi-stage build
# Stage 1: Dependencies
FROM node:20-alpine AS deps
WORKDIR /app

# Install Python and build dependencies for native modules
# This helps with ARM64 builds and native module compilation
RUN apk add --no-cache python3 make g++ libc6-compat

# Copy package files
COPY ui/package*.json ./

# Clean install with proper handling of native modules
RUN --mount=type=cache,target=/root/.npm npm ci

# Stage 2: Builder
FROM node:20-alpine AS builder
WORKDIR /app

# Install libc6-compat for native modules in builder stage too
RUN apk add --no-cache libc6-compat

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy all files needed for build
COPY ui/package*.json ./
COPY ui/tsconfig.json ./
COPY ui/next.config.ts ./
COPY ui/components.json ./
COPY ui/sentry.edge.config.ts ./
COPY ui/sentry.server.config.ts ./
COPY ui/postcss.config.mjs ./
COPY ui/public ./public
COPY ui/src ./src

# Set build-time environment variables (needed for Next.js build)
ARG NEXT_PUBLIC_BRAND_NAME=Zenvoice
ARG NEXT_PUBLIC_BRAND_TAGLINE="Open Source Voice Assistant Workflow Builder"
ARG NEXT_PUBLIC_BRAND_HERO_HEADLINE="The open-source voice AI platform."
ARG NEXT_PUBLIC_BRAND_WEBSITE_URL=https://zenvoice.example
ARG NEXT_PUBLIC_DOCS_URL=https://docs.zenvoice.example
ENV NEXT_PUBLIC_BRAND_NAME=$NEXT_PUBLIC_BRAND_NAME
ENV NEXT_PUBLIC_BRAND_TAGLINE=$NEXT_PUBLIC_BRAND_TAGLINE
ENV NEXT_PUBLIC_BRAND_HERO_HEADLINE=$NEXT_PUBLIC_BRAND_HERO_HEADLINE
ENV NEXT_PUBLIC_BRAND_WEBSITE_URL=$NEXT_PUBLIC_BRAND_WEBSITE_URL
ENV NEXT_PUBLIC_DOCS_URL=$NEXT_PUBLIC_DOCS_URL
ENV NEXT_PUBLIC_NODE_ENV="oss"
ENV NEXT_TELEMETRY_DISABLED="1"
# Chatwoot support-chat widget is disabled by default (ChatwootWidget no-ops
# without these). Set to your own Chatwoot instance URL/website token to enable it.
ENV NEXT_PUBLIC_CHATWOOT_URL=""
ENV NEXT_PUBLIC_CHATWOOT_TOKEN=""
ENV BACKEND_URL="http://api:8000"

# Build the application with standalone mode
# Increase Node.js heap size to prevent out-of-memory errors during build
ENV NODE_OPTIONS="--max-old-space-size=4096"
RUN npm run build && \
    rm -rf /tmp/* /root/.npm /root/.next/cache

# Stage 3: Runner (production image)
FROM node:20-alpine AS runner
WORKDIR /app

# Environment variables will be provided by docker-compose
ENV NODE_ENV=production

# Create a non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy standalone build output
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

# Switch to non-root user
USER nextjs

# Expose the port Next.js runs on
EXPOSE 3010

# Start the production server using the standalone Node.js server
CMD sh -c "echo '🚀 Application ready at http://localhost:3010' && PORT=3010 node server.js"
