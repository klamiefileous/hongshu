from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

app = FastAPI()

# 添加 CORS 中间件 - 这是关键！
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/posts")
def get_posts(keyword: str = None):
    conn = sqlite3.connect("posts.db")
    cur = conn.cursor()
    if keyword:
        cur.execute("SELECT id, keyword, title, url, publish_time FROM posts WHERE keyword = ? ORDER BY publish_time DESC", (keyword,))
    else:
        cur.execute("SELECT id, keyword, title, url, publish_time FROM posts ORDER BY publish_time DESC")
    rows = cur.fetchall()
    conn.close()
    return [
        {"id": r[0], "keyword": r[1], "title": r[2], "url": r[3], "publish_time": r[4]}
        for r in rows
    ]

@app.get("/")
def health_check():
    return {"status": "ok"}
