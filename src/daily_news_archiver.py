import os
import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Optional

# 配置项 ===============================================
CONFIG = {
    "BASE_API_URL": "https://api-hot.imsyy.top/",
    "PLATFORMS": ["weibo", "zhihu", "bilibili", "baidu", "toutiao"],
    "MAX_ITEMS": 20,
    "REQUEST_TIMEOUT": 20,
    "REQUEST_DELAY": 1.5,
    "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "ARCHIVE_ROOT": "archive"
}
# ======================================================

class NewsArchiver:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": CONFIG["USER_AGENT"],
            "Accept": "application/json"
        })
        self.session.verify = False  # 全局禁用SSL验证

    def fetch_platform_news(self, platform: str) -> Optional[List[dict]]:
        """获取平台数据（含错误重试）"""
        url = f"{CONFIG['BASE_API_URL']}{platform}"
        
        try:
            response = self.session.get(
                url,
                timeout=CONFIG["REQUEST_TIMEOUT"]
            )
            response.raise_for_status()
            
            # 解析JSON
            try:
                data = response.json()
            except json.JSONDecodeError:
                print(f"[{platform}] 响应非JSON格式")
                return None
                
            # 提取数据
            news_data = data if isinstance(data, list) else data.get("data", [])
            return news_data[:CONFIG["MAX_ITEMS"]]
            
        except requests.exceptions.RequestException as e:
            print(f"[{platform}] 请求失败: {str(e)[:120]}")
            return None
        except Exception as e:
            print(f"[{platform}] 处理错误: {str(e)[:120]}")
            return None

    def save_news(self, platform: str, news_list: List[dict]) -> bool:
        """保存平台数据到文件"""
        if not news_list:
            return False
            
        date_str = datetime.now().strftime("%Y/%m/%d")
        save_dir = os.path.join(
            CONFIG["ARCHIVE_ROOT"],
            date_str
        )
        os.makedirs(save_dir, exist_ok=True)
        
        file_path = os.path.join(save_dir, f"{platform}.json")
        archive_data = {
            "meta": {
                "platform": platform,
                "date": datetime.now().isoformat(),
                "source": CONFIG["BASE_API_URL"],
                "item_count": len(news_list)
            },
            "data": news_list
        }
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(archive_data, f, ensure_ascii=False, indent=2)
            return True
        except IOError as e:
            print(f"[{platform}] 文件保存失败: {e}")
            return False

    def run(self):
        """主执行流程"""
        success_count = 0
        
        for platform in CONFIG["PLATFORMS"]:
            if news_list := self.fetch_platform_news(platform):
                if self.save_news(platform, news_list):
                    success_count += 1
                    print(f"[✓] {platform} 归档成功 ({len(news_list)}条)")
                else:
                    print(f"[×] {platform} 归档失败")
            else:
                print(f"[×] {platform} 无有效数据")
            
            time.sleep(CONFIG["REQUEST_DELAY"])
        
        # 推送条件：至少一个平台成功
        if success_count > 0:
            self.git_push()
        else:
            print("所有平台归档失败，终止推送")

    def git_push(self):
        """执行Git推送"""
        os.chdir(os.path.dirname(__file__))
        os.system(f'git add {CONFIG["ARCHIVE_ROOT"]}/')
        os.system(f'git commit -m "Auto-archive: {datetime.now().strftime("%Y-%m-%d %H:%M")}"')
        os.system('git push origin main')

if __name__ == "__main__":
    archiver = NewsArchiver()
    archiver.run()
