-- ============================================
-- 易享圈 二手交易平台数据库
-- ============================================

-- 1. 创建数据库
CREATE DATABASE YiXiangQuanDB;
GO

-- 2. 使用数据库
USE YiXiangQuanDB;
GO

-- 3. 创建用户表
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

-- 4. 创建分类表
CREATE TABLE categories (
    id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(50) NOT NULL
);
GO

-- 5. 创建帖子表
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
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE()
);
GO

-- 6. 创建收藏表
CREATE TABLE favorites (
    id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT FOREIGN KEY REFERENCES users(id),
    post_id INT FOREIGN KEY REFERENCES posts(id),
    created_at DATETIME DEFAULT GETDATE(),
    UNIQUE(user_id, post_id)
);
GO

-- 7. 创建评论表
CREATE TABLE comments (
    id INT PRIMARY KEY IDENTITY(1,1),
    post_id INT FOREIGN KEY REFERENCES posts(id),
    user_id INT FOREIGN KEY REFERENCES users(id),
    content NVARCHAR(500),
    created_at DATETIME DEFAULT GETDATE()
);
GO

-- 8. 插入分类数据
INSERT INTO categories (name) VALUES 
('手机数码'), ('电脑配件'), ('图书教材'), ('生活用品'), ('服饰鞋包'), ('其他');
GO

-- 9. 插入测试用户
INSERT INTO users (username, password, nickname, is_admin, is_vip) 
VALUES ('admin', 'admin123', '系统管理员', 1, 1);
GO

INSERT INTO users (username, password, nickname, is_vip) 
VALUES ('test', '123456', '测试用户', 0);
GO

-- 10. 插入测试帖子
INSERT INTO posts (user_id, category_id, title, description, price) 
VALUES (2, 1, 'iPhone 14 Pro 九成新', '自用iPhone 14 Pro，256GB，深空黑色，无拆无修', 5999);
GO

INSERT INTO posts (user_id, category_id, title, description, price) 
VALUES (2, 3, 'Java编程思想', '正版图书，几乎全新', 45);
GO

-- 11. 查看数据验证
SELECT * FROM users;
SELECT * FROM categories;
SELECT * FROM posts;
GO

PRINT '========================================';
PRINT '易享圈数据库创建成功！';
PRINT '测试账号：';
PRINT '  - 管理员: admin / admin123';
PRINT '  - 测试用户: test / 123456';
PRINT '========================================';
GO