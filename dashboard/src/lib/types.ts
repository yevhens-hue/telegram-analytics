
export interface AppData {
  app_name: string;
  category: string;
  position: number;
  daily_revenue_ton: number;
  daily_active_wallets: number;
  growth: number;
  organic_index: number;
  trend_score: number;
  market_sentiment: number;
  prediction_7d: number;
}

export interface TrendData {
  date: string;
  total_ton: number;
  total_dau: number;
}

export interface TonMetrics {
  price_usd: number;
  asset_id: string;
  date: string;
}

export interface NewsItem {
  app_name: string;
  content: string;
  sentiment_score: number;
  date: string;
}

export interface Alert {
  app_name: string;
  message: string;
  severity: string;
  date: string;
}
