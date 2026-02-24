import sqlite3
import os
import sys

def migrate_database():
    """
    统一的数据库迁移脚本，用于添加所有缺失的字段
    支持student表的bed_number和phone字段，
    以及user表的email和reset_token字段，
    还有repair表的image_url字段
    """
    # 使用正确的数据库路径
    db_path = os.path.join('instance', 'campus.db')
    
    # 检查数据库文件是否存在
    if not os.path.exists(db_path):
        print("数据库文件不存在，将在下次应用启动时自动创建。")
        return True
    
    try:
        # 连接到数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("开始数据库迁移...")
        
        # 检查并更新student表
        print("\n--- 检查 student 表 ---")
        cursor.execute("PRAGMA table_info(student)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        print("当前 student 表的字段:")
        for column in columns:
            print(f"  {column[1]} ({column[2]})")
        
        # 添加bed_number字段（如果不存在）
        if 'bed_number' not in column_names:
            try:
                cursor.execute("ALTER TABLE student ADD COLUMN bed_number VARCHAR(10)")
                print("成功添加 bed_number 字段")
            except sqlite3.OperationalError as e:
                print(f"添加 bed_number 字段时出错: {e}")
        else:
            print("bed_number 字段已存在")
        
        # 添加phone字段（如果不存在）
        if 'phone' not in column_names:
            try:
                cursor.execute("ALTER TABLE student ADD COLUMN phone VARCHAR(20)")
                print("成功添加 phone 字段")
            except sqlite3.OperationalError as e:
                print(f"添加 phone 字段时出错: {e}")
        else:
            print("phone 字段已存在")
        
        # 检查并更新user表
        print("\n--- 检查 user 表 ---")
        cursor.execute("PRAGMA table_info(user)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        print("当前 user 表的字段:")
        for column in columns:
            print(f"  {column[1]} ({column[2]})")
        
        # 添加email字段（如果不存在）
        if 'email' not in column_names:
            try:
                cursor.execute("ALTER TABLE user ADD COLUMN email VARCHAR(100)")
                print("成功添加 email 字段")
            except sqlite3.OperationalError as e:
                if 'duplicate column name' in str(e):
                    print("email 字段已存在")
                else:
                    print(f"添加 email 字段时出错: {e}")
        else:
            print("email 字段已存在")
        
        # 添加reset_token字段（如果不存在）
        if 'reset_token' not in column_names:
            try:
                cursor.execute("ALTER TABLE user ADD COLUMN reset_token VARCHAR(50)")
                print("成功添加 reset_token 字段")
            except sqlite3.OperationalError as e:
                if 'duplicate column name' in str(e):
                    print("reset_token 字段已存在")
                else:
                    print(f"添加 reset_token 字段时出错: {e}")
        else:
            print("reset_token 字段已存在")
        
        # 检查并更新repair表
        print("\n--- 检查 repair 表 ---")
        cursor.execute("PRAGMA table_info(repair)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        print("当前 repair 表的字段:")
        for column in columns:
            print(f"  {column[1]} ({column[2]})")
        
        # 添加image_url字段（如果不存在）
        if 'image_url' not in column_names:
            try:
                cursor.execute("ALTER TABLE repair ADD COLUMN image_url VARCHAR(200)")
                print("成功添加 image_url 字段")
            except sqlite3.OperationalError as e:
                if 'duplicate column name' in str(e):
                    print("image_url 字段已存在")
                else:
                    print(f"添加 image_url 字段时出错: {e}")
        else:
            print("image_url 字段已存在")
        
        # 提交更改并关闭连接
        conn.commit()
        conn.close()
        
        print("\n=== 数据库迁移完成! ===")
        return True
        
    except Exception as e:
        print(f"数据库迁移过程中出现错误: {e}")
        return False

if __name__ == "__main__":
    print("开始执行数据库迁移...")
    success = migrate_database()
    if success:
        print("数据库迁移成功!")
    else:
        print("数据库迁移失败!")
        sys.exit(1)