from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response
from datetime import timedelta
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, JWTManager
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
# 增加資料庫連線重試機制
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
import os
from datetime import datetime, timedelta
import time
from functools import wraps

app = Flask(__name__)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Add JWT configuration after Flask initialization
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')

app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
jwt = JWTManager(app)



# 從環境變數獲取資料庫連線資訊，如果沒有則使用預設值
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'mysql')
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')  # k8s service name
DB_NAME = os.getenv('DB_NAME','flask_book_app')
#DB_NAME = os.getenv('DB_NAME', 'mydb')

# 設定資料庫連線 URI
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'secret_key')


import time

def wait_for_db(app, max_retries=5, retry_interval=5):
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            engine.connect()
            print("成功連接到資料庫！")
            return True
        except OperationalError as e:
            retry_count += 1
            print(f"無法連接到資料庫 (嘗試 {retry_count}/{max_retries}): {str(e)}")
            if retry_count < max_retries:
                print(f"等待 {retry_interval} 秒後重試...")
                time.sleep(retry_interval)
    
    print("無法連接到資料庫，已達到最大重試次數")
    return False

# 初始化資料庫
db = SQLAlchemy(app)

# 定義 Book 模型，代表圖書資料表
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    published_date = db.Column(db.String(20))
    is_borrowed = db.Column(db.Boolean, default=False)
    image_url = db.Column(db.String(500))  # New column for storing image file location

    


# 借書記錄模型
class BorrowRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    borrower_name = db.Column(db.String(100), nullable=False)
    borrow_date = db.Column(db.DateTime, default=datetime.utcnow)
    return_date = db.Column(db.DateTime, nullable=True)  # 只有歸還時才會更新

    book = db.relationship('Book', backref=db.backref('borrow_records', lazy=True))

    def __repr__(self):
        return f"<BorrowRecord {self.borrower_name} - {self.book.title}>"

# 用戶模型
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    login_attempts = db.Column(db.Integer, default=0)  # 新增：記錄登入嘗試次數
    locked_until = db.Column(db.DateTime)  # 新增：帳號鎖定時間

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        print(f"Password hash created: {self.password_hash}")  # 偵錯用

    def check_password(self, password):
        if not self.password_hash:
            print("No password hash found")  # 偵錯用
            return False
        result = bcrypt.check_password_hash(self.password_hash, password)
        print(f"Password check result: {result}")  # 偵錯用
        return result

    def increment_login_attempts(self):
        self.login_attempts += 1
        if self.login_attempts >= 5:  # 5次錯誤就鎖定帳號
            self.locked_until = datetime.utcnow() + timedelta(minutes=15)  # 鎖定15分鐘
        db.session.commit()

    def reset_login_attempts(self):
        self.login_attempts = 0
        self.locked_until = None
        db.session.commit()

    def is_locked(self):
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        if self.locked_until and self.locked_until <= datetime.utcnow():
            self.reset_login_attempts()  # 如果鎖定時間已過，重置計數
            return False
        return False

# 修改這個部分：將註解的裝飾器改為啟用狀態
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 註冊路由
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 檢查用戶名是否已存在
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({
                'success': False,
                'message': 'Username already exists, please choose another one'
            })
            
        # 建立新用戶
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Registration successful! Please login',
            'redirect': url_for('login')
        })
        
    return render_template('register.html')

# 當第一次請求時建立資料庫與資料表（若尚未建立）
#@app.before_first_request
#def create_tables():
#    db.create_all()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(f"Login attempt for username: {username}")  # 偵錯用

        user = User.query.filter_by(username=username).first()
        
        # 檢查用戶是否存在
        if not user:
            flash('Username does not exist')
            return redirect(url_for('login'))

        # 檢查帳號是否被鎖定
        if user.is_locked():
            remaining_time = (user.locked_until - datetime.utcnow()).seconds // 60
            flash(f'Account is locked. Please try again in {remaining_time} minutes')
            return redirect(url_for('login'))

        # 驗證密碼
        if user.check_password(password):
            print("Password check succeeded")  # 偵錯用
            user.reset_login_attempts()  # 登入成功，重置錯誤計數
            # 確保 user.id 是字串類型
            access_token = create_access_token(identity=str(user.id))
            login_user(user)
            response = make_response(redirect(url_for('index')))
            response.set_cookie(
                'access_token',
                access_token,
                httponly=True,
                secure=False,  # 修改這裡，在開發環境中設為 False
                samesite='Lax',
                max_age=86400
            )
            flash('Login successful!')
            return response
        else:
            print(f"Password check failed for user: {username}")  # 偵錯用
            user.increment_login_attempts()
            attempts_left = 5 - user.login_attempts
            if attempts_left > 0:
                flash(f'Incorrect password. {attempts_left} attempts remaining')
            else:
                flash('Too many failed attempts. Account locked for 15 minutes')
            return redirect(url_for('login'))

    return render_template('login.html')

# 新增一個 before_request 處理器來自動處理 JWT
@app.before_request
def handle_jwt():
    if 'access_token' in request.cookies:
        token = request.cookies.get('access_token')
        if 'Authorization' not in request.headers:
            # 創建一個新的不可變字典
            headers = dict(request.headers)
            headers['Authorization'] = f'Bearer {token}'
            # 更新 request 的 environ
            request.environ['HTTP_AUTHORIZATION'] = f'Bearer {token}'

# Add a protected route example
@app.route('/api/protected')
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return jsonify({
        'message': f'Hello {user.username}! This is a protected route.',
        'user_id': current_user_id
    })

# Protect your existing routes with JWT
@app.route('/borrow_system')
@jwt_required()
def borrow_system():
    books = Book.query.all()
    records = BorrowRecord.query.filter_by(return_date=None).all()
    return render_template('borrow.html', books=books, records=records)

@app.route('/manage_books')
@jwt_required()
def manage_books():
    books = Book.query.all()
    return render_template('manage_books.html', books=books)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout successful!")
    return redirect(url_for('index'))
    
# 首頁：顯示所有圖書
@app.route('/')
def index():
    books = Book.query.all()  # 取得所有圖書資料
    return render_template('index.html', books=books)




# 新增圖書
@app.route('/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        published_date = request.form.get('published_date')
        # 簡單驗證必填欄位
        if not title or not author:
            flash("Title and author are required fields!")
            return redirect(url_for('add_book'))
        # 建立新圖書資料
        new_book = Book(title=title, author=author, published_date=published_date)
        db.session.add(new_book)
        db.session.commit()
        flash("Book added successfully!")
        return redirect(url_for('index'))
    return render_template('add_book.html')

# 編輯圖書資料
@app.route('/edit/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    if request.method == 'POST':  # 移除多餘的右括號
        book.title = request.form.get('title')
        book.author = request.form.get('author')
        book.published_date = request.form.get('published_date')
        db.session.commit()
        flash("Book information updated successfully!")
        return redirect(url_for('index'))
    return render_template('edit_book.html', book=book)

# 刪除圖書
@app.route('/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash("Book deleted successfully!")
    return redirect(url_for('index'))

# ------------------- 借閱管理 -------------------
#borrow API
@app.route('/borrow/<int:book_id>', methods=['POST'])
def borrow_book(book_id):
    book = Book.query.get_or_404(book_id)
    if book.is_borrowed:
        flash("This book is already borrowed!")
        return redirect(url_for('index'))

    borrower_name = request.form.get('borrower_name')
    if not borrower_name:
        flash("Please enter borrower's name!")
        return redirect(url_for('index'))

    book.is_borrowed = True
    borrow_record = BorrowRecord(book_id=book.id, borrower_name=borrower_name)
    db.session.add(borrow_record)
    db.session.commit()
    
    flash(f"'{book.title}' has been borrowed by {borrower_name}!")
    return redirect(url_for('index'))

#return API
@app.route('/return/<int:book_id>', methods=['POST'])
def return_book(book_id):
    book = Book.query.get_or_404(book_id)
    if not book.is_borrowed:
        flash("This book hasn't been borrowed!")
        return redirect(url_for('index'))

    # 找到該書最近的借閱紀錄（未歸還的）
    borrow_record = BorrowRecord.query.filter_by(book_id=book.id, return_date=None).first()
    if borrow_record:
        borrow_record.return_date = datetime.utcnow()
    
    book.is_borrowed = False
    db.session.commit()

    flash(f"'{book.title}' has been returned successfully!")
    return redirect(url_for('index'))






if __name__ == '__main__':
    with app.app_context():
        if wait_for_db(app):
            db.create_all()
            # 預設 10 本中文書籍
            default_books_cn = [
            {"title": "Python 程式設計", "author": "張三", "published_date": "2020-01-15"},
                {"title": "Flask Web 開發", "author": "李四", "published_date": "2019-05-23"},
                {"title": "機器學習入門", "author": "王五", "published_date": "2021-07-01"},
                {"title": "數據科學基礎", "author": "陳六", "published_date": "2018-11-30"},
                {"title": "深度學習應用", "author": "何七", "published_date": "2022-03-18"},
                {"title": "資料庫設計", "author": "趙八", "published_date": "2017-09-12"},
                {"title": "演算法導論", "author": "孫九", "published_date": "2020-08-22"},
                {"title": "雲端運算基礎", "author": "周十", "published_date": "2019-04-05"},
                {"title": "區塊鏈技術", "author": "呂十一", "published_date": "2021-06-10"},
                {"title": "人工智慧概論", "author": "高十二", "published_date": "2023-01-01"}
            ]

            # 預設 10 本英文書籍
            default_books_en = [
                {"title": "Python Programming", "author": "John Doe", "published_date": "2020-01-15"},
                {"title": "Flask Web Development", "author": "Michael Grinberg", "published_date": "2019-05-23"},
                {"title": "Machine Learning for Beginners", "author": "Andrew Ng", "published_date": "2021-07-01"},
                {"title": "Data Science Essentials", "author": "Jake VanderPlas", "published_date": "2018-11-30"},
                {"title": "Deep Learning Applications", "author": "Ian Goodfellow", "published_date": "2022-03-18"},
                {"title": "Database Design Fundamentals", "author": "Elmasri & Navathe", "published_date": "2017-09-12"},
                {"title": "Introduction to Algorithms", "author": "Thomas H. Cormen", "published_date": "2020-08-22"},
                {"title": "Cloud Computing Basics", "author": "Rajkumar Buyya", "published_date": "2019-04-05"},
                {"title": "Blockchain Technology Explained", "author": "Don Tapscott", "published_date": "2021-06-10"},
                {"title": "Artificial Intelligence A Modern Approach", "author": "Stuart Russell", "published_date": "2023-01-01"}
            ]

            # 檢查資料庫是否已有書籍，若無則插入 20 本預設書籍
            if Book.query.count() == 0:
                for book in default_books_en + default_books_cn:
                    new_book = Book(
                        title=book["title"], 
                        author=book["author"], 
                        published_date=book["published_date"],
                        image_url=f"./static/images/{book['title']}.jpg"  # 直接使用標題生成圖片路徑
                    )
                    db.session.add(new_book)
                    db.session.commit()
                print("已初始化 20 本書籍（10 本中文 + 10 本英文）至資料庫！")
            else:
                print("資料庫已有書籍，跳過初始化。")
            

            def __repr__(self):
                return f"<Book {self.title}>"
            app.run(host='0.0.0.0', debug=True, port=5010)
        else:
            print("應用程式啟動失敗：無法連接到資料庫")
