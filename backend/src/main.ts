import { NestFactory } from '@nestjs/core';
import { AppModule } from './app/app.module';
import { ConfigService } from '@nestjs/config';
import { setSwaggerConfig } from './setting';
import type { NestExpressApplication } from '@nestjs/platform-express';

async function bootstrap() {
  const app = await NestFactory.create<NestExpressApplication>(AppModule);
  await app.listen(process.env.PORT ?? 3000);
  const configService = app.get(ConfigService);

  if (configService.get('NODE_ENV') !== 'production') {
    setSwaggerConfig(app);
  }
}
bootstrap();
