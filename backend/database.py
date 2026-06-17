"""GaussDB / openGauss 数据库连接管理 (兼容 PostgreSQL)"""
import os
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "studentdb"),
    "user": os.getenv("DB_USER", "gaussuser"),
    "password": os.getenv("DB_PASSWORD", "GaussDB@123"),
}

# 简单连接池
connection_pool = pool.ThreadedConnectionPool(minconn=2, maxconn=10, **DB_CONFIG)


@contextmanager
def get_connection():
    """获取数据库连接的上下文管理器"""
    conn = connection_pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        connection_pool.putconn(conn)


def init_db():
    """初始化数据库表"""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id          SERIAL PRIMARY KEY,
                name        VARCHAR(50)  NOT NULL,
                gender      VARCHAR(10)  DEFAULT '男',
                age         INTEGER      DEFAULT 20,
                major       VARCHAR(100) DEFAULT '计算机科学与技术',
                class_name  VARCHAR(100) DEFAULT '',
                phone       VARCHAR(20)  DEFAULT '',
                email       VARCHAR(100) DEFAULT '',
                created_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
