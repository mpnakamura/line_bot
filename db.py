import os
import psycopg2
import uuid

DATABASE_URL = os.environ['DATABASE_URL']

def get_db_connection():
    """
    新しいデータベース接続を確立する関数。
    """
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def initialize_db():
    """
    テーブルとインデックスを作成する関数。
    アプリケーションの起動時に一度だけ呼び出されることを想定。
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # テーブル作成
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Messages (
                id UUID PRIMARY KEY,
                lineUserId VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                role VARCHAR(50) NOT NULL,
                createdAt TIMESTAMP NOT NULL,
                updatedAt TIMESTAMP
            );
            """)
            # インデックス作成
            cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_lineUserId ON Messages (lineUserId);
            """)
        conn.commit()
    finally:
        conn.close()

def get_recent_messages(line_user_id, limit=3):
    """
    特定のユーザーIDに関連する最新のメッセージを取得する関数。
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            SELECT content, createdAt FROM Messages
            WHERE lineUserId = %s
            ORDER BY createdAt DESC
            LIMIT %s;
            """, (line_user_id, limit))
            return cursor.fetchall()
    finally:
        conn.close()

def save_message(id, line_user_id, content, role):
    """
    新しいメッセージをデータベースに保存する関数。
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            INSERT INTO Messages (id, lineUserId, content, role, createdAt)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP);
            """, (id, line_user_id, content, role))
            conn.commit()
    finally:
        conn.close()

# データベース初期化関数の呼び出し
initialize_db()
