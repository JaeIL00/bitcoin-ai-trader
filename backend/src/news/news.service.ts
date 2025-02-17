import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { News } from './entities/news.entity';
import { LatestNewsResponseDto } from './dto/latest-news.dto';

@Injectable()
export class NewsService {
  constructor(
    @InjectRepository(News)
    private newsRepository: Repository<News>,
  ) {}

  async getLatestNews(): Promise<LatestNewsResponseDto> {
    const latestNews = await this.newsRepository.findOne({
      order: { created_at: 'DESC' },
    });

    if (!latestNews) {
      throw new NotFoundException('최신 뉴스를 찾을 수 없습니다.');
    }

    return {
      title: latestNews.title,
      created_at: latestNews.created_at.toISOString(),
    };
  }
}
