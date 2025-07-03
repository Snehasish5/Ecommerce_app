# Ecommerce_app

**🛍️ ShopEase – Flask eCommerce Web App:**


ShopEase is a modern eCommerce platform built with Python Flask, MySQL, HTML, CSS, and JavaScript. It features user authentication, a shopping cart, Razorpay payments and more.


**🚀 Features**

✅ User Registration & Login (with email & phone)

🛒 Product Browsing with Search

📦 Product Details Page (with stock alert logic)

💼 Add to Cart, Quantity Management

💳 Razorpay Payment Integration

📜 Order History with Paid & Failed Orders

🖼️ Product Images with Discount Tag Display

📧 Flash Messages (Success, Error, Alerts)

🔐 Session-based Security

📱 Responsive Layout using Bootstrap 5

📍 Footer with Company Info

⬆️ "Back to Top" Button



**🛠️ Technologies Used**

**Backend** : *Python Flask, MySQL*

**Frontend** : *HTML5, CSS3, Bootstrap 5, JavaScript*

**Payment** : *Razorpay Payment Gateway*

**Database** : *MySQL (with mysql-connector-python)*

**Session** : *Flask Session Management*



**📂 Folder Structure**

ShopEase/
│
├── app.py
├── config.py
├── models.py
├── requirements.txt
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── product.html
│   ├── cart.html
│   ├── checkout.html
│   ├── login.html
│   ├── register.html
│   ├── profile.html
│   ├── order_history.html
│   └── ...
└── README.md


**🔧 Installation & Setup**


*Clone the Repository:*

--git clone https://github.com/yourusername/shopease.git


--cd shopease


*Install Python Dependencies:*


--pip install -r requirements.txt



*Set up the MySQL Database:*


--CREATE DATABASE ecommerce;


*Import schema and sample data if available:*



--mysql -u root -p ecommerce < schema.sql


*Configure Database in config.py:*



DB_CONFIG = {
    
    'host': 'localhost',
    
    'user': 'root',
    
    'password': 'yourpassword',
    
    'database': 'ecommerce'
}


*Set Up Razorpay:*


--razorpay_key = 'rzp_test_XXXXXX'


--razorpay_secret = 'your_secret'


*Run the App:*

--python app.py


**App will run at: http://127.0.0.1:5000**

**📃 License**


--This project is licensed under the MIT License. Feel free to use, modify, and share.
