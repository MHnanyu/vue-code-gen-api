"""
数据库初始化脚本
创建数据库、集合和索引
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from pymongo import MongoClient
from app.config import settings


def init_database():
    client = MongoClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    
    print(f"正在初始化数据库: {settings.DATABASE_NAME}")
    
    # 创建 sessions 集合
    if "sessions" not in db.list_collection_names():
        db.create_collection("sessions")
        print("  - 创建集合: sessions")
    else:
        print("  - 集合已存在: sessions")
    
    # 创建 users 集合
    if "users" not in db.list_collection_names():
        db.create_collection("users")
        print("  - 创建集合: users")
    else:
        print("  - 集合已存在: users")
    
    # 创建 sessions 索引
    sessions = db["sessions"]
    
    sessions.create_index("id", unique=True)
    print("  - 创建索引: sessions.id (唯一)")
    
    sessions.create_index("userId")
    print("  - 创建索引: sessions.userId")
    
    sessions.create_index([("updatedAt", -1)])
    print("  - 创建索引: sessions.updatedAt (降序)")
    
    # 创建 users 索引
    users = db["users"]
    
    users.create_index("id", unique=True)
    print("  - 创建索引: users.id (唯一)")
    
    users.create_index("username", unique=True)
    print("  - 创建索引: users.username (唯一)")
    
    client.close()
    
    print("\n数据库初始化完成!")
    print(f"- 数据库: {settings.DATABASE_NAME}")
    print("- 集合: sessions, users")
    print("- 索引:")
    print("  - sessions.id (唯一)")
    print("  - sessions.userId")
    print("  - sessions.updatedAt (降序)")
    print("  - users.id (唯一)")
    print("  - users.username (唯一)")


if __name__ == "__main__":
    init_database()
