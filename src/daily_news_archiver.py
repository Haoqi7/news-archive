import os
import json
import requests
import time
import warnings
from datetime import datetime
from typing import Dict, List, Optional

# 禁用SSL警告
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# 配置项
CONFIG = {
    "BASE_API_URL": "https://api-hot.imsyy.top/",
    "PLATFORMS": ["weibo", "zhihu", "bilibili", "baidu", "toutiao"],
    "MAX_ITEMS": 20,
    "REQUEST_TIMEOUT": 20,
    "REQUEST_DELAY": 1.5,
    "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "ARCHIVE_ROOT": os.path.abspath("archive")
}

class NewsArchiver:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": CONFIG["USER_AGENT"],
            "Accept": "application/json"
        })
        self.session.verify = False

    def fetch_platform_news(self, platform: str) -> Optional[List[dict]]:
        """获取平台数据"""
        url = f"{CONFIG['BASE_API_URL']}{platform}"
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                response = self.session.get(url, timeout=CONFIG["REQUEST_TIMEOUT"])
                response.raise_for_status()
                return response.json()[:CONFIG["MAX_ITEMS"]]
        except Exception as e:
            print(f"[{platform}] 请求失败: {str(e)[:100]}")
            return None

    def save_news(self, platform: str, news_list: List[dict]) -> bool:
        """保存数据"""
        date_path = datetime.now().strftime("%Y/%m/%d")
        save_dir = os.path.join(CONFIG["ARCHIVE_ROOT"], date_path)
        os.makedirs(save_dir, exist_ok=True)
        
        file_path = os.path.join(save_dir, f"{platform}.json")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump({
                    "meta": {
                        "platform": platform,
                        "date": datetime.now().isoformat(),
                        "count": len(news_list)
                    },
                    "data": news_list
                }, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"[{platform}] 保存失败: {e}")
            return False

    def git_commit(self):
        """Git提交"""
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # 强制设置用户信息
        os.system('git config --global user.name "Haoqi7"')
        os.system('git config --global user.email "w00989988@gmail.com"')
        
        # 添加所有变更
        os.system('git add -A')
        os.system(f'git commit -m "Auto-archive: {datetime.now().strftime("%Y-%m-%d")}"')
        return os.system('git push origin main') == 0

    def run(self):
        """主流程"""
        success_count = 0
        for platform in CONFIG["PLATFORMS"]:
            if news := self.fetch_platform_news(platform):
                if self.save_news(platform, news):
                    success_count += 1
                    print(f"[✓] {platform} 归档成功 ({len(news)}条)")
                else:
                    print(f"[×] {platform} 保存失败")
            time.sleep(CONFIG["REQUEST_DELAY"])
        
        if success_count > 0 and self.git_commit():
            print("数据推送成功")
        else:
            print("无有效数据或推送失败")

if __name__ == "__main__":
    NewsArchiver().run()
