from werkzeug.security import check_password_hash
import sqlite3
import os

# 连接到数据库
db_path = 'campus.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查询用户'user'的信息
    cursor.execute("SELECT id, username, password, role, name FROM user WHERE username = 'user'")
    user = cursor.fetchone()
    
    if user:
        print(f"找到用户: {user[1]}")
        print(f"角色: {user[3]}")
        print(f"密码哈希: {user[2]}")
        
        # 验证密码
        password_to_check = 'user123'
        is_valid = check_password_hash(user[2], password_to_check)
        print(f"密码 '{password_to_check}' 验证结果: {is_valid}")
    else:
        print("未找到用户名为'user'的用户")
    
    conn.close()
else:
    print("数据库文件不存在")