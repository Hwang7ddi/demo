import os
import sys
import subprocess
import shutil

def build_console_executable():
    """
    将Flask应用打包为带有控制台窗口的Windows可执行文件
    """
    print("开始打包Flask应用为带控制台的exe文件...")
    
    # 确保在正确的目录中
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    print(f"工作目录: {project_dir}")
    
    # 检查必要文件是否存在
    required_files = ["app.py", "templates", "static"]
    for file in required_files:
        if not os.path.exists(file):
            print(f"错误: 必要文件或目录 {file} 不存在!")
            return False
    
    # 创建打包命令
    cmd = [
        "pyinstaller",
        "--onefile",                 # 打包为单个exe文件
        "--console",                 # 显示控制台窗口
        "--name", "校园宿舍管理系统",      # exe文件名
        "--icon", "NONE",            # 不使用图标
        "--add-data", "templates;templates",  # 添加模板文件夹
        "--add-data", "static;static",        # 添加静态文件夹
        "--add-data", "instance;instance",    # 添加instance文件夹及其内容
        "--hidden-import", "flask",
        "--hidden-import", "flask_sqlalchemy",
        "--hidden-import", "werkzeug",
        "--hidden-import", "jinja2",
        "--hidden-import", "sqlalchemy",
        "--hidden-import", "sqlite3",
        "app.py"                     # 主程序文件
    ]
    
    print("正在执行打包命令...")
    print("命令:", " ".join(cmd))
    
    try:
        # 执行打包命令
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)  # 设置10分钟超时
        
        print(f"返回码: {result.returncode}")
        print("标准输出:")
        print(result.stdout)
        
        if result.returncode == 0:
            print("\n打包成功!")
            print("可执行文件位于 dist/校园宿舍管理系统.exe")
            
            # 复制数据库文件到dist/instance目录，确保exe文件运行时有初始数据
            dist_dir = os.path.join(project_dir, "dist")
            dist_instance_dir = os.path.join(dist_dir, "instance")
            
            # 确保dist目录中的instance目录存在
            if not os.path.exists(dist_instance_dir):
                os.makedirs(dist_instance_dir)
            
            if os.path.exists(dist_dir):
                print("\n生成的文件:")
                for file in os.listdir(dist_dir):
                    file_path = os.path.join(dist_dir, file)
                    if os.path.isfile(file_path):  # 只显示文件，不显示目录
                        size = os.path.getsize(file_path)
                        print(f"  {file} ({size} bytes)")
                
                # 复制instance目录中的所有内容到dist的instance目录
                source_instance_dir = os.path.join(project_dir, "instance")
                if os.path.exists(source_instance_dir):
                    for item in os.listdir(source_instance_dir):
                        source_item = os.path.join(source_instance_dir, item)
                        dest_item = os.path.join(dist_instance_dir, item)
                        if os.path.isfile(source_item):
                            shutil.copy2(source_item, dest_item)
                            print(f"\n已复制数据库文件到: {dest_item}")
                        elif os.path.isdir(source_item):
                            if os.path.exists(dest_item):
                                shutil.rmtree(dest_item)
                            shutil.copytree(source_item, dest_item)
                            print(f"\n已复制目录到: {dest_item}")
                    # 确保有数据库文件
                    db_path = os.path.join(dist_instance_dir, "campus.db")
                    if os.path.exists(db_path):
                        db_size = os.path.getsize(db_path)
                        print(f"✓ 数据库文件 campus.db 已就位 ({db_size} bytes)")
                    else:
                        print("⚠ 注意: instance目录中没有发现campus.db文件，系统启动时将创建新的空数据库")
                else:
                    print("\n警告: 未找到instance目录，exe运行时将创建新的空数据库")
                    print("提示: 如果你已有数据，请确保在项目目录中有instance文件夹")
            
            return True
        else:
            print("\n打包失败!")
            print("错误信息:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("\n错误: 打包过程超时（超过10分钟）")
        return False
    except Exception as e:
        print(f"\n执行打包时发生错误: {e}")
        return False

def create_readme():
    """
    创建使用说明文件
    """
    readme_content = '''校园宿舍管理系统使用说明
========================

运行方式：
1. 双击运行 "校园宿舍管理系统.exe"
2. 程序启动后会显示控制台窗口，其中包含运行日志
3. 在浏览器中访问 http://127.0.0.1:5000 使用系统

注意事项：
1. 如果要保留原有数据，请确保在运行exe文件的同一目录下放置campus.db数据库文件
2. 第一次运行时如果没有数据库文件，系统会自动创建一个新的空数据库
3. 默认测试账户：
   - 管理员：admin / admin123
   - 学生：student / student123
   - 工作人员：staff1 / staff123

数据持久化：
- 系统会优先使用与exe文件同目录下的instance/campus.db数据库文件
- 首次运行时如果找不到数据库文件，将自动创建新的空数据库
- 如需保留数据，请确保campus.db文件位于exe文件同一目录的instance子目录中
'''

    with open("使用说明.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("已创建使用说明.txt文件")

if __name__ == "__main__":
    # 创建使用说明文件
    create_readme()
    
    # 执行打包
    success = build_console_executable()
    if success:
        print("\n" + "="*50)
        print("打包完成! 您可以在 dist 目录中找到可执行文件")
        print("同时请查看使用说明.txt了解如何保留数据")
        print("="*50)
    else:
        print("\n" + "="*50)
        print("打包失败，请检查错误信息")
        print("="*50)
        sys.exit(1)