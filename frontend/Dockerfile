# 빌드 스테이지
FROM node:18-alpine as build

WORKDIR /app

# 의존성 설치
COPY package.json package-lock.json* ./
RUN npm ci  
# npm ci는 package-lock.json을 엄격하게 따릅니다

# 소스 코드 복사 및 빌드
COPY . .
RUN npm run build

# 프로덕션 스테이지
FROM nginx:alpine

# Nginx 설정 복사
COPY ./nginx.conf /etc/nginx/conf.d/default.conf

# 빌드된 파일을 Nginx 서빙 디렉토리로 복사 (Vite는 dist 디렉토리 사용)
COPY --from=build /app/dist /usr/share/nginx/html

# 80 포트 노출
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]