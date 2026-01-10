"""
小红书监控配置文件
"""

# ==================== 关键词配置 ====================
KEYWORDS = ["msi", "微星"]  # 需要监控的关键词列表

# ==================== 抓取配置 ====================
MAX_POSTS = 15  # 每次抓取的最大帖子数
CHECK_INTERVAL_MINUTES = 10  # 检查间隔（分钟）

# ==================== 浏览器配置 ====================
USER_DATA_DIR = "./user_data"  # 浏览器用户数据目录（保存登录态）
HEADLESS = False  # 是否无头模式（首次登录必须为 False）

# ==================== Server酱推送配置 ====================
# 获取 SendKey：https://sct.ftqq.com/
SERVERCHAN_SENDKEY = ""  # 你的 Server酱 SendKey

# ==================== 邮件推送配置（备选）====================
EMAIL_ENABLED = False  # 是否启用邮件推送
EMAIL_SMTP_SERVER = "smtp.qq.com"
EMAIL_SMTP_PORT = 465
EMAIL_SENDER = ""  # 发件邮箱
EMAIL_PASSWORD = ""  # 邮箱授权码（非登录密码）
EMAIL_RECEIVER = ""  # 收件邮箱

# ==================== 数据库配置 ====================
DB_PATH = "./xhs_notes.db"