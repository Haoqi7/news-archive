import os
import json
import requests
import time
from datetime import datetime
from typing import Dict, List

# 配置信息
BASE_API_URL = "https://api-hot.imsyy.top/"
PLATFORMS = ["weibo", "zhihu", "baidu", "bilibili", "toutiao", "douyin"]
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "application/json"
}
MAX_ITEMS = 20  # 每个平台最多归档20条
REQUEST_DELAY = 1
GIT_REPO_PATH = "./"

def fetch_platform_news(platform: str) -> List[dict]:
    """获取单个平台新闻（自动截取前MAX_ITEMS条）"""
    api_url = f"{BASE_API_URL}{platform}"
    try:
        response = requests.get(
            api_url,
            headers=HEADERS,
            timeout=15,
            verify=False
        )
        response.raise_for_status()
        
        data = response.json()
        
        # 根据API结构提取数据
        raw_data = data if isinstance(data, list) else data.get("data", [])
        
        # 返回前MAX_ITEMS条，按实际需求排序（假设API返回已排序）
        return raw_data[:MAX_ITEMS]
        
    except Exception as e:
        print(f"[{platform}] 获取失败: {str(e)[:100]}")  # 截取错误前100字符
        return []

def save_news_by_date(platform_news: Dict[str, List[dict]]):
    """保存数据（包含条数限制）"""
    today = datetime.now().strftime("%Y-%m-%d")
    date_path = datetime.now().strftime("%Y/%m/%d")
    archive_dir = os.path.join(GIT_REPO_PATH, "archive", date_path)
    os.makedirs(archive_dir, exist_ok=True)
    
    for platform, news_list in platform_news.items():
        if not news_list:
            continue
            
        # 添加平台数据统计
        output_data = {
            "date": today,
            "platform": platform,
            "total_results": len(news_list),
            "news": news_list
        }
        
        filename = os.path.join(archive_dir, f"{platform}.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        print(f"已归档 {platform} ({len(news_list)}条)")

def git_commit_and_push():
    """自动提交到GitHub"""
    os.chdir(GIT_REPO_PATH)
    os.system('git config --global user.name "GitHub Actions"')
    os.system('git config --global user.email "actions@github.com"')
    os.system('git add archive/')
    os.system(f'git commit -m "Auto-archive: {datetime.now().strftime("%Y-%m-%d")}"')
    os.system('git push origin main')

if __name__ == "__main__":
    platform_news = {}
    
    for platform in PLATFORMS:
        news_list = fetch_platform_news(platform)
        platform_news[platform] = news_list
        time.sleep(REQUEST_DELAY)
    
    if sum(len(v) for v in platform_news.values()) == 0:
        print("所有平台数据为空，终止执行")
        exit(1)
    
    save_news_by_date(platform_news)
    git_commit_and_push()