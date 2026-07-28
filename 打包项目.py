import os
import shutil
import zipfile
from datetime import datetime

# ============================================
# 易享圈项目一键打包脚本
# ============================================

# 配置区域 - 请修改为你的实际路径
ANDROID_PROJECT_PATH = r"D:\andro_studio\AndroidstudioProjects\Yixiangquan"
BACKEND_PROJECT_PATH = r"C:\Users\Admin\Desktop\yixiangquan"
APK_PATH = r"D:\andro_studio\AndroidstudioProjects\Yixiangquan\app\build\outputs\apk\debug\app-debug.apk"
OUTPUT_DIR = r"C:\Users\Admin\Desktop"

# 项目信息
CLASS_NAME = "25专升本计科03班"
PROJECT_NAME = "易享圈"
STUDENT_IDS = "13,18,08"  # 修改为你们的学号末两位
STUDENT_NAMES = "黄锡辉,李智辉,何梓恒"  # 修改为你们的姓名

# ============================================
# 以下代码无需修改
# ============================================

def create_zip(zip_path, source_dir):
    """创建zip压缩包"""
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(source_dir))
                zipf.write(file_path, arcname)
    print(f"  ✓ 已添加: {os.path.basename(source_dir)}")

def copy_directory(src, dst):
    """复制目录"""
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    print(f"  ✓ 已复制: {os.path.basename(src)}")

def main():
    print("=" * 50)
    print("     易享圈项目一键打包工具")
    print("=" * 50)
    print()

    # 生成压缩包名称
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"{CLASS_NAME}+{PROJECT_NAME}+{STUDENT_IDS}+{STUDENT_NAMES}.zip"
    zip_name = zip_name.replace(" ", "")
    zip_path = os.path.join(OUTPUT_DIR, zip_name)

    # 创建临时文件夹
    temp_dir = os.path.join(OUTPUT_DIR, "temp_package")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    print("正在整理项目文件...")
    print()

    # 1. 复制 Android 项目
    print("[1/5] 复制 Android 客户端...")
    android_dest = os.path.join(temp_dir, "01_Android客户端", "Yixiangquan")
    copy_directory(ANDROID_PROJECT_PATH, android_dest)

    # 2. 复制 APK
    print("[2/5] 复制 APK 安装包...")
    apk_dest = os.path.join(temp_dir, "01_Android客户端", "APK")
    os.makedirs(apk_dest, exist_ok=True)
    shutil.copy2(APK_PATH, os.path.join(apk_dest, "易享圈_v1.0.apk"))
    print(f"  ✓ 已复制: 易享圈_v1.0.apk")

    # 3. 复制后端项目
    print("[3/5] 复制后端服务端...")
    backend_dest = os.path.join(temp_dir, "02_后端服务端", "yixiangquan")
    copy_directory(BACKEND_PROJECT_PATH, backend_dest)

    # 4. 创建数据库脚本
    print("[4/5] 创建数据库脚本...")
    db_dir = os.path.join(temp_dir, "03_数据库")
    os.makedirs(db_dir, exist_ok=True)
    
    sql_script = '''-- ============================================
-- 易享圈 二手交易平台数据库
-- ============================================

-- 创建数据库
CREATE DATABASE YiXiangQuanDB;
GO

USE YiXiangQuanDB;
GO

-- 用户表
CREATE TABLE users (
    id INT PRIMARY KEY IDENTITY(1,1),
    username NVARCHAR(50) UNIQUE NOT NULL,
    password NVARCHAR(100) NOT NULL,
    nickname NVARCHAR(50),
    email NVARCHAR(100),
    avatar NVARCHAR(500),
    is_vip BIT DEFAULT 0,
    is_admin BIT DEFAULT 0,
    status BIT DEFAULT 1,
    created_at DATETIME DEFAULT GETDATE()
);
GO

-- 分类表
CREATE TABLE categories (
    id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(50) NOT NULL
);
GO

-- 帖子表
CREATE TABLE posts (
    id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT FOREIGN KEY REFERENCES users(id),
    category_id INT FOREIGN KEY REFERENCES categories(id),
    title NVARCHAR(100) NOT NULL,
    description NVARCHAR(MAX),
    price DECIMAL(10,2),
    images NVARCHAR(1000),
    view_count INT DEFAULT 0,
    status NVARCHAR(20) DEFAULT 'active',
    is_sold VARCHAR(10) DEFAULT '0',
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE()
);
GO

-- 收藏表
CREATE TABLE favorites (
    id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT FOREIGN KEY REFERENCES users(id),
    post_id INT FOREIGN KEY REFERENCES posts(id),
    created_at DATETIME DEFAULT GETDATE(),
    UNIQUE(user_id, post_id)
);
GO

-- 评论表
CREATE TABLE comments (
    id INT PRIMARY KEY IDENTITY(1,1),
    post_id INT FOREIGN KEY REFERENCES posts(id),
    user_id INT FOREIGN KEY REFERENCES users(id),
    content NVARCHAR(500),
    created_at DATETIME DEFAULT GETDATE()
);
GO

-- 插入分类数据
INSERT INTO categories (name) VALUES 
('手机数码'), ('电脑配件'), ('图书教材'), ('生活用品'), ('服饰鞋包'), ('其他');
GO

-- 插入测试用户
INSERT INTO users (username, password, nickname, is_admin, is_vip) 
VALUES ('admin', 'admin123', '系统管理员', 1, 1);
GO

INSERT INTO users (username, password, nickname, is_vip) 
VALUES ('test', '123456', '测试用户', 0);
GO

-- 插入测试帖子
INSERT INTO posts (user_id, category_id, title, description, price, images) 
VALUES (2, 1, 'iPhone 14 Pro 九成新', '自用iPhone 14 Pro，256GB，深空黑色', 5999, 'default');
GO

PRINT '数据库创建成功！'
PRINT '测试账号：admin/admin123, test/123456'
GO
'''
    
    with open(os.path.join(db_dir, "YiXiangQuanDB.sql"), "w", encoding="utf-8") as f:
        f.write(sql_script)
    print("  ✓ 已创建: YiXiangQuanDB.sql")

    # 5. 创建部署文档
    print("[5/5] 创建部署文档...")
    doc_dir = os.path.join(temp_dir, "04_文档")
    os.makedirs(doc_dir, exist_ok=True)
    
    deploy_doc = '''========================================
         易享圈 二手交易平台
           部署说明
========================================

一、环境要求
-----------
1. Windows 10/11 操作系统
2. SQL Server 2019 或更高版本
3. JDK 11 或更高版本
4. Android 9.0 或更高版本

二、数据库部署
-----------
1. 安装 SQL Server 和 SSMS
2. 打开 SSMS，执行 03_数据库/YiXiangQuanDB.sql
3. 启用 sa 账号，设置密码为 123456
4. 启用 TCP/IP 协议，端口 1433

三、后端部署
-----------
1. 安装 JDK 11
2. 打开 VS Code，打开 02_后端服务端/yixiangquan 文件夹
3. 修改 src/main/resources/application.properties 中的数据库密码
4. 运行 YiXiangQuanApplication.java
5. 看到"服务端启动成功"即完成

四、Android 客户端安装
-----------
1. 将 01_Android客户端/APK/易享圈_v1.0.apk 复制到手机
2. 点击安装
3. 修改 ApiService.java 中的 IP 地址（如需重新编译）

五、测试账号
-----------
管理员：admin / admin123
测试用户：test / 123456

========================================
'''
    
    with open(os.path.join(doc_dir, "部署说明.txt"), "w", encoding="utf-8") as f:
        f.write(deploy_doc)
    print("  ✓ 已创建: 部署说明.txt")

    # 创建技术栈说明
    tech_doc = '''========================================
       易享圈 技术栈清单
========================================

一、Android 客户端
-----------------
1. Activity 组件
2. Android 布局管理
3. UI控件（TextView、EditText、ImageView、Button）
4. RecyclerView（列表展示）
5. Spinner（下拉选择）
6. Intent（页面跳转）
7. 事件处理
8. Handler 处理机制
9. Fragment + ViewPager2（底部导航）
10. SharedPreferences（本地存储）
11. OkHttp（网络请求）
12. Gson（JSON解析）
13. Glide（图片加载）
14. CircleImageView（圆形头像）

二、后端服务端
-------------
1. Spring Boot 2.7.0
2. Spring MVC
3. MyBatis
4. SQL Server JDBC

三、数据库
---------
1. SQL Server 2022
2. 表：users、posts、categories、favorites、comments

四、开发工具
-----------
1. Android Studio（客户端）
2. VS Code（后端）
3. SSMS（数据库管理）

========================================
'''
    
    with open(os.path.join(doc_dir, "技术栈说明.txt"), "w", encoding="utf-8") as f:
        f.write(tech_doc)
    print("  ✓ 已创建: 技术栈说明.txt")

    print()
    print("正在打包压缩...")

    # 创建压缩包
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(temp_dir))
                zipf.write(file_path, arcname)

    # 清理临时文件夹
    shutil.rmtree(temp_dir)

    print()
    print("=" * 50)
    print("打包完成！")
    print("=" * 50)
    print(f"压缩包位置: {zip_path}")
    print(f"压缩包大小: {os.path.getsize(zip_path) / 1024 / 1024:.2f} MB")
    print()

    # 打开文件夹
    os.startfile(OUTPUT_DIR)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"错误: {e}")
        input("按回车键退出...")