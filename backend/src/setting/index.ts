import type { NestExpressApplication } from '@nestjs/platform-express';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';

export const setSwaggerConfig = (app: NestExpressApplication) => {
  const config = new DocumentBuilder()
    .setTitle('우리집 AI 트레이더 API')
    .setDescription('우리집 AI 트레이더 API 문서')
    .setVersion('1.0')
    .addServer('http://localhost:5000/docs')
    .addBearerAuth({ type: 'http', scheme: 'bearer', in: 'header' }, 'Bearer')
    .build();

  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('api', app, document);
};
