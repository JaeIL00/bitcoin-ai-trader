# Node 23 alpine 이미지 사용
FROM node:23-alpine

# 작업 디렉토리 설정
WORKDIR /app

# yarn 설치 파일 복사
COPY package.json yarn.lock ./

# dependencies 설치
RUN yarn install --frozen-lockfile

# 소스 코드 복사
COPY . .

# 빌드
RUN yarn build

# 포트 설정
EXPOSE 5000

# 프로덕션 실행
CMD ["yarn", "start:prod"]