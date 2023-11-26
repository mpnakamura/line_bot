import os
import psycopg2
from datetime import datetime

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
            # UserTokenUsage テーブル作成
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS UserTokenUsage (
                user_id VARCHAR(255) NOT NULL,
                date DATE NOT NULL,
                tokens_used INT DEFAULT 0,
                PRIMARY KEY (user_id, date)
                
            );
            """)
            cursor.execute("""
    CREATE TABLE IF NOT EXISTS UserSelections (
    reminder_id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    details TEXT,
    datetime TIMESTAMP,
    );
""")


            
        conn.commit()
    finally:
        conn.close()

def get_recent_messages(line_user_id, limit=4):
    """
    特定のユーザーIDに関連する最新の3件のメッセージを取得する関数。
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
    新しいメッセージをデータベースに保存し、古いメッセージを削除する関数。
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 新しいメッセージを挿入
            cursor.execute("""
            INSERT INTO Messages (id, lineUserId, content, role, createdAt)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP);
            """, (id, line_user_id, content, role))

            # 最新の3件を除いて古いメッセージを削除
            cursor.execute("""
            DELETE FROM Messages
            WHERE id NOT IN (
                SELECT id FROM Messages
                WHERE lineUserId = %s
                ORDER BY createdAt DESC
                LIMIT 5
            ) AND lineUserId = %s;
            """, (line_user_id, line_user_id))

            conn.commit()
    finally:
        conn.close()
        
def update_token_usage(user_id, tokens):
    """
    ユーザーの1日あたりのトークン使用量を更新する。
    """
    date_today = datetime.now().date()
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            INSERT INTO UserTokenUsage (user_id, date, tokens_used)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, date)
            DO UPDATE SET tokens_used = UserTokenUsage.tokens_used + EXCLUDED.tokens_used;
            """, (user_id, date_today, tokens))
            conn.commit()
    finally:
        conn.close()

def check_token_limit(user_id, token_limit):
    """
    ユーザーが1日あたりのトークン使用量の制限に達しているか確認する。
    """
    date_today = datetime.now().date()
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            SELECT tokens_used FROM UserTokenUsage
            WHERE user_id = %s AND date = %s;
            """, (user_id, date_today))
            result = cursor.fetchone()
            if result and result[0] >= token_limit:
                return True
            return False
    finally:
        conn.close()


# データベース初期化関数の呼び出し
initialize_db()
