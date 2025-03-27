# 每日新闻归档系统

自动归档各平台热点新闻到GitHub，按日期和平台分类存储。

## 特性
- 每日自动运行（UTC 00:00）
- 每个平台保存前20条新闻
- 结构化JSON存储
- 自动错误重试机制

## 数据格式
```json
{
  "meta": {
    "platform": "weibo",
    "date": "2023-10-05T08:00:00",
    "source": "https://api-hot.imsyy.top/",
    "item_count": 20
  },
  "data": [
    // 新闻条目...
  ]
}
