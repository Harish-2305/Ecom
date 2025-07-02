-- Creating database named Ecom 
Create database ecom;
use ecom;

-- Creating table  customers
CREATE TABLE IF NOT EXISTS customers(
customer_id int primary Key auto_increment,
name varchar(50) not null,
email varchar(50) not null unique,
password varchar(50) not null 
);

-- Creating table products
CREATE TABLE IF NOT EXISTS PRODUCTS(
product_id int primary key auto_increment,
name varchar(50) not null,
price decimal(10,2) not null,
description text ,
stockQuantity int not null
);

-- Creating table cart 
CREATE TABLE IF NOT EXISTS cart(
cart_id int primary key auto_increment,
customer_id int,
product_id int,
quantity int not null,
foreign key (customer_id) references customers(customer_id),
foreign key (product_id) references products(product_id)
ON update cascade
on delete cascade
);

-- Creating table orders

CREATE TABLE IF NOT EXISTS orders(
order_id int Primary Key auto_increment,
customer_id int,
order_date date,
total_price decimal(10,2),
shipping_address text,
foreign key (customer_id) references customers(customer_id)
on update cascade
on delete cascade
); 

-- Creating table order_items
CREATE TABLE IF NOT EXISTS order_items(
order_item_id int primary key auto_increment,
order_id int,
product_id int,
quantity int,
foreign key (order_id) references orders(order_id),
foreign key (product_id) references products(product_id)
on update cascade
on delete cascade
);

select * from customers;

select * from products;

select * from cart;

select * from orders;


