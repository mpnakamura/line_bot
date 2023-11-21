import os
import psycopg2
import uuid

DATABASE_URL = os.environ['DATABASE_URL']

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()

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

# コミットして変更を確定
conn.commit()

# 新しいメッセージを追加する処理
# 生成したUUID、ユーザーID、メッセージ内容、ロールに適切な値を設定
new_uuid = str(uuid.uuid4())  # 新しいUUIDを生成
user_id = "ユーザーID"         # 適切なユーザーIDに置き換える
message_content = "メッセージ内容"  # メッセージの内容
role = "ロール"                # 'user' または 'bot' などのロール

cursor.execute("""
INSERT INTO Messages (id, lineUserId, content, role, createdAt)
VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP);
""", (new_uuid, user_id, message_content, role))

# コミットして変更を確定
conn.commit()

cursor.close()
conn.close()

def get_recent_messages(line_user_id, limit=3):
    with conn.cursor() as cursor:
        cursor.execute("""
        SELECT content, createdAt FROM Messages
        WHERE lineUserId = %s
        ORDER BY createdAt DESC
        LIMIT %s;
        """, (line_user_id, limit))
        return cursor.fetchall()
    
def save_message(id, line_user_id, content, role):
    with conn.cursor() as cursor:
        cursor.execute("""
        INSERT INTO Messages (id, lineUserId, content, role, createdAt)
        VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP);
        """, (id, line_user_id, content, role))
        conn.commit()