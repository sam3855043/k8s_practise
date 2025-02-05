from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# 建立 Flask 應用實例
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'  # 資料庫檔案：books.db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret_key'  # 用於 flash 訊息

# 初始化 SQLAlchemy
db = SQLAlchemy(app)

# 定義 Book 模型，代表圖書資料表
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 自動產生的主鍵
    title = db.Column(db.String(200), nullable=False)  # 圖書標題
    author = db.Column(db.String(100), nullable=False)  # 作者
    published_date = db.Column(db.String(20))  # 出版日期
    is_borrowed = db.Column(db.Boolean, default=False)  # 新增是否被借出的欄位
    


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

# 當第一次請求時建立資料庫與資料表（若尚未建立）
#@app.before_first_request
#def create_tables():
#    db.create_all()

# 首頁：顯示所有圖書
@app.route('/')
def index():
    books = Book.query.all()  # 取得所有圖書資料
    return render_template('index.html', books=books)


@app.route('/borrow_system')
def borrow_system():
    books = Book.query.all()
    records = BorrowRecord.query.filter_by(return_date=None).all()
    return render_template('borrow.html', books=books, records=records)

@app.route('/manage_books')
def manage_books():
    books = Book.query.all()
    return render_template('manage_books.html', books=books)

# 新增圖書
@app.route('/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        published_date = request.form.get('published_date')
        # 簡單驗證必填欄位
        if not title or not author:
            flash("標題與作者為必填欄位！")
            return redirect(url_for('add_book'))
        # 建立新圖書資料
        new_book = Book(title=title, author=author, published_date=published_date)
        db.session.add(new_book)
        db.session.commit()
        flash("新增圖書成功！")
        return redirect(url_for('index'))
    return render_template('add_book.html')

# 編輯圖書資料
@app.route('/edit/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    if request.method == 'POST':
        book.title = request.form.get('title')
        book.author = request.form.get('author')
        book.published_date = request.form.get('published_date')
        db.session.commit()
        flash("更新圖書資訊成功！")
        return redirect(url_for('index'))
    return render_template('edit_book.html', book=book)

# 刪除圖書
@app.route('/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash("刪除圖書成功！")
    return redirect(url_for('index'))

# ------------------- 借閱管理 -------------------
#borrow API
@app.route('/borrow/<int:book_id>', methods=['POST'])
def borrow_book(book_id):
    book = Book.query.get_or_404(book_id)
    if book.is_borrowed:
        flash("此書已被借出，無法借閱！")
        return redirect(url_for('index'))

    borrower_name = request.form.get('borrower_name')
    if not borrower_name:
        flash("請輸入借閱者姓名！")
        return redirect(url_for('index'))

    book.is_borrowed = True
    borrow_record = BorrowRecord(book_id=book.id, borrower_name=borrower_name)
    db.session.add(borrow_record)
    db.session.commit()
    
    flash(f"《{book.title}》已成功借出給 {borrower_name}！")
    return redirect(url_for('index'))

#return API
@app.route('/return/<int:book_id>', methods=['POST'])
def return_book(book_id):
    book = Book.query.get_or_404(book_id)
    if not book.is_borrowed:
        flash("此書尚未被借出！")
        return redirect(url_for('index'))

    # 找到該書最近的借閱紀錄（未歸還的）
    borrow_record = BorrowRecord.query.filter_by(book_id=book.id, return_date=None).first()
    if borrow_record:
        borrow_record.return_date = datetime.utcnow()
    
    book.is_borrowed = False
    db.session.commit()

    flash(f"《{book.title}》已成功歸還！")
    return redirect(url_for('index'))






if __name__ == '__main__':
    with app.app_context():
        db.create_all();
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
            {"title": "Artificial Intelligence: A Modern Approach", "author": "Stuart Russell", "published_date": "2023-01-01"}
        ]

        # 檢查資料庫是否已有書籍，若無則插入 20 本預設書籍
        if Book.query.count() == 0:
            for book in default_books_cn + default_books_en:
                new_book = Book(title=book["title"], author=book["author"], published_date=book["published_date"])
                db.session.add(new_book)
                db.session.commit()
                print("已初始化 20 本書籍（10 本中文 + 10 本英文）至資料庫！")
        else:
            print("資料庫已有書籍，跳過初始化。")
            # 檢查資料庫是否已有書籍，若無則插入 10 本預設書籍
        

        def __repr__(self):
            return f"<Book {self.title}>"
    app.run(host='0.0.0.0',debug=True, port=5020)
