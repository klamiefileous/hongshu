"""
小红书爬虫模块
使用 Playwright 持久化浏览器上下文抓取搜索结果
"""

import re
import time
import random
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright, Page, BrowserContext
from config import USER_DATA_DIR, HEADLESS, MAX_POSTS


def random_sleep(min_sec: float = 1.0, max_sec: float = 3.0):
    """随机等待，模拟人类操作"""
    time.sleep(random.uniform(min_sec, max_sec))


def extract_note_id(url: str) -> Optional[str]:
    """
    从小红书帖子链接中提取 note_id
    示例：https://www.xiaohongshu.com/explore/6579a1b2000000001e00xxxx
    """
    patterns = [
        r'/explore/([a-zA-Z0-9]+)',
        r'/discovery/item/([a-zA-Z0-9]+)',
        r'note_id=([a-zA-Z0-9]+)',
        r'/note/([a-zA-Z0-9]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def search_keyword(page: Page, keyword: str) -> List[Dict]:
    """
    搜索单个关键词并抓取结果
    """
    print(f"[Spider] 开始搜索关键词: {keyword}")
    results = []
    
    try:
        # 访问搜索页面
        search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}&source=web_search_result_notes"
        page.goto(search_url, wait_until='networkidle', timeout=30000)
        random_sleep(2, 4)
        
        # 点击"最新"排序按钮
        try:
            # 尝试找到排序选项
            sort_buttons = page.locator('text=最新').all()
            for btn in sort_buttons:
                if btn.is_visible():
                    btn.click()
                    print("[Spider] 已切换到最新排序")
                    random_sleep(2, 3)
                    break
        except Exception as e:
            print(f"[Spider] 切换排序失败（可能默认就是最新）: {e}")
        
        # 等待内容加载
        random_sleep(2, 3)
        
        # 滚动页面加载更多内容
        for _ in range(3):
            page.mouse.wheel(0, 800)
            random_sleep(1, 2)
        
        # 抓取帖子卡片
        # 小红书搜索结果通常在 section 或带有特定 class 的容器中
        note_cards = page.locator('section.note-item, div[class*="note-item"], a[href*="/explore/"], a[href*="/discovery/item/"]').all()
        
        if not note_cards:
            # 备用选择器
            note_cards = page.locator('[class*="note"], [class*="card"]').all()
        
        print(f"[Spider] 找到 {len(note_cards)} 个帖子元素")
        
        seen_ids = set()
        
        for card in note_cards[:MAX_POSTS * 2]:  # 多抓一些，后面去重
            try:
                # 尝试获取链接
                link_elem = card if card.get_attribute('href') else card.locator('a[href*="/explore/"], a[href*="/discovery/"]').first
                
                href = link_elem.get_attribute('href') if link_elem else None
                
                if not href:
                    continue
                
                # 确保是完整 URL
                if href.startswith('/'):
                    href = f"https://www.xiaohongshu.com{href}"
                
                # 提取 note_id
                note_id = extract_note_id(href)
                if not note_id or note_id in seen_ids:
                    continue
                
                seen_ids.add(note_id)
                
                # 尝试获取标题
                title = ""
                try:
                    title_elem = card.locator('[class*="title"], [class*="desc"], span, p').first
                    title = title_elem.text_content() if title_elem else ""
                    title = title.strip()[:100] if title else ""
                except:
                    pass
                
                # 尝试获取发布时间
                publish_time = ""
                try:
                    time_elem = card.locator('[class*="time"], [class*="date"]').first
                    publish_time = time_elem.text_content() if time_elem else ""
                    publish_time = publish_time.strip() if publish_time else ""
                except:
                    pass
                
                results.append({
                    'platform': 'xiaohongshu',
                    'note_id': note_id,
                    'title': title or f"小红书笔记 {note_id[:8]}",
                    'publish_time': publish_time,
                    'url': href,
                    'keyword': keyword
                })
                
                if len(results) >= MAX_POSTS:
                    break
                    
            except Exception as e:
                continue
        
        print(f"[Spider] 关键词 '{keyword}' 抓取到 {len(results)} 条有效帖子")
        
    except Exception as e:
        print(f"[Spider] 搜索 '{keyword}' 时出错: {e}")
    
    return results


def run_spider(keywords: List[str]) -> List[Dict]:
    """
    运行爬虫，搜索所有关键词
    使用持久化浏览器上下文保存登录态
    """
    all_results = []
    
    with sync_playwright() as p:
        # 使用持久化上下文，保存登录态
        context = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=HEADLESS,
            viewport={'width': 1280, 'height': 800},
            locale='zh-CN',
            timezone_id='Asia/Shanghai',
            # 模拟真实浏览器
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = context.new_page()
        
        # 首次访问主页，检查登录状态
        print("[Spider] 访问小红书主页...")
        page.goto("https://www.xiaohongshu.com", wait_until='networkidle', timeout=30000)
        random_sleep(3, 5)
        
        # 检查是否需要登录
        if page.locator('text=登录').count() > 0:
            print("\n" + "="*50)
            print("[Spider] ⚠️ 检测到未登录状态")
            print("[Spider] 请在打开的浏览器中手动登录小红书")
            print("[Spider] 登录完成后，程序将自动继续...")
            print("="*50 + "\n")
            
            # 等待登录完成（检测登录按钮消失或用户头像出现）
            try:
                page.wait_for_selector('[class*="user"], [class*="avatar"], [class*="header-user"]', timeout=300000)
                print("[Spider] ✅ 登录成功！")
            except:
                print("[Spider] 登录超时，请重新运行程序")
                context.close()
                return []
        else:
            print("[Spider] ✅ 已处于登录状态")
        
        random_sleep(2, 3)
        
        # 搜索每个关键词
        for keyword in keywords:
            results = search_keyword(page, keyword)
            all_results.extend(results)
            random_sleep(3, 5)  # 关键词之间多等待一下
        
        context.close()
    
    # 去重（基于 note_id）
    seen = set()
    unique_results = []
    for r in all_results:
        if r['note_id'] not in seen:
            seen.add(r['note_id'])
            unique_results.append(r)
    
    print(f"[Spider] 本次共抓取 {len(unique_results)} 条唯一帖子")
    return unique_results
