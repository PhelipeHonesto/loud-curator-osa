export interface Article {
  id: string;
  title: string;
  custom_title?: string;
  date: string;
  body: string;
  link: string;
  source: string;
  status: string;
  score_relevance?: number;
  score_vibe?: number;
  score_viral?: number;
  target_channels?: string[];
  auto_post?: boolean;
  priority?: string;
}
