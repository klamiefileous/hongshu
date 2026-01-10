"""
通知推送模块
支持 Server酱微信推送 和 邮件推送
"""

import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
from config import (
    SERVERCHAN_SENDKEY,
    EMAIL_ENABLED,
    EMAIL_SMTP_SERVER,
    EMAIL_SMTP_PORT,
    EMAIL_SENDER,
    EMAIL_PASSWORD,
    EMAIL_RECEIVER
)


def send_serverchan(title: str, content: str) -> bool:
    """
    通过 Server酱 发送微信推送
    文档：https://sct.ftqq.com/
    """
    if not SERVERCHAN_SENDKEY:
        print("[通知] Server酱 SendKey 未配置，跳过推送")
        return False
    
    url = f"https://sctapi.ftqq.com/{SERVERCHAN_SENDKEY}.send"
    
    try:
        response = requests.post(url, data={
            "title": title,
            "desp": content
        }, timeout=10)
        
        result = response.json()
        if result.get("code") == 0:
            print("[通知] Server酱推送成功")
            return True
        else:
            print(f"[通知] Server酱推送失败: {result}")
            return False
    except Exception as e:
        print(f"[通知] Server酱推送异常: {e}")
        return False


def send_email(title: str, content: str) -> bool:
    """发送邮件通知"""
    if not EMAIL_ENABLED:
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER
        msg['Subject'] = title
        
        # 将 Markdown 转为 HTML
        html_content = content.replace('\n', '<br>')
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))
        
        with smtplib.SMTP_SSL(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        
        print("[通知] 邮件发送成功")
        return True
    except Exception as e:
        print(f"[通知] 邮件发送失败: {e}")
        return False


def notify_new_posts(posts: List[Dict]):
    """
    通知新帖子
    posts: 新帖子列表
    """
    if not posts:
        return
    
    # 构建通知内容
    title = f"🔔 小红书监控 - 发现 {len(posts)} 条新帖子"
    
    content_lines = [f"## 发现 {len(posts)} 条新帖子\n"]
    
    for i, post in enumerate(posts, 1):
        content_lines.append(f"### {i}. {post.get('title', '无标题')}")
        content_lines.append(f"- **关键词**: {post.get('keyword', '-')}")
        content_lines.append(f"- **时间**: {post.get('publish_time', '未知')}")
        content_lines.append(f"- **链接**: [{post.get('note_id')}]({post.get('url', '#')})")
        content_lines.append("")
    
    content = "\n".join(content_lines)
    
    # 优先使用 Server酱
    if SERVERCHAN_SENDKEY:
        send_serverchan(title, content)
    
    # 邮件备选
    if EMAIL_ENABLED:
        send_email(title, content)
