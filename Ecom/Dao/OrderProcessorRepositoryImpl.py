from Dao.OrderProcessorRepository import OderProcessorRespository
from Entity.products import products
from Entity.customers import customers
from Util.db_connection import DBconnection
from Exception.custom_exceptions import CustomerNotFoundException, ProductNotFoundException, OrderNotFoundException
import mysql
from datetime import date
class OrderProcesserRepositoryimpl(OderProcessorRespository):

    def __init__(self):
        self.conn=DBconnection.get_connection()
        self.cursor=self.conn.cursor(dictionary=True)



    def createProduct(self,products:products) -> bool:
        try:
            sql="""
            INSERT INTO products(name,price,description,stockQuantity)
            values(%s,%s,%s,%s)
            """
            values=(
                products.get_name(),
                products.get_price(),
                products.get_description(),
                products.get_stockquantity()
            )
            self.cursor.execute(sql,values)
            self.conn.commit()
            return self.cursor.lastrowid
        except mysql.connector.Error as e:
            print(f"Error creating product:{e}")
            return False

    def createCustomer(self,customers:customers) -> bool:
        try:
            sql="""
            INSERT INTO customers(name,email,password)
            VALUES(%s,%s,%s)
            """
            values=(
                customers.get_name(),
                customers.get_email(),
                customers.get_password()
            )
            self.cursor.execute(sql,values)
            self.conn.commit()
            return self.cursor.lastrowid
        except mysql.connector.Error as e:
            print(f"Error creating Customer:{e}")
            return False

    def deleteProduct(self,product_id:int) ->bool:
        try:
            self.cursor.execute("SELECT * FROM products WHERE product_id=%s",(product_id,))
            if not self.cursor.fetchone():
                raise ProductNotFoundException
            sql="DELETE FROM products WHERE product_id=%s"
            self.cursor.execute(sql,(product_id,))
            self.conn.commit()
            return True
        except mysql.connector.Error as e:
            print(f"Error deleting product: {e}")
            return False

    def deleteCustomer(self, customer_id: int, password: str) -> bool:
        try:
            self.cursor.execute("SELECT * FROM customers WHERE customer_id=%s", (customer_id,))
            customer = self.cursor.fetchone()

            if not customer:
                raise CustomerNotFoundException

            if customer['password'] != password:
                print("Incorrect password. Cannot delete customer.")
                return False

            sql = "DELETE FROM customers WHERE customer_id=%s"
            self.cursor.execute(sql, (customer_id,))
            self.conn.commit()
            return True

        except mysql.connector.Error as e:
            print(f"Error deleting customer: {e}")
            return False

    def addToCart(self, customers: customers, products: products, quantity: int) -> bool:
        try:
            # Validate customer
            self.cursor.execute("SELECT * FROM customers WHERE customer_id=%s", (customers.get_customer_id(),))
            if not self.cursor.fetchone():
                raise CustomerNotFoundException

            # Validate product
            self.cursor.execute("SELECT * FROM products WHERE product_id=%s", (products.get_product_id(),))
            product_row = self.cursor.fetchone()
            if not product_row:
                raise ProductNotFoundException

            available_qty = product_row['stockQuantity']
            if quantity > available_qty:
                raise ValueError("Requested quantity exceeds available stock.")

            # Check if product already in cart
            self.cursor.execute("""
                SELECT quantity FROM cart 
                WHERE customer_id=%s AND product_id=%s
            """, (customers.get_customer_id(), products.get_product_id()))
            existing = self.cursor.fetchone()

            if existing:
                # Update existing quantity
                new_qty = existing['quantity'] + quantity
                update_cart_sql = """
                    UPDATE cart SET quantity = %s 
                    WHERE customer_id = %s AND product_id = %s
                """
                self.cursor.execute(update_cart_sql, (
                    new_qty,
                    customers.get_customer_id(),
                    products.get_product_id()
                ))
            else:
                # Insert new item into cart
                insert_cart_sql = """
                    INSERT INTO cart(customer_id, product_id, quantity)
                    VALUES (%s, %s, %s)
                """
                self.cursor.execute(insert_cart_sql, (
                    customers.get_customer_id(),
                    products.get_product_id(),
                    quantity
                ))

            # Deduct from stock
            update_stock_sql = "UPDATE products SET stockQuantity = stockQuantity - %s WHERE product_id = %s"
            self.cursor.execute(update_stock_sql, (quantity, products.get_product_id()))

            self.conn.commit()
            return True

        except mysql.connector.Error as e:
            print(f"Error in adding to cart: {e}")
            self.conn.rollback()
            return False
        except ValueError as ve:
            print(f"Validation error: {ve}")
            self.conn.rollback()
            return False

    def removeFromCart(self, customers: customers, products:products) -> bool:
        try:
            self.cursor.execute("SELECT * FROM cart WHERE customer_id = %s AND product_id = %s",
                                (customers.get_customer_id(), products.get_product_id()))
            result=self.cursor.fetchone()
            if not result:
                raise ProductNotFoundException
            quantity_to_restore = result['quantity']

            # Update the product stock by adding back the quantity
            update_stock_sql = """
                    UPDATE products SET stockQuantity = stockQuantity + %s WHERE product_id = %s
                    """
            self.cursor.execute(update_stock_sql, (quantity_to_restore, products.get_product_id()))
            sql="DELETE FROM cart WHERE customer_id=%s AND product_id=%s"
            self.cursor.execute(sql,(customers.get_customer_id(),products.get_product_id()))
            self.conn.commit()
            return True
        except mysql.connector.Error as e:
            print(f"Error in removing from cart: {e}")
            return False


    def getAllFromCart(self,customers:customers) -> list[products]:
        try:
            sql = ("""
                    SELECT c.cart_id, p.product_id, p.name, p.price, p.description, c.quantity
                    FROM cart c
                    JOIN products p ON c.product_id = p.product_id
                    WHERE c.customer_id = %s
                """)
            self.cursor.execute(sql, (customers.get_customer_id(),))
            result = self.cursor.fetchall()
            if not result:
                raise CustomerNotFoundException

            cart_items = []
            for row in result:
                cart_items.append({
                    "cart_id": row["cart_id"],
                    "product_id": row["product_id"],
                    "name": row["name"],
                    "price": row["price"],
                    "description": row["description"],
                    "quantity": row["quantity"]
                })
            return cart_items

        except mysql.connector.Error as e:
            print(f"Error retrieving cart: {e}")
            return []

    def placeOrder(self, customers: customers, cart_id: int, shippingAddress: str) -> bool:
        try:
            # Step 1: Get the cart item by cart_id
            self.cursor.execute("""
                SELECT c.product_id, c.quantity, p.price
                FROM cart c
                JOIN products p ON c.product_id = p.product_id
                WHERE c.cart_id = %s AND c.customer_id = %s
            """, (cart_id, customers.get_customer_id()))

            row = self.cursor.fetchone()
            if not row:
                raise ValueError("Cart item not found")

            product_id = row['product_id']
            quantity = row['quantity']
            price = row['price']
            total_price = price * quantity

            # Step 2: Create order
            self.cursor.execute("""
                INSERT INTO orders (customer_id, order_date, total_price, shipping_address)
                VALUES (%s, %s, %s, %s)
            """, (customers.get_customer_id(), date.today(), total_price, shippingAddress))
            order_id = self.cursor.lastrowid

            # Step 3: Add to order_items
            self.cursor.execute("""
                INSERT INTO order_items (order_id, product_id, quantity)
                VALUES (%s, %s, %s)
            """, (order_id, product_id, quantity))

            # Step 4: Clear the item from cart
            self.cursor.execute("DELETE FROM cart WHERE cart_id = %s", (cart_id,))

            self.conn.commit()
            return True

        except mysql.connector.Error as e:
            print(f"Error in placing the order: {e}")
            self.conn.rollback()
            return False
        except ValueError as ve:
            print(f"Validation error in placing order: {ve}")
            self.conn.rollback()
            return False

    def getOrdersByCustomer(self,customer_id) -> list[dict[str,any]]:
        try:
            self.cursor.execute("SELECT * FROM customers WHERE customer_id=%s",(customer_id,))
            if not self.cursor.fetchone():
                raise CustomerNotFoundException

            sql="""
            SELECT o.order_id,o.order_date,o.total_price,o.shipping_address,
            p.name as product_name,oi.quantity
            FROM orders o
            JOIN order_items oi ON o.order_id=oi.order_id
            JOIN products p ON oi.product_id=p.product_id
            WHERE o.customer_id=%s
            """
            self.cursor.execute(sql,(customer_id,))
            orders=self.cursor.fetchall()
            if not orders:
                raise OrderNotFoundException
            return orders
        except mysql.connector.Error as e:
            print(f"Error in retrieving orders : {e}")
            return []

    def getAllProducts(self) -> list[products]:
        try:
            self.cursor.execute("SELECT * FROM products")
            rows = self.cursor.fetchall()
            return [products(product_id=row['product_id'], name=row['name'], description=row['description'],
                             price=row['price'], stockquantity=row['stockQuantity']) for row in rows]
        except mysql.connector.Error as e:
            print(f"Error fetching products: {e}")
            return []

    def cancelOrder(self, order_id: int) -> bool:
        try:
            # Check if order exists
            self.cursor.execute("SELECT * FROM orders WHERE order_id = %s", (order_id,))
            order = self.cursor.fetchone()
            if not order:
                raise OrderNotFoundException

            # Restore stock quantity for each product in the order
            self.cursor.execute("SELECT product_id, quantity FROM order_items WHERE order_id = %s", (order_id,))
            items = self.cursor.fetchall()
            for item in items:
                update_stock_sql = "UPDATE products SET stockQuantity = stockQuantity + %s WHERE product_id = %s"
                self.cursor.execute(update_stock_sql, (item['quantity'], item['product_id']))

            # Delete from order_items
            self.cursor.execute("DELETE FROM order_items WHERE order_id = %s", (order_id,))

            # Delete from orders
            self.cursor.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))

            self.conn.commit()
            return True
        except OrderNotFoundException:
            raise
        except mysql.connector.Error as e:
            print(f"Error canceling order: {e}")
            self.conn.rollback()
            return False

    def getOrderById(self, order_id: int) -> dict:
        try:
            # Check if order exists
            self.cursor.execute("SELECT * FROM orders WHERE order_id = %s", (order_id,))
            order = self.cursor.fetchone()
            if not order:
                raise OrderNotFoundException

            # Fetch order items
            self.cursor.execute("""
                SELECT oi.quantity, p.name AS product_name, p.price
                FROM order_items oi
                JOIN products p ON oi.product_id = p.product_id
                WHERE oi.order_id = %s
            """, (order_id,))
            items = self.cursor.fetchall()

            return {
                "order_id": order['order_id'],
                "customer_id": order['customer_id'],
                "order_date": order['order_date'],
                "total_price": order['total_price'],
                "shipping_address": order['shipping_address'],
                "items": items
            }

        except mysql.connector.Error as e:
            print(f"Error fetching order: {e}")
            return {}

    def getCartById(self, cart_id: int) -> dict:
        try:
            sql = """
                SELECT c.cart_id, c.customer_id, c.product_id, c.quantity,
                       p.name, p.price, p.description
                FROM cart c
                JOIN products p ON c.product_id = p.product_id
                WHERE c.cart_id = %s
            """
            self.cursor.execute(sql, (cart_id,))
            row = self.cursor.fetchone()
            if not row:
                raise ProductNotFoundException
            return row
        except mysql.connector.Error as e:
            print(f"Error fetching cart: {e}")
            return {}

    def updateStock(self, product_id: int, new_quantity: int) -> bool:
        try:
            self.cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
            if not self.cursor.fetchone():
                raise ProductNotFoundException

            sql = "UPDATE products SET stockQuantity = %s WHERE product_id = %s"
            self.cursor.execute(sql, (new_quantity, product_id))
            self.conn.commit()
            return True
        except mysql.connector.Error as e:
            print(f"Error updating stock: {e}")
            return False

    def updateCustomerEmail(self, customer_id: int, password: str, new_email: str) -> bool:
        try:
            self.cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (customer_id,))
            result = self.cursor.fetchone()

            if not result:
                raise CustomerNotFoundException

            if result['password'] != password:
                print("Incorrect password. Email update not allowed.")
                return False

            update_sql = "UPDATE customers SET email = %s WHERE customer_id = %s"
            self.cursor.execute(update_sql, (new_email, customer_id))
            self.conn.commit()
            return True

        except mysql.connector.Error as e:
            print(f"Error updating email: {e}")
            return False

    def getAllCustomers(self) -> list[customers]:
        try:
            self.cursor.execute("SELECT * FROM customers")
            rows = self.cursor.fetchall()
            return [customers(customer_id=row['customer_id'], name=row['name'], email=row['email'],
                              password=row['password']) for row in rows]
        except mysql.connector.Error as e:
            print(f"Error fetching customers: {e}")
            return []

    def updateCustomerPassword(self, customer_id: int, current_password: str, new_password: str) -> bool:
        try:
            # Check if customer exists and password matches
            self.cursor.execute(
                "SELECT * FROM customers WHERE customer_id = %s AND password = %s",
                (customer_id, current_password)
            )
            if not self.cursor.fetchone():
                print("Invalid customer ID or current password.")
                return False

            # Update password
            self.cursor.execute(
                "UPDATE customers SET password = %s WHERE customer_id = %s",
                (new_password, customer_id)
            )
            self.conn.commit()
            return True
        except mysql.connector.Error as e:
            print(f"Error updating password: {e}")
            return False

    def updateProductPrice(self, product_id: int, new_price: float) -> bool:
        try:
            self.cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
            if not self.cursor.fetchone():
                raise ProductNotFoundException("Product not found.")

            self.cursor.execute(
                "UPDATE products SET price = %s WHERE product_id = %s",
                (new_price, product_id)
            )
            self.conn.commit()
            return True
        except mysql.connector.Error as e:
            print(f"Error updating product price: {e}")
            return False
        except ProductNotFoundException as pnf:
            print(pnf)
            return False

    def getCustomerById(self, customer_id: int):
        try:
            self.cursor.execute("SELECT * FROM customers WHERE customer_id=%s", (customer_id,))
            row = self.cursor.fetchone()
            if row:
                return customers(customer_id=row['customer_id'], name=row['name'], email=row['email'],
                                 password=row['password'])
            return None
        except mysql.connector.Error as e:
            print("Error fetching customer:", e)
            return None

    def updateCart(self, cart_id: int, action: str, quantity: int) -> bool:
        try:
            # Get current cart info
            self.cursor.execute("SELECT * FROM cart WHERE cart_id = %s", (cart_id,))
            cart_item = self.cursor.fetchone()

            if not cart_item:
                raise ValueError("Cart item not found.")

            current_qty = cart_item['quantity']
            product_id = cart_item['product_id']

            # Fetch product info
            self.cursor.execute("SELECT stockQuantity FROM products WHERE product_id = %s", (product_id,))
            product = self.cursor.fetchone()
            if not product:
                raise ProductNotFoundException

            current_stock = product['stockQuantity']

            if action.lower() == "add":
                if quantity > current_stock:
                    raise ValueError("Insufficient stock available.")
                new_qty = current_qty + quantity

                # Update cart and product stock
                self.cursor.execute("UPDATE cart SET quantity = %s WHERE cart_id = %s", (new_qty, cart_id))
                self.cursor.execute("UPDATE products SET stockQuantity = stockQuantity - %s WHERE product_id = %s",
                                    (quantity, product_id))

            elif action.lower() == "remove":
                if quantity >= current_qty:
                    raise ValueError("Cannot remove more than existing quantity.")
                new_qty = current_qty - quantity

                # Update cart and restore stock
                self.cursor.execute("UPDATE cart SET quantity = %s WHERE cart_id = %s", (new_qty, cart_id))
                self.cursor.execute("UPDATE products SET stockQuantity = stockQuantity + %s WHERE product_id = %s",
                                    (quantity, product_id))

            else:
                raise ValueError("Invalid action. Use 'add' or 'remove'.")

            self.conn.commit()
            return True

        except mysql.connector.Error as e:
            print(f"Database error while updating cart: {e}")
            self.conn.rollback()
            return False
        except ValueError as ve:
            print(f"Validation error: {ve}")
            return False

    def removeFromCartByCartId(self, cart_id: int) -> bool:
        try:
            # Fetch product_id and quantity from the cart
            self.cursor.execute("SELECT product_id, quantity FROM cart WHERE cart_id = %s", (cart_id,))
            result = self.cursor.fetchone()
            if not result:
                raise ProductNotFoundException

            product_id = result['product_id']
            quantity_to_restore = result['quantity']

            # Restore product stock
            update_stock_sql = """
                UPDATE products SET stockQuantity = stockQuantity + %s WHERE product_id = %s
            """
            self.cursor.execute(update_stock_sql, (quantity_to_restore, product_id))

            # Delete from cart
            delete_sql = "DELETE FROM cart WHERE cart_id = %s"
            self.cursor.execute(delete_sql, (cart_id,))

            self.conn.commit()
            return True
        except mysql.connector.Error as e:
            print(f"Error in removing from cart: {e}")
            return False

    def updateShippingAddress(self, order_id: int, new_address: str) -> bool:
        try:
            self.cursor.execute("SELECT * FROM orders WHERE order_id = %s", (order_id,))
            if not self.cursor.fetchone():
                raise OrderNotFoundException

            update_sql = "UPDATE orders SET shipping_address = %s WHERE order_id = %s"
            self.cursor.execute(update_sql, (new_address, order_id))
            self.conn.commit()
            return True
        except mysql.connector.Error as e:
            print(f"Error updating shipping address: {e}")
            return False
    #  Reports

    def getCustomersByProductId(self, product_id: int) -> list[dict]:
        try:
            query = """
                SELECT DISTINCT c.customer_id, c.name, c.email
                FROM customers c
                JOIN orders o ON c.customer_id = o.customer_id
                JOIN order_items oi ON o.order_id = oi.order_id
                WHERE oi.product_id = %s
            """
            self.cursor.execute(query, (product_id,))
            results = self.cursor.fetchall()
            return results
        except mysql.connector.Error as e:
            print(f"Error fetching customers by product ID: {e}")
            return []

    def getCustomerOrderCounts(self) -> list[dict]:
        try:
            query = """
                SELECT c.customer_id, c.name, c.email, COUNT(o.order_id) AS order_count
                FROM customers c
                LEFT JOIN orders o ON c.customer_id = o.customer_id
                GROUP BY c.customer_id, c.name, c.email
                ORDER BY order_count DESC
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Error retrieving customer order counts: {e}")
            return []

    from tabulate import tabulate

    def getProductsWithStock(self) -> list[dict]:
        try:
            sql = """
                SELECT product_id, name, description, price, stockQuantity
                FROM products
                WHERE stockQuantity > 0
            """
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Error fetching products with stock: {e}")
            return []

    def getProductsWithZeroStock(self) -> list[dict]:
        try:
            sql = """
                SELECT product_id, name, description, price, stockQuantity
                FROM products
                WHERE stockQuantity = 0
            """
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Error fetching out-of-stock products: {e}")
            return []

    def getFrequentlyOrderedProducts(self) -> list[dict]:
        try:
            sql = """
                SELECT p.product_id, p.name, p.description, p.price, COUNT(oi.product_id) AS order_count
                FROM products p
                JOIN order_items oi ON p.product_id = oi.product_id
                GROUP BY p.product_id, p.name, p.description, p.price
                ORDER BY order_count DESC
            """
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Error fetching frequently ordered products: {e}")
            return []

    def getProductsNotOrdered(self) -> list[dict]:
        try:
            sql = """
                SELECT p.product_id, p.name, p.description, p.price, p.stockQuantity
                FROM products p
                LEFT JOIN order_items oi ON p.product_id = oi.product_id
                WHERE oi.product_id IS NULL
            """
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Error fetching unordered products: {e}")
            return []

    def getCartsByProductId(self, product_id: int) -> list[dict]:
        try:
            sql = """
                SELECT c.cart_id, cu.customer_id, cu.name AS customer_name, cu.email,
                       p.product_id, p.name AS product_name, c.quantity
                FROM cart c
                JOIN customers cu ON c.customer_id = cu.customer_id
                JOIN products p ON c.product_id = p.product_id
                WHERE c.product_id = %s
            """
            self.cursor.execute(sql, (product_id,))
            return self.cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Error fetching cart details for product: {e}")
            return []

    def getOrdersByCustomer(self, customer_id: int) -> list[dict]:
        try:
            self.cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (customer_id,))
            if not self.cursor.fetchone():
                raise CustomerNotFoundException

            sql = """
                SELECT o.order_id, o.order_date, o.total_price, o.shipping_address,
                       p.name AS product_name, oi.quantity
                FROM orders o
                JOIN order_items oi ON o.order_id = oi.order_id
                JOIN products p ON oi.product_id = p.product_id
                WHERE o.customer_id = %s
                ORDER BY o.order_date DESC
            """
            self.cursor.execute(sql, (customer_id,))
            orders = self.cursor.fetchall()
            if not orders:
                raise OrderNotFoundException
            return orders
        except mysql.connector.Error as e:
            print(f"Error in retrieving orders : {e}")
            return []

    def getOrdersByProductId(self, product_id: int) -> list[dict]:
        try:
            self.cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
            if not self.cursor.fetchone():
                raise ProductNotFoundException

            sql = """
                SELECT o.order_id, o.order_date, o.total_price, o.shipping_address,
                       c.customer_id, c.name as customer_name, oi.quantity
                FROM orders o
                JOIN order_items oi ON o.order_id = oi.order_id
                JOIN customers c ON o.customer_id = c.customer_id
                WHERE oi.product_id = %s
                ORDER BY o.order_date DESC
            """
            self.cursor.execute(sql, (product_id,))
            orders = self.cursor.fetchall()
            if not orders:
                raise OrderNotFoundException
            return orders
        except mysql.connector.Error as e:
            print(f"Error in retrieving product orders: {e}")
            return []

def getOrdersByDate(self, order_date: str) -> list[dict]:
    try:
        sql = """
            SELECT o.order_id, o.order_date, o.total_price, o.shipping_address,
                   c.customer_id, c.name AS customer_name
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            WHERE o.order_date = %s
        """
        self.cursor.execute(sql, (order_date,))
        orders = self.cursor.fetchall()
        if not orders:
            raise OrderNotFoundException
        return orders
    except mysql.connector.Error as e:
        print(f"Error retrieving orders by date: {e}")
        return []

def getOrdersInDateRange(self, start_date: str, end_date: str) -> list[dict]:
    try:
        sql = """
            SELECT o.order_id, o.order_date, o.total_price, o.shipping_address,
                   c.customer_id, c.name AS customer_name
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            WHERE o.order_date BETWEEN %s AND %s
            ORDER BY o.order_date
        """
        self.cursor.execute(sql, (start_date, end_date))
        orders = self.cursor.fetchall()
        if not orders:
            raise OrderNotFoundException
        return orders
    except mysql.connector.Error as e:
        print(f"Error retrieving orders by date range: {e}")
        return []

def getAllOrders(self) -> list[dict]:
    try:
        sql = """
            SELECT o.order_id, o.order_date, o.total_price, o.shipping_address,
                   c.customer_id, c.name AS customer_name,
                   p.name AS product_name, oi.quantity
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN products p ON oi.product_id = p.product_id
            ORDER BY o.order_date DESC
        """
        self.cursor.execute(sql)
        return self.cursor.fetchall()
    except mysql.connector.Error as e:
        print(f"Error retrieving all orders: {e}")
        return []









