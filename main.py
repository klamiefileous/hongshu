
#!/usr/bin/env python3
"""
小红书关键词监控脚本
主程序入口

功能：
1. 监控指定关键词的最新帖子
2. 使用 SQLite 去重
3. 发现新帖子时推送通知
4. 支持定时运行

使用方法：
1. 安装依赖: pip install -r requirements.txt
2. 安装 Playwright 浏览器: playwright install chromium
3. 配置 config.py 中的关键词和推送设置
4. 运行: python main.py
"""

import time
import schedule
from datetime import datetime

from config import KEYWORDS, CHECK_INTERVAL_MINUTES
from db import init_db, save_notes, get_recent_notes
from spiders.xhs_spider import run_spider
from notifier import notify_new_posts


def check_new_posts():
    """执行一次检查任务"""
    print(f"\n{'='*50}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始检查...")
    print(f"{'='*50}")
    
    try:
        # 运行爬虫
        posts = run_spider(KEYWORDS)
        
        if not posts:
            print("[Main] 本次未抓取到任何帖子")
            return
        
        # 保存到数据库，获取新增的帖子
        new_posts = save_notes(posts)
        
        if new_posts:
            print(f"[Main] 🆕 发现 {len(new_posts)} 条新帖子！")
            
            # 发送通知
            notify_new_posts(new_posts)
            
            # 打印新帖子信息
            for post in new_posts:
                print(f"  - [{post['keyword']}] {post['title'][:40]}...")
        else:
            print("[Main] 没有新帖子")
            
    except Exception as e:
        print(f"[Main] ❌ 检查过程出错: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    print("""
    ╔═══════════════════════════════════════════════╗
    ║       小红书关键词监控脚本 v1.0               ║
    ║       XiaoHongShu Keyword Monitor              ║
    ╚═══════════════════════════════════════════════╝
    """)
    
    print(f"[Config] 监控关键词: {', '.join(KEYWORDS)}")
    print(f"[Config] 检查间隔: {CHECK_INTERVAL_MINUTES} 分钟")
    print()
    
    # 初始化数据库
    init_db()
    
    # 立即执行一次检查
    check_new_posts()
    
    # 设置定时任务
    schedule.every(CHECK_INTERVAL_MINUTES).minutes.do(check_new_posts)
    
    print(f"\n[Scheduler] 定时任务已启动，每 {CHECK_INTERVAL_MINUTES} 分钟检查一次")
    print("[Scheduler] 按 Ctrl+C 停止程序\n")
    
    # 运行定时任务
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Main] 程序已停止")


if __name__ == "__main__":
    main()
