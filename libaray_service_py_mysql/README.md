# Library Management System

A Flask-based library management system with user authentication and book borrowing functionality.

([/libaray_service_py_mysql/screenshots/hompage.png](https://github.com/sam3855043/k8s_practise/blob/main/libaray_service_py_mysql/screenshots/hompage.png))
![1](/libaray_service_py_mysql/screenshots/hompage.png)


## Features

- User Authentication (Login/Register)
- JWT-based Authorization
- Book Management (Add/Edit/Delete)
- Book Borrowing System
- Account Security Features
  - Failed Login Attempt Tracking
  - Account Lockout Protection
  - Secure Password Hashing

## Tech Stack

- **Backend**: Python Flask
- **Database**: MySQL
- **Authentication**: JWT + Flask-Login
- **Frontend**: Bootstrap 5
- **Security**: Bcrypt
- **Container**: Docker/Kubernetes ready

## Project Structure
```
project_root/
├── screenshots/
│   ├── login.png
│   ├── books.png
│   └── borrow.png
├── app.py # Main application file ├── templates/
│ ├── login.html # Login page
│ ├── register.html # Registration page 
│ ├── index.html # Home page 
│ ├── borrow.html # Borrowing system 
│ └── add_book.html # Add book form 
├── static/ 
│ └── images/ # Book cover images 
└── README.md
```
## Setup Instructions

1. Clone the repository
```bash
git clone <repository-url>
```
2.Set up virtual environment
```python -m venv .venv
source .venv/bin/activate  # For Unix
.venv\Scripts\activate     # For Windows 
```

3.Install dependencies
```
pip install -r requirements.txt
```
4.Configure environment variables
```export DB_USER=your_db_user
export DB_PASSWORD=your_db_password
export DB_HOST=your_db_host
export DB_NAME=flask_book_app
export JWT_SECRET_KEY=your_jwt_secret
export SECRET_KEY=your_app_secret
```
5. Initialize database
``` 
   flask db upgrade
```
6.Run the application
```
python app.py
```
API Endpoints
* /register - User registration
* /login - User login
* /logout - User logout
* /borrow_system - Book borrowing management
* /add - Add new book
* /edit/<book_id> - Edit book details
* /delete/<book_id> - Delete book
* /borrow/<book_id> - Borrow a book
* /return/<book_id> - Return a book


## Security Features
* Password hashing using Bcrypt
* JWT authentication
* Account lockout after 5 failed login attempts
 15-minute lockout duration
* Secure cookie handling
* CSRF protection
# Docker Support
Build the image:
```docker build -t library-system .
```

# Contributing
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

# License
MIT License

# Author
Samuel-chuang


#Acknowledgments
Flask framework
Bootstrap team
MySQL team