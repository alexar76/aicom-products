FROM node:20-alpine

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install --no-audit --no-fund

COPY frontend ./

ENV VITE_API_BASE=/api \
    HOST=0.0.0.0
EXPOSE 5173

CMD ["sh", "-c", "npm run build && npx vite preview --host 0.0.0.0 --port 5173"]
