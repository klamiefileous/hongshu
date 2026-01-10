"""
SQLite 数据库操作模块
用于存储已抓取的帖子，实现去重
"""

import sqlite3
from typing import List, Dict, Optional
from config import DB_PATH


def init_db():
    """初始化数据库，创建表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id TEXT UNIQUE NOT NULL,
            platform TEXT DEFAULT 'xiaohongshu',
            title TEXT,
            publish_time TEXT,
            url TEXT,
            keyword TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("[DB] 数据库初始化完成")


def get_existing_note_ids() -> set:
    """获取所有已存在的 note_id"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT note_id FROM notes")
    result = {row[0] for row in cursor.fetchall()}
    conn.close()
    return result


def save_notes(notes: List[Dict]) -> List[Dict]:
    """
    保存新帖子到数据库
    返回：实际新增的帖子列表
    """
    if not notes:
        return []
    
    existing_ids = get_existing_note_ids()
    new_notes = [n for n in notes if n['note_id'] not in existing_ids]
    
    if not new_notes:
        return []
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for note in new_notes:
        try:
            cursor.execute('''
                INSERT INTO notes (note_id, platform, title, publish_time, url, keyword)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                note['note_id'],
                note.get('platform', 'xiaohongshu'),
                note.get('title', ''),
                note.get('publish_time', ''),
                note.get('url', ''),
                note.get('keyword', '')
            ))
        except sqlite3.IntegrityError:
            # note_id 已存在，跳过
            pass
    
    conn.commit()
    conn.close()
    
    print(f"[DB] 新增 {len(new_notes)} 条帖子")
    return new_notes


def get_recent_notes(limit: int = 50) -> List[Dict]:
    """获取最近的帖子"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM notes ORDER BY created_at DESC LIMIT ?
    ''', (limit,))
    result = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return result
