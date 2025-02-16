import { NestFactory } from '@nestjs/core';
import { AppModule } from './app/app.module';
import { setSwaggerConfig } from './setting';
import type { NestExpressApplication } from '@nestjs/platform-express';

async function bootstrap() {
  const app = await NestFactory.create<NestExpressApplication>(AppModule);
  const port = 5000;
  await app.listen(port);

  setSwaggerConfig(app);
}
bootstrap();
