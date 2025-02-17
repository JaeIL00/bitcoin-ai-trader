// src/news/news.controller.ts
import { Controller, Get } from '@nestjs/common';
import { LatestNewsResponseDto } from './dto/latest-news.dto';
import { NewsService } from './news.service';
import { ApiTags } from '@nestjs/swagger';

@ApiTags('news')
@Controller('news')
export class NewsController {
  constructor(private readonly newsService: NewsService) {}

  @Get('latest')
  async getLatestNews(): Promise<LatestNewsResponseDto> {
    return this.newsService.getLatestNews();
  }
}
