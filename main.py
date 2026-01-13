from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sqlite3
from datetime import datetime
from db import init_database

app = FastAPI()

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据模型
class PostCreate(BaseModel):
    title: str
    keyword: str
    url: str
    created_at: Optional[str] = None

# 初始化数据库
def init_db():
    conn = sqlite3.connect("posts.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            keyword TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# POST /posts - 写入帖子（自动去重）
@app.post("/posts")
def create_post(post: PostCreate):
    conn = sqlite3.connect("posts.db")
    cur = conn.cursor()
    
    # 使用 url 去重
    cur.execute("SELECT id FROM posts WHERE url = ?", (post.url,))
    existing = cur.fetchone()
    
    if existing:
        conn.close()
        return {"message": "Post already exists", "id": existing[0]}
    
    created_at = post.created_at or datetime.now().isoformat()
    
    cur.execute(
        "INSERT INTO posts (title, keyword, url, created_at) VALUES (?, ?, ?, ?)",
        (post.title, post.keyword, post.url, created_at)
    )
    conn.commit()
    post_id = cur.lastrowid
    conn.close()
    
    return {"message": "Post created", "id": post_id}

# GET /posts - 读取帖子
@app.get("/posts")
def get_posts(keyword: Optional[str] = None):
    conn = sqlite3.connect("posts.db")
    cur = conn.cursor()
    
    if keyword:
        cur.execute(
            "SELECT id, title, keyword, url, created_at FROM posts WHERE keyword = ? ORDER BY created_at DESC",
            (keyword,)
        )
    else:
        cur.execute(
            "SELECT id, title, keyword, url, created_at FROM posts ORDER BY created_at DESC"
        )
    
    rows = cur.fetchall()
    conn.close()
    
    return [
        {"id": r[0], "title": r[1], "keyword": r[2], "url": r[3], "created_at": r[4]}
        for r in rows
    ]

# 健康检查
@app.get("/")
def health_check():
    return {"status": "ok"}

