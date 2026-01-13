"""
SQLite 数据库模块 - 用于去重和记录
"""
print("LOADED db.py FROM:", __file__)

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from api_config import DATABASE_PATH



def get_connection() -> sqlite3.Connection:
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """初始化数据库表"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id TEXT UNIQUE NOT NULL,
            platform TEXT DEFAULT 'xiaohongshu',
            title TEXT,
            link TEXT,
            keyword TEXT,
            publish_time TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_note_id ON notes(note_id)
    """)
    
    conn.commit()
    conn.close()
    print(f"[DB] 数据库初始化完成: {DATABASE_PATH}")


def note_exists(note_id: str) -> bool:
    """检查帖子是否已存在"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM notes WHERE note_id = ?", (note_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def save_note(note: Dict) -> bool:
    """
    保存帖子到数据库
    返回 True 表示新帖子，False 表示已存在
    """
    if note_exists(note["note_id"]):
        return False
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO notes (note_id, platform, title, link, keyword, publish_time, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            note["note_id"],
            note.get("platform", "xiaohongshu"),
            note.get("title", ""),
            note.get("link", ""),
            note.get("keyword", ""),
            note.get("publish_time", ""),
            datetime.now().isoformat()
        ))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False


def get_notes_count() -> int:
    """获取已保存帖子总数"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM notes")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_recent_notes(limit: int = 20) -> List[Dict]:
    """获取最近的帖子"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM notes ORDER BY created_at DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
