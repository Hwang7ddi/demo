import logging
import os
import sys
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import random
import string
import smtplib  # 或使用 Flask-Mail
from email.mime.text import MIMEText



# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 初始化Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'campus_management_system_2024'  # 安全密钥




@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        input_username = request.form['username']  # 用户名或学号
        name = request.form['name']
        
        # 先尝试按用户名查找
        user = User.query.filter_by(username=input_username, name=name).first()
        
        # 如果用户名没找到，尝试按学号查找
        if not user:
            student = Student.query.filter_by(student_id=input_username).first()
            if student and student.user.name == name:
                user = User.query.filter_by(id=student.user_id).first()
        
        # 特殊处理测试账户
        if not user:
            # 检查是否为测试账户
            test_users = [
                {'username': 'admin', 'name': 'admin'},
                {'username': 'student', 'name': 'student'},
                {'username': 'staff1', 'name': 'staff'}
            ]
            
            for test_user in test_users:
                if input_username == test_user['username'] and name == test_user['name']:
                    user = User.query.filter_by(username=test_user['username']).first()
                    break
        
        if user:
            # 生成临时令牌
            import secrets
            token = secrets.token_urlsafe(32)
            user.reset_token = token
            db.session.commit()
            
            # 重定向到重置密码页面
            flash("身份验证成功，请设置新密码。")
            return redirect(url_for('reset_password', token=token))
        
        flash("提供的信息不匹配，请重新输入。", "error")
    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # 验证令牌
    user = User.query.filter_by(reset_token=token).first()
    if not user:
        flash("重置链接无效或已过期。", "error")
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        use_default = request.form.get('use_default')
        
        if use_default:
            # 使用默认密码
            password = '123456'
        else:
            # 自定义密码
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            
            # 验证密码
            if len(password) < 6:
                flash("密码长度至少为6位。", "error")
                return render_template('reset_password.html', token=token)
            
            if password != confirm_password:
                flash("两次输入的密码不一致。", "error")
                return render_template('reset_password.html', token=token)
        
        # 更新密码
        user.password = generate_password_hash(password)
        user.reset_token = None  # 清除重置令牌
        db.session.commit()
        
        flash("密码已重置，请登录。", "success")
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', token=token)

# 配置数据库路径，使其在开发环境和打包环境都能正确工作
if getattr(sys, 'frozen', False):
    # 如果是打包环境（exe文件运行）
    application_path = os.path.dirname(sys.executable)
else:
    # 如果是开发环境（直接运行py文件）
    application_path = os.path.dirname(os.path.abspath(__file__))

# 确保instance目录存在
instance_path = os.path.join(application_path, 'instance')
if not os.path.exists(instance_path):
    os.makedirs(instance_path)

# 设置数据库路径
database_path = os.path.join(instance_path, 'campus.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'  # SQLite数据库
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True  # 启用调试模式
db = SQLAlchemy(app)

# ------------------------------
# 数据库模型定义
# ------------------------------
class User(db.Model):
    """用户表（管理员、学生、工作人员共用）"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # 加密存储
    role = db.Column(db.String(20), nullable=False)  # admin/student/staff
    name = db.Column(db.String(50), nullable=False)  # 真实姓名
    email = db.Column(db.String(100), unique=True, nullable=True)  # 邮箱字段，用于密码找回
    reset_token = db.Column(db.String(50), nullable=True)  # 重置密码令牌

class Student(db.Model):
    """学生详细信息表"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    student_id = db.Column(db.String(20), unique=True, nullable=False)  # 学号
    major = db.Column(db.String(50), nullable=False)  # 专业
    gender = db.Column(db.String(10), nullable=False)  # 性别
    dormitory_id = db.Column(db.Integer, db.ForeignKey('dormitory.id'), nullable=True)  # 宿舍
    bed_number = db.Column(db.String(10), nullable=True)  # 床位号
    phone = db.Column(db.String(20), nullable=True)  # 联系电话
    
    # 关系
    user = db.relationship('User', backref=db.backref('student', uselist=False), lazy=True)
    # 注意：dormitory关系已经在Dormitory模型中通过backref定义

class Staff(db.Model):
    """工作人员详细信息表"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    staff_id = db.Column(db.String(20), unique=True, nullable=False)  # 工号
    
    # 关系
    user = db.relationship('User', backref=db.backref('staff', uselist=False), lazy=True)

class Dormitory(db.Model):
    """宿舍信息表"""
    id = db.Column(db.Integer, primary_key=True)
    building = db.Column(db.String(20), nullable=False)  # 楼栋（如1号楼）
    number = db.Column(db.String(20), nullable=False)  # 宿舍号（如101）
    type = db.Column(db.String(20), nullable=False)  # 类型（4人间/6人间）
    capacity = db.Column(db.Integer, nullable=False)  # 容量
    status = db.Column(db.String(20), nullable=False, default='良好')  # 状态
    # 关联学生
    students = db.relationship('Student', backref='dormitory', lazy=True)

class Repair(db.Model):
    """维修申请表"""
    id = db.Column(db.Integer, primary_key=True)
    dormitory_id = db.Column(db.Integer, db.ForeignKey('dormitory.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 申请人
    description = db.Column(db.Text, nullable=False)  # 问题描述
    status = db.Column(db.String(20), nullable=False, default='待处理')  # 状态
    create_time = db.Column(db.DateTime, default=datetime.now)  # 申请时间
    handle_time = db.Column(db.DateTime, nullable=True)  # 处理时间
    handler_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=True)  # 处理人
    image_url = db.Column(db.String(200), nullable=True)  # 图片路径
    
    # 添加关系
    dormitory = db.relationship('Dormitory', backref='repairs', lazy=True)
    user = db.relationship('User', foreign_keys=[user_id], backref='repairs')

# ------------------------------
# 初始化数据库（首次运行创建）
# ------------------------------
with app.app_context():
    db.create_all()
    # 添加测试账号（若不存在）
    if not User.query.filter_by(username='admin').first():
        # 管理员：admin/admin123
        admin_pw = generate_password_hash('admin123', method='pbkdf2:sha256')
        admin = User(username='admin', password=admin_pw, role='admin', name='系统管理员')
        db.session.add(admin)
        
        # 学生：student/student123
        student_pw = generate_password_hash('student123', method='pbkdf2:sha256')
        student_user = User(username='student', password=student_pw, role='student', name='张三')
        db.session.add(student_user)
        db.session.flush()  # 刷新获取user_id
        # 学生详细信息
        student = Student(
            user_id=student_user.id,
            student_id='2024001',
            major='计算机科学与技术',
            gender='男',
            dormitory_id=1  # 后续可手动分配
        )
        db.session.add(student)
        
        # 工作人员：staff1/staff123
        staff_pw = generate_password_hash('staff123', method='pbkdf2:sha256')
        staff_user = User(username='staff1', password=staff_pw, role='staff', name='李师傅')
        db.session.add(staff_user)
        db.session.flush()
        # 工作人员详细信息
        staff = Staff(
            user_id=staff_user.id,
            staff_id='S2024001'
        )
        db.session.add(staff)
        
        # 测试宿舍
        dorm = Dormitory(building='1号楼', number='101', type='4人间', capacity=4, status='良好')
        db.session.add(dorm)
        
        db.session.commit()

# ------------------------------
# 权限装饰器
# ------------------------------
def login_required(f):
    """验证登录状态"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查用户是否已登录
        if 'user_id' not in session:
            flash('请先登录！', 'danger')
            return redirect(url_for('login'))
        # 用户已登录，继续执行原函数
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    """验证角色权限"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('请先登录！', 'danger')
                return redirect(url_for('login'))
            if session.get('role') != role:
                flash('权限不足！', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ------------------------------
# 路由功能实现
# ------------------------------
@app.route('/')
@login_required
def index():
    """首页（根据角色跳转）"""
    role = session.get('role')
    if role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif role == 'student':
        return redirect(url_for('student_profile'))
    elif role == 'staff':
        return redirect(url_for('staff_repairs'))
    else:
        # 如果角色未知，重定向到登录页面
        flash('用户角色信息异常，请重新登录。', 'danger')
        return redirect(url_for('logout'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录功能"""
    # 如果用户已经登录，直接跳转到首页
    if 'user_id' in session:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # 先尝试按用户名查找
        user = User.query.filter_by(username=username).first()
        
        # 如果用户名没找到，尝试按学号查找
        if not user:
            student = Student.query.filter_by(student_id=username).first()
            if student:
                user = User.query.filter_by(id=student.user_id).first()
        
        if user and check_password_hash(user.password, password):
            # 登录成功，保存session
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session['name'] = user.name
            flash('登录成功！', 'success')
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误！', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """注册功能"""
    if request.method == 'POST':
        try:
            username = request.form['username']
            name = request.form['name']
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            role = request.form['role']
            
            logger.debug(f"Registration attempt: username={username}, name={name}, role={role}")
            
            # 检查用户名是否已存在
            if User.query.filter_by(username=username).first():
                flash('用户名已存在，请选择其他用户名！', 'danger')
                return render_template('register.html')
            
            # 检查密码是否一致
            if password != confirm_password:
                flash('两次输入的密码不一致！', 'danger')
                return render_template('register.html')
            
            # 检查密码长度
            if len(password) < 6:
                flash('密码长度至少为6位！', 'danger')
                return render_template('register.html')
            
            # 检查角色是否合法（不允许注册管理员）
            if role not in ['student', 'staff']:
                flash('无效的用户角色！', 'danger')
                return render_template('register.html')
            
            # 创建新用户
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(
                username=username,
                password=hashed_password,
                role=role,
                name=name
            )
            
            db.session.add(new_user)
            db.session.flush()  # 获取新用户的ID
            logger.debug(f"User created with ID: {new_user.id}")
            
            # 根据角色创建相应的详细信息记录
            if role == 'student':
                # 创建学生记录
                student = Student(
                    user_id=new_user.id,
                    student_id=f'S{new_user.id:06d}',  # 自动生成学号
                    major='待定',
                    gender='待定'
                )
                
                # 如果提供了宿舍信息，则尝试绑定宿舍
                building = request.form.get('building', '').strip()
                dorm_number = request.form.get('dorm_number', '').strip()
                
                logger.debug(f"Dorm info provided: building={building}, dorm_number={dorm_number}")
                
                if building and dorm_number:
                    # 查找宿舍
                    dormitory = Dormitory.query.filter_by(building=building, number=dorm_number).first()
                    if dormitory:
                        student.dormitory_id = dormitory.id
                        logger.debug(f"Linked to existing dormitory ID: {dormitory.id}")
                    else:
                        # 如果宿舍不存在，创建新宿舍（设置合理默认值）
                        dormitory = Dormitory(
                            building=building.strip(),
                            number=dorm_number.strip(),
                            type='4人间',  # 默认类型
                            capacity=4,   # 默认容量
                            status='良好'
                        )
                        db.session.add(dormitory)
                        db.session.flush()
                        student.dormitory_id = dormitory.id
                        logger.debug(f"Created new dormitory with ID: {dormitory.id}, "
                                   f"building: {building}, number: {dorm_number}")
                        
                # 设置床位号和电话（去除首尾空格）
                bed_number = request.form.get('bed_number', '').strip()
                phone = request.form.get('phone', '').strip()
                student.bed_number = bed_number if bed_number else None
                student.phone = phone if phone else None
                logger.debug(f"Student additional info: bed_number={student.bed_number}, phone={student.phone}")
                
                db.session.add(student)
            elif role == 'staff':
                # 创建工作人员记录（默认值，后续可由管理员完善）
                staff = Staff(
                    user_id=new_user.id,
                    staff_id=f'E{new_user.id:06d}'  # 自动生成工号
                )
                db.session.add(staff)
                logger.debug(f"Staff record created for user ID: {new_user.id}")
            
            db.session.commit()
            flash('注册成功！请登录。', 'success')
            logger.debug("Registration successful")
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Registration failed: {str(e)}")
            flash(f'注册失败：{str(e)}', 'danger')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """退出登录（允许未登录状态访问）"""
    # 清理会话数据
    user_id = session.get('user_id')
    session.clear()
    
    # 记录登出日志（可选）
    if user_id:
        logger.debug(f"User logged out: {user_id}")
    
    flash('您已成功退出登录。', 'info')
    return redirect(url_for('login'))

# ------------------------------
# 管理员功能路由
# ------------------------------
@app.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    """管理员仪表盘（数据统计）"""
    # 统计数据
    dorm_count = Dormitory.query.count()
    student_count = Student.query.count()
    male_count = Student.query.filter_by(gender='男').count()
    female_count = Student.query.filter_by(gender='女').count()
    repair_total = Repair.query.count()
    repair_pending = Repair.query.filter_by(status='待处理').count()
    repair_processing = Repair.query.filter_by(status='处理中').count()
    repair_completed = Repair.query.filter_by(status='已完成').count()
    
    from datetime import datetime
    return render_template('admin/dashboard.html',
                           dorm_count=dorm_count,
                           student_count=student_count,
                           male_count=male_count,
                           female_count=female_count,
                           repair_total=repair_total,
                           repair_pending=repair_pending,
                           repair_processing=repair_processing,
                           repair_completed=repair_completed,
                           now=datetime.now())

@app.route('/admin/dormitories')
@login_required
@role_required('admin')
def admin_dormitories():
    """宿舍管理（查看/添加/删除）"""
    dormitories = Dormitory.query.options(db.joinedload(Dormitory.students)).all()
    return render_template('admin/dormitories.html', dormitories=dormitories)

@app.route('/admin/dormitory/add', methods=['POST'])
@login_required
@role_required('admin')
def add_dormitory():
    """添加宿舍"""
    building = request.form['building']
    number = request.form['number']
    type_ = request.form['type']
    capacity = int(request.form['capacity'])
    status = request.form['status']
    
    # 验证容量是否符合宿舍类型标准
    type_capacity_map = {
        '4人间': 4,
        '6人间': 6,
        '8人间': 8
    }
    
    max_capacity = type_capacity_map.get(type_, 8)
    
    if capacity > max_capacity:
        flash(f'容量不能超过{type_}的标准容量({max_capacity}人)', 'error')
        return redirect(url_for('admin_dormitories'))
    
    if capacity < 1:
        flash('容量必须大于0', 'error')
        return redirect(url_for('admin_dormitories'))
    
    new_dorm = Dormitory(
        building=building,
        number=number,
        type=type_,
        capacity=capacity,
        status=status
    )
    db.session.add(new_dorm)
    db.session.commit()
    flash('宿舍添加成功！', 'success')
    return redirect(url_for('admin_dormitories'))

@app.route('/admin/dormitory/edit/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def edit_dormitory(id):
    """编辑宿舍信息"""
    dorm = Dormitory.query.get_or_404(id)
    
    # 获取表单数据
    building = request.form['building'].strip()
    number = request.form['number'].strip()
    type_ = request.form['type']
    capacity = int(request.form['capacity'])
    status = request.form['status']
    
    # 检查宿舍是否已存在（除了当前宿舍）
    existing_dorm = Dormitory.query.filter(
        Dormitory.building == building,
        Dormitory.number == number,
        Dormitory.id != id
    ).first()
    
    if existing_dorm:
        flash('该宿舍已存在！', 'danger')
        return redirect(url_for('admin_dormitories'))
    
    # 检查是否有学生居住该宿舍
    if dorm.students:
        # 如果有学生居住，不允许更改楼栋和房间号
        if dorm.building != building or dorm.number != number:
            flash('该宿舍已有学生居住，无法修改楼栋和房间号！', 'danger')
            return redirect(url_for('admin_dormitories'))
    
    # 更新宿舍信息
    dorm.building = building
    dorm.number = number
    dorm.type = type_
    dorm.capacity = capacity
    dorm.status = status
    
    db.session.commit()
    flash('宿舍信息更新成功！', 'success')
    return redirect(url_for('admin_dormitories'))

@app.route('/admin/dormitory/delete/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def delete_dormitory(id):
    dorm = Dormitory.query.get_or_404(id)
    if dorm.students:
        flash('该宿舍仍有学生居住，无法删除！', 'danger')
        return redirect(url_for('admin_dormitories'))
    db.session.delete(dorm)
    db.session.commit()
    flash('宿舍删除成功！', 'success')
    return redirect(url_for('admin_dormitories'))

@app.route('/admin/students')
@login_required
@role_required('admin')
def admin_students():
    """学生管理（查看/添加/删除）"""
    students = Student.query.join(User).join(Dormitory, isouter=True).all()
    dormitories = Dormitory.query.all()
    return render_template('admin/students.html', students=students, dormitories=dormitories)

@app.route('/admin/student/add', methods=['POST'])
@login_required
@role_required('admin')
def add_student():
    """添加学生（同时创建用户）"""
    name = request.form['name']
    username = request.form['name']  # 使用姓名作为用户名
    major = request.form['major']
    gender = request.form['gender']
    dormitory_id = request.form['dormitory_id'] if request.form['dormitory_id'] else None
    password = '123456'  # 默认密码
    
    # 生成随机学号 (STU + 8位数字)
    import random
    student_id = 'STU' + str(random.randint(10000000, 99999999))
    
    # 检查用户名是否已存在，如果存在则添加数字后缀
    original_username = username
    suffix = 1
    while User.query.filter_by(username=username).first():
        username = original_username + str(suffix)
        suffix += 1
    
    # 检查学号是否已存在，如果存在则重新生成
    while Student.query.filter_by(student_id=student_id).first():
        student_id = 'STU' + str(random.randint(10000000, 99999999))
    
    # 创建用户
    hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
    user = User(username=username, password=hashed_pw, role='student', name=name)
    db.session.add(user)
    db.session.flush()
    
    # 创建学生信息
    student = Student(
        user_id=user.id,
        student_id=student_id,
        major=major,
        gender=gender,
        dormitory_id=dormitory_id if dormitory_id else None
    )
    db.session.add(student)
    db.session.commit()
    flash(f'学生添加成功！默认密码：{password}，学号：{student_id}', 'success')
    return redirect(url_for('admin_students'))

@app.route('/admin/student/edit/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def edit_student(id):
    """编辑学生信息"""
    student = Student.query.get_or_404(id)
    user = User.query.get_or_404(student.user_id)
    
    # 获取表单数据
    name = request.form['name'].strip()
    student_id = request.form['student_id'].strip()
    major = request.form['major'].strip()
    gender = request.form['gender']
    dormitory_id = request.form['dormitory_id'] if request.form['dormitory_id'] else None
    
    # 检查学号是否已存在（除了当前学生）
    existing_student = Student.query.filter(
        Student.student_id == student_id,
        Student.id != id
    ).first()
    
    if existing_student:
        flash('学号已存在！', 'danger')
        return redirect(url_for('admin_students'))
    
    # 更新学生和用户信息
    user.name = name
    student.student_id = student_id
    student.major = major
    student.gender = gender
    student.dormitory_id = dormitory_id
    
    db.session.commit()
    flash('学生信息更新成功！', 'success')
    return redirect(url_for('admin_students'))

@app.route('/admin/student/delete/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def delete_student(id):
    """删除学生（同时删除用户）"""
    student = Student.query.get_or_404(id)
    user = User.query.get(student.user_id)
    db.session.delete(student)
    db.session.delete(user)
    db.session.commit()
    flash('学生信息删除成功！', 'success')
    return redirect(url_for('admin_students'))

@app.route('/admin/repairs')
@login_required
@role_required('admin')
def admin_repairs():
    """维修申请管理（管理员视角）"""
    status = request.args.get('status', 'all')
    
    # 统计信息
    repair_total = Repair.query.count()
    repair_pending = Repair.query.filter_by(status='待处理').count()
    repair_processing = Repair.query.filter_by(status='处理中').count()
    repair_completed = Repair.query.filter_by(status='已完成').count()
    
    if status == 'all':
        repairs = Repair.query.join(User).join(Dormitory).all()
    else:
        repairs = Repair.query.filter_by(status=status).join(User).join(Dormitory).all()
    return render_template('admin/repairs.html', 
                          repairs=repairs, 
                          current_status=status,
                          repair_total=repair_total,
                          repair_pending=repair_pending,
                          repair_processing=repair_processing,
                          repair_completed=repair_completed)

@app.route('/admin/repair/<int:repair_id>')
@login_required
@role_required('admin')
def admin_repair_detail(repair_id):
    """维修申请详情（管理员视角）"""
    repair = Repair.query.join(User).join(Dormitory).filter(Repair.id == repair_id).first_or_404()
    return render_template('admin/repair_detail.html', repair=repair)

# ------------------------------
# 学生功能路由
# ------------------------------
@app.route('/student/profile')
@login_required
@role_required('student')
def student_profile():
    """学生个人信息"""
    student = Student.query.filter_by(user_id=session['user_id']).first()
    if student is None:
        # 如果找不到学生记录，显示错误信息并重定向到首页
        flash('未找到学生信息，请联系管理员。', 'danger')
        return redirect(url_for('index'))
    
    dormitory = Dormitory.query.get(student.dormitory_id) if student.dormitory_id else None
    return render_template('student/profile.html', student=student, dormitory=dormitory)

@app.route('/student/profile/update', methods=['POST'])
@login_required
@role_required('student')
def update_student_info():
    """更新学生个人信息"""
    student = Student.query.filter_by(user_id=session['user_id']).first()
    if student is None:
        flash('学生信息不存在，请联系管理员。', 'danger')
        return redirect(url_for('student_profile'))
    
    # 更新基本信息
    student.major = request.form.get('major', student.major)
    student.gender = request.form.get('gender', student.gender)
    
    # 更新床位号和电话
    student.bed_number = request.form.get('bed_number', student.bed_number) or None
    student.phone = request.form.get('phone', student.phone) or None
    
    # 处理宿舍绑定
    building = request.form.get('building', '').strip()
    dorm_number = request.form.get('dorm_number', '').strip()
    
    if building and dorm_number:
        # 查找宿舍
        dormitory = Dormitory.query.filter_by(building=building, number=dorm_number).first()
        if dormitory:
            student.dormitory_id = dormitory.id
        else:
            # 如果宿舍不存在，创建新宿舍
            dormitory = Dormitory(
                building=building,
                number=dorm_number,
                type='未指定',
                capacity=0,
                status='良好'
            )
            db.session.add(dormitory)
            db.session.flush()
            student.dormitory_id = dormitory.id
    
    db.session.commit()
    flash('个人信息更新成功！', 'success')
    return redirect(url_for('student_profile'))

@app.route('/student/repairs')
@login_required
@role_required('student')
def student_repairs():
    """维修申请记录（学生视角）"""
    student = Student.query.filter_by(user_id=session['user_id']).first()
    repairs = Repair.query.filter_by(user_id=session['user_id'])\
                         .join(Dormitory)\
                         .order_by(Repair.create_time.desc()).all()
    return render_template('student/repairs.html', repairs=repairs, student=student)

@app.route('/student/repair_apply')
@login_required
@role_required('student')
def repair_apply():
    """提交维修申请页面"""
    return render_template('student/repair_apply.html')

@app.route('/student/repair/submit', methods=['POST'])
@login_required
@role_required('student')
def submit_repair():
    """提交维修申请"""
    # 获取表单数据
    building = request.form.get('building', '')
    dorm_number = request.form.get('dorm_number', '')
    applicant_name = request.form.get('applicant_name', '')
    bed_number = request.form.get('bed_number', '')
    phone = request.form.get('phone', '')
    description = request.form.get('description', '')
    
    # 验证必填字段
    if not all([building, dorm_number, applicant_name, description]):
        flash('请填写所有必填字段！', 'danger')
        return redirect(url_for('student_repairs'))
    
    # 构造详细的维修描述
    detailed_description = f"宿舍：{building}-{dorm_number}\n"
    detailed_description += f"申请人：{applicant_name}\n"
    detailed_description += f"联系电话：{phone or '未填写'}\n"
    detailed_description += f"床位号：{bed_number or '未填写'}\n"
    detailed_description += f"问题描述：{description}"
    
    # 处理文件上传
    image_url = None
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename != '':
            # 确保上传目录存在
            upload_folder = os.path.join(app.root_path, 'static', 'uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            # 保存文件
            from werkzeug.utils import secure_filename
            filename = secure_filename(file.filename)
            if filename != '':
                filepath = os.path.join(upload_folder, filename)
                file.save(filepath)
                image_url = f"uploads/{filename}"
    
    # 查找或创建宿舍记录
    dormitory = Dormitory.query.filter_by(building=building, number=dorm_number).first()
    if not dormitory:
        # 如果宿舍不存在，创建一个新的宿舍记录
        dormitory = Dormitory(
            building=building,
            number=dorm_number,
            type='未指定',
            capacity=0,
            status='良好'
        )
        db.session.add(dormitory)
        db.session.flush()  # 获取新创建宿舍的ID
    
    # 创建维修申请
    new_repair = Repair(
        dormitory_id=dormitory.id,
        user_id=session['user_id'],
        description=detailed_description,
        image_url=image_url
    )
    db.session.add(new_repair)
    db.session.commit()
    flash('维修申请提交成功！', 'success')
    return redirect(url_for('student_repairs'))

@app.route('/student/repair/cancel/<int:repair_id>', methods=['POST'])
@login_required
@role_required('student')
def cancel_repair(repair_id):
    """撤销维修申请"""
    # 获取要撤销的维修申请
    repair = Repair.query.filter_by(id=repair_id, user_id=session['user_id']).first_or_404()
    
    # 只有待处理状态的申请可以撤销
    if repair.status != '待处理':
        flash('只能撤销待处理状态的申请！', 'danger')
        return redirect(url_for('student_repairs'))
    
    # 删除维修申请
    db.session.delete(repair)
    db.session.commit()
    
    flash('维修申请已成功撤销！', 'success')
    return redirect(url_for('student_repairs'))

# ------------------------------
# 工作人员功能路由
# ------------------------------
@app.route('/staff/repairs')
@login_required
@role_required('staff')
def staff_repairs():
    """维修处理（工作人员视角）"""
    # 获取状态参数，如果没有提供则默认为"待处理"
    status = request.args.get('status', '待处理')
    staff = Staff.query.filter_by(user_id=session['user_id']).first()
    
    if not staff:
        flash('工作人员信息不存在，请联系管理员。', 'danger')
        return redirect(url_for('index'))
    
    # 打印调试信息
    print(f"请求的状态参数: {status}")
    
    # 查询维修申请，确保正确连接相关表
    query = Repair.query.join(User).join(Dormitory)
    
    # 只有在status不是'all'时才过滤状态
    if status != 'all':
        query = query.filter(Repair.status == status)
    
    repairs = query.order_by(Repair.create_time.desc()).all()
    print(f"查询到的维修申请数量: {len(repairs)}")
    
    return render_template('staff/repairs.html', repairs=repairs, current_status=status, staff=staff)

@app.route('/staff/repair/<int:repair_id>')
@login_required
@role_required('staff')
def staff_repair_detail(repair_id):
    """维修申请详情（工作人员视角）"""
    repair = Repair.query.join(User).join(Dormitory).filter(Repair.id == repair_id).first_or_404()
    staff = Staff.query.filter_by(user_id=session['user_id']).first()
    if not staff:
        flash('工作人员信息不存在，请联系管理员。', 'danger')
        return redirect(url_for('index'))
    return render_template('staff/repair_detail.html', repair=repair, staff=staff)

@app.route('/staff/repair/handle/<int:id>', methods=['POST'])
@login_required
@role_required('staff')
def handle_repair(id):
    """处理维修申请（更新状态）"""
    repair = Repair.query.get_or_404(id)
    action = request.form.get('action')
    
    staff = Staff.query.filter_by(user_id=session['user_id']).first()
    if not staff:
        flash('工作人员信息不存在，请联系管理员。', 'danger')
        return redirect(url_for('staff_repairs'))
    
    current_time = datetime.now()
    
    if action == 'accept':
        repair.status = '处理中'
        repair.handler_id = staff.id
        repair.handle_time = current_time
        flash('已接受维修申请，开始处理。', 'success')
    elif action == 'complete':
        repair.status = '已完成'
        repair.handler_id = staff.id  # 确保处理人被设置
        repair.handle_time = current_time
        flash('维修申请处理完成。', 'success')
    else:
        flash('无效的操作。', 'danger')
        return redirect(url_for('staff_repairs'))
    
    db.session.commit()
    return redirect(url_for('staff_repairs'))

if __name__ == '__main__':
    app.run(debug=True)