# Ecom
# Ecom
# 🛒 E-Commerce System (Python + MySQL)

A console-based E-Commerce application built using Python and MySQL, demonstrating core software engineering concepts including OOP, database integration, exception handling, validation, and modular architecture.

## 📌 Features

### 🧑 Customers
- Create new customers (with email and password validation)
- View all registered customers
- Update email and password (with credential check)
- Delete customers securely

### 📦 Products
- Add new products
- View all products
- Update product details (price, stock)
- Delete products
- View frequently ordered / not ordered / out of stock products

### 🛒 Cart
- Add product to cart (check stock before adding)
- View cart (in table format with product info)
- Update cart (increase/decrease quantity)
- Remove from cart (stock updated accordingly)

### 📦 Orders
- Place orders from cart
- View order history (by customer, product, date, price, etc.)
- Change shipping address
- Delete/cancel orders

### 📊 Reports
- Customers by product ID
- Orders by product/customer/date/price range
- Order frequency & statistics
- Product stock availability

## 🛠️ Technologies Used

- **Python** (OOPs, exception handling, input validation)
- **MySQL** (Data persistence and querying)
- **Tabulate** (For table-format printing)
- **Modular Design**:
  - `Entity/` for data models (Customer, Product, Cart, Order)
  - `Dao/` for data access logic
  - `Util/` for DB connection
  - `Exception/` for custom error handling

## 📂 Folder Structure

Ecom/
├── Dao/
│ └── OrderProcessorRepositoryImpl.py
├── Entity/
│ ├── customers.py
│ ├── products.py
│ └── ...
├── Util/
│ └── db_connection.py
├── Exception/
│ ├── custom_exceptions.py
├── Test/
│ └── test_cases.py
├── main.py
└── README.md


## 🧪 Testing

- Unit test cases using `unittest` module
- Covers: customer/product creation, cart operations, order placement, and exception handling

## 🚀 How to Run

1. Clone the repository
2. Set up MySQL with the required tables
3. Install dependencies:

```bash
pip install mysql-connector-python tabulate
