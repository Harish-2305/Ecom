from Dao.OrderProcessorRepositoryImpl import OrderProcesserRepositoryimpl
from Entity.products import products
from Entity.customers import customers
from Exception.custom_exceptions import CustomerNotFoundException,ProductNotFoundException,OrderNotFoundException
import re
from tabulate import tabulate


def is_valid_name(name):
    if not name.strip():
        return False
    return bool(re.match(r'^[A-Za-z ]{2,}$', name))

def is_valid_password(password: str) -> bool:
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{6,}$'
    return re.match(pattern, password) is not None

def validate_customer_login(repo):
    try:
        cid = int(input("Enter your Customer ID: "))
        password = input("Enter your password: ")

        customer = repo.getCustomerById(cid)
        if customer and customer.get_password() == password:
            print(f"\nWelcome {customer.get_name()}!")
            return customer
        else:
            print("Invalid credentials! Access denied.\n")
            return None
    except:
        print("Error validating customer.")
        return None

def customers_list(repo):
    customers_list = repo.getAllCustomers()
    print("\nAll Customers:")

    if customers_list:
        table = [[c.get_customer_id(), c.get_name(), c.get_email()] for c in customers_list]
        print(tabulate(table, headers=["Customer ID", "Name", "Email"], tablefmt="pipe"))
    else:
        print("No customers found.")

def products_list(repo):
    products_list = repo.getAllProducts()
    if products_list:
        print("\n----- All Products ------")
        table = [[
            prod.get_product_id(), prod.get_name(),
            prod.get_price(), prod.get_stockquantity()] for prod in products_list]
        print(tabulate(table, headers=["Product ID", "Name", "Price (Rs)", "Stock"], tablefmt="fancy_grid"))
        return 1

def cart_items(repo,customer):
    cart_items = repo.getAllFromCart(customer)
    if cart_items:
        from tabulate import tabulate
        table = [
            [item["cart_id"], item["product_id"], item["name"], f"Rs.{item['price']}", item["quantity"]]
            for item in cart_items
        ]
        headers = ["Cart ID", "Product ID", "Name", "Price", "Quantity"]
        print(tabulate(table, headers, tablefmt="pretty"))
    else:
        print("Cart is empty.")

def order_items(repo,customer):
    orders = repo.getOrdersByCustomer(customer.get_customer_id())
    if orders:
        table = [
            [o['order_id'], o['product_name'], o['quantity'], f"Rs.{o['total_price']}", o['order_date'],
             o['shipping_address']]
            for o in orders
        ]
        headers = ["Order ID", "Product Name", "Quantity", "Total Price", "Order Date",
                   "Shipping Address"]
        print("\nCustomer Orders:")
        print(tabulate(table, headers=headers, tablefmt="pretty"))
    else:
        print("No orders found for this customer.")

#      === customer menu ====
def customer_menu(repo):

    while True:
        print("""
            ==== Customer Menu ====
            1. Register Customer
            2. View all Customer
            3. Update Email
            4. Update Password
            5. Delete Customer
            0. Back to Main Menu
            """)
        try:
            ch=input("Enter Choice: ")
            if ch=='1':
                while True:
                    name = input("\nEnter Customer name: ")
                    if is_valid_name(name): break
                    print("Invalid name !")
                while True:
                    email = input("Enter Customer email: ")
                    if re.match(r"^[a-zA-Z0-9._%+-]+@gmail\.com$", email): break
                    print("Invalid email! Please use a valid Gmail address.")
                while True:
                    password = input("Enter password: ")
                    if is_valid_password(password): break
                    print("Invalid! password must contain uppercase,lowercase,number,special character")
                c = customers(password, name, email, password)
                customer_id = repo.createCustomer(c)
                if customer_id != -1:
                    print(f"\nCustomer created successfully with ID: {customer_id}")
                else:
                    print("\nCustomer creation failed.")

            elif ch=='2':
                customers_list(repo)

            elif ch=='3':
                cid = int(input("\nEnter Customer ID: "))
                pwd = input("Enter Password: ")
                while True:
                    new_email = input("Enter New Email: ")
                    if not re.match(r"^[a-zA-Z0-9._%+-]+@gmail\.com$", new_email):
                        print("Invalid email! Please use a valid Gmail address.")
                    else:
                        break
                if repo.updateCustomerEmail(cid, pwd, new_email):
                    print("\nEmail updated successfully.")
                else:
                    print("\nEmail update failed.")

            elif ch=='4':
                cid = int(input("\nEnter Customer ID: "))
                old_pwd = input("Enter current password: ")
                while True:
                    new_pwd = input("Enter new password: ")
                    if is_valid_password(new_pwd): break
                    print("Invalid! password must contain uppercase,lowercase,number,special character")
                if repo.updateCustomerPassword(cid, old_pwd, new_pwd):
                    print("\nPassword updated successfully!")
                else:
                    print("\nFailed to update password. Please check credentials.")

            elif ch == '5':
                cid = int(input("\nEnter customer ID to delete: "))
                pwd = input("Enter password to confirm: ")
                if repo.deleteCustomer(cid, pwd):
                    print("\nCustomer deleted successfully.")
                else:
                    print("\nCustomer deletion failed.")


            elif ch == '0':
                break

            else:
                print("\nInvalid! Enter choice from menu.")
        except CustomerNotFoundException:
            print(" Customer not found !")
        except Exception as e:
            print(" Error:", e)

#     ===== Product Menu =====
def product_menu(repo):
    while True:
        print("""
        ==== Product Menu ====
        1. Create product
        2. View all Products
        3. Update Stock 
        4. Change Price
        5. Delete Product
        0. Back to Main Menu
        """)

        ch=input("Enter Choice: ")

        try:
            if ch=='1':
                while True:
                    name = input("\nEnter Product name: ")
                    if not is_valid_name(name):
                        print("Invalid name !")
                    else:
                        break
                while True:
                    price = float(input("Enter price: "))
                    if price > 0: break
                    print("Invalid price !")
                desc = input("Enter description: ")
                while True:
                    stockQuantity = int(input("Enter stock quantity: "))
                    if stockQuantity > -1: break
                    print("The quantity must be greater than 0")
                p = products(desc, name, price, desc, stockQuantity)
                product_id = repo.createProduct(p)
                if product_id != -1:
                    print(f"\nProduct created successfully with ID: {product_id}")
                else:
                    print("\nProduct creation failed.")

            elif ch == '2':
                a=products_list(repo)
                if not a:
                    print("Product not found!")

            elif ch == '3':
                a=products_list(repo)
                if a:
                    pid = int(input("Enter Product ID to update: "))
                    while True:
                        new_qty = int(input("Enter new stock quantity: "))
                        if new_qty>-1: break
                        print("Enter valid stock!")
                    if repo.updateStock(pid, new_qty):
                        print("\nStock updated successfully")
                else:
                    print("\n No products Found ")

            elif ch == '4':
                a=products_list(repo)
                if a:
                    try:
                        pid = int(input("Enter Product ID: "))
                        while True:
                            new_price = float(input("Enter New Price: "))
                            if new_price>0: break
                            print("Enter Valid Price !")
                        if repo.updateProductPrice(pid, new_price):
                            print("Product price updated successfully!")
                        else:
                            print("Failed to update product price.")
                    except ValueError:
                        print("Invalid input.")
                else:
                    print("\n No products Found ")

            elif ch == '5':
                a=products_list(repo)
                if a:
                    pid = int(input("Enter product ID to delete: "))
                    if repo.deleteProduct(pid):
                        print("\nProduct deleted successfully")
                else:
                    print("\n No products Found !")

            elif ch == '0':
                break

            else:
                print("\nInvalid ! Enter choice from menu.")
        except ProductNotFoundException:
            print(" Product not found !")
        except Exception as e:
            print(" Error:", e)

# ==== cart menu ====
def cart_menu(repo):

    customer = validate_customer_login(repo)
    if not customer:
        return

    while True:
        print("""
            ===== Cart Menu =====
            1. Add to cart
            2. Update cart
            3. View cart
            4. Remove from cart
            0. Back to Main Menu
            """)
        choice = input("Enter your choice: ")
        try:
            if choice == "0":
                break

            elif choice == "1":
                a=products_list(repo)
                if a:
                    prod_id = int(input("Enter product ID to add: "))
                    qty = int(input("Enter quantity: "))
                    product = products(product_id=prod_id)
                    if repo.addToCart(customer, product, qty):
                        print("Added to cart.")
                else:
                    print("No product available!")
            elif choice == "2":
                try:
                    cart_items(repo,customer)
                    cart_id = int(input("Enter Cart ID to update: "))
                    action = input("Do you want to add or remove stock? (add/remove): ").strip().lower()
                    quantity = int(input("Enter quantity: "))

                    if repo.updateCart(cart_id, action, quantity):
                        print("Cart updated successfully.")
                    else:
                        print("Failed to update cart.")
                except Exception as e:
                    print("Error:", e)
            elif choice == "3":
                cart_items(repo,customer)
            elif choice == "4":
                cart_items(repo, customer)
                cart_id = int(input("Enter cart ID to remove: "))
                if repo.removeFromCartByCartId(cart_id):
                    print("Product removed from cart.")
            else:
                print("\nInvalid choice.")
        except CustomerNotFoundException:
            print(" Customer not found !")
        except ProductNotFoundException:
            print(" Product not found !")
        except Exception as e:
            print(" Error:", e)

#  ==== Order menu ====
def order_menu(repo):
    customer = validate_customer_login(repo)
    if not customer:
        return
    while True:
        print("""
        ===== Order Menu =====
        1. Place Order
        2. View Order
        3. Update Shipping Address
        4. Delete Order
        0. Back To Main Menu
        """)

        ch=input("Enter Choice: ")
        try:
            if ch=='0':
                break
            elif ch=='1':
                cart_items(repo,customer)
                cart_id = int(input("Enter cart ID: "))
                shipping = input("Enter shipping address: ")
                if repo.placeOrder(customer, cart_id, shipping):
                    print("Order placed successfully")

            elif ch == '2':
                order_items(repo,customer)

            elif ch == '3':
                order_items(repo, customer)
                try:
                    order_id = int(input("\nEnter Order ID to update: "))
                    new_address = input("Enter new shipping address: ")
                    if repo.updateShippingAddress(order_id, new_address):
                        print("\nShipping address updated successfully!")
                    else:
                        print("\nFailed to update shipping address.")
                except ValueError:
                    print("Invalid input! Please enter a valid order ID.")

            elif ch == '4':
                order_items(repo, customer)
                order_id = int(input("\nEnter Order ID to cancel: "))
                if repo.cancelOrder(order_id):
                    print("\nOrder cancelled successfully.")

            else:
                print("Invalid ! enter from Menu")
        except CustomerNotFoundException:
            print(" Customer not found !")
        except ProductNotFoundException:
            print(" Product not found !")
        except OrderNotFoundException:
            print(" No orders found !")
        except Exception as e:
            print(" Error:", e)

# === Reports ===
def reports(repo):
    while True:
        print("""
        ===== Reports Menu =====
        1. Customers by product ID
        2. Customers Order Count
        3. Products with stock
        4. Products with empty stock
        5. Frequently ordered products
        6. Products not ordered
        7. Carts by product ID
        8. orders by customer ID
        9. Orders by product ID
        10. Orders by date
        11. Orders in date range
        12. All Orders
        0. Back To Main Menu
        """)
        ch=input("Enter Choice: ")
        try:
            if ch=='0':
                break

            elif ch =='1':
                products_list(repo)
                product_id = int(input("\nEnter Product ID: "))
                customer = repo.getCustomersByProductId(product_id)
                if customer:
                    print("\nCustomers who purchased this product:")
                    for c in customer:
                        print(f"ID: {c['customer_id']}, Name: {c['name']}, Email: {c['email']}")
                else:
                    print("No customers found for this product.")

            elif ch =='2':
                order_counts = repo.getCustomerOrderCounts()
                if order_counts:
                    headers = ["Customer ID", "Name", "Email", "Order Count"]
                    table_data = [
                        [row["customer_id"], row["name"], row["email"], row["order_count"]]
                        for row in order_counts
                    ]
                    print("\nCustomer Order Counts:")
                    print(tabulate (table_data, headers=headers, tablefmt="pipe"))
                else:
                    print("No customer orders found.")

            elif ch =='3':
                products = repo.getProductsWithStock()
                if products:
                    headers = ["Product ID", "Name", "Description", "Price", "Stock"]
                    table_data = [
                        [p["product_id"], p["name"], p["description"], f"Rs.{p['price']}", p["stockQuantity"]]
                        for p in products
                    ]
                    print("\nProducts with Available Stock:")
                    print(tabulate(table_data, headers=headers, tablefmt="pretty"))
                else:
                    print("No products with stock available.")

            elif ch == '4':
                products = repo.getProductsWithZeroStock()
                if products:
                    headers = ["Product ID", "Name", "Description", "Price", "Stock"]
                    table_data = [
                        [p["product_id"], p["name"], p["description"], f"Rs.{p['price']}", p["stockQuantity"]]
                        for p in products
                    ]
                    print("\nProducts with Empty Stock:")
                    print(tabulate(table_data, headers=headers, tablefmt="pipe"))
                else:
                    print("All products are currently in stock.")

            elif ch == '5':
                frequent_products = repo.getFrequentlyOrderedProducts()
                if frequent_products:
                    headers = ["Product ID", "Name", "Description", "Price", "Order Count"]
                    table_data = [
                        [p["product_id"], p["name"], p["description"], f"Rs.{p['price']}", p["order_count"]]
                        for p in frequent_products
                    ]
                    print("\nFrequently Ordered Products:")
                    print(tabulate(table_data, headers=headers, tablefmt="pretty"))
                else:
                    print("No product orders found.")

            elif ch == '6':
                unordered_products = repo.getProductsNotOrdered()
                if unordered_products:
                    headers = ["Product ID", "Name", "Description", "Price", "Stock"]
                    table_data = [
                        [p["product_id"], p["name"], p["description"], f"Rs.{p['price']}", p["stockQuantity"]]
                        for p in unordered_products
                    ]
                    print("\nProducts Not Yet Ordered:")
                    print(tabulate(table_data, headers=headers, tablefmt="pretty"))
                else:
                    print("All products have been ordered at least once.")

            elif ch == '7':
                products_list(repo)
                prod_id = int(input("Enter Product ID to view its carts: "))
                cart_data = repo.getCartsByProductId(prod_id)
                if cart_data:
                    headers = ["Cart ID", "Customer ID", "Customer Name", "Email", "Product ID", "Product Name",
                               "Quantity"]
                    table = [
                        [row["cart_id"], row["customer_id"], row["customer_name"], row["email"],
                         row["product_id"], row["product_name"], row["quantity"]]
                        for row in cart_data
                    ]
                    print("\nCarts Containing Product:")
                    print(tabulate(table, headers=headers, tablefmt="pretty"))
                else:
                    print("No carts found for the given product ID.")

            elif ch == '8':
                customers_list(repo)
                customer_id = int(input("Enter Customer ID to view orders: "))
                orders = repo.getOrdersByCustomer(customer_id)
                if orders:
                    headers = ["Order ID", "Product", "Quantity", "Total Price", "Shipping Address", "Date"]
                    table = [
                        [o['order_id'], o['product_name'], o['quantity'], f"Rs.{o['total_price']}",
                         o['shipping_address'], o['order_date']]
                        for o in orders
                    ]
                    print("\nOrders for Customer:")
                    print(tabulate(table, headers=headers, tablefmt="pretty"))
                else:
                    print("No orders found for this customer.")

            elif ch == '9':
                products_list(repo)
                prod_id = int(input("Enter Product ID to view related orders: "))
                orders = repo.getOrdersByProductId(prod_id)

                if orders:
                    headers = ["Order ID", "Customer ID", "Customer Name", "Quantity", "Total Price",
                               "Shipping Address", "Order Date"]
                    table = [
                        [o['order_id'], o['customer_id'], o['customer_name'], o['quantity'], f"Rs.{o['total_price']}",
                         o['shipping_address'], o['order_date']]
                        for o in orders
                    ]
                    print("\nOrders containing this product:")
                    print(tabulate(table, headers=headers, tablefmt="pretty"))
                else:
                    print("No orders found for this product.")

            elif ch == '10':
                date_input = input("Enter order date (YYYY-MM-DD): ")
                if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_input):
                    print("Invalid date format! Please enter in YYYY-MM-DD format (e.g., 2025-07-01)")
                else:
                    orders = repo.getOrdersByDate(date_input)
                    if orders:
                        headers = ["Order ID", "Customer ID", "Customer Name", "Total Price", "Shipping Address",
                                   "Order Date"]
                        table = [
                            [o['order_id'], o['customer_id'], o['customer_name'], f"Rs.{o['total_price']}",
                             o['shipping_address'], o['order_date']]
                            for o in orders
                        ]
                        print("\nOrders on selected date:")
                        print(tabulate(table, headers=headers, tablefmt="pretty"))
                    else:
                        print("No orders found on this date.")

            elif ch == '11':
                start_date = input("Enter start date (YYYY-MM-DD): ")
                end_date = input("Enter end date (YYYY-MM-DD): ")

                date_pattern = r"^\d{4}-\d{2}-\d{2}$"
                if not re.match(date_pattern, start_date) or not re.match(date_pattern, end_date):
                    print("Invalid date format! Please enter in YYYY-MM-DD format (e.g., 2025-06-01)")
                else:
                    orders = repo.getOrdersInDateRange(start_date, end_date)
                    if orders:
                        headers = ["Order ID", "Customer ID", "Customer Name", "Total Price", "Shipping Address",
                                   "Order Date"]
                        table = [
                            [o['order_id'], o['customer_id'], o['customer_name'], f"Rs.{o['total_price']}",
                             o['shipping_address'], o['order_date']]
                            for o in orders
                        ]
                        print(f"\nOrders from {start_date} to {end_date}:")
                        print(tabulate(table, headers=headers, tablefmt="pretty"))
                    else:
                        print("No orders found in this date range.")

            elif ch == '12':
                orders = repo.getAllOrders()
                if orders:
                    from tabulate import tabulate
                    table = [
                        [o['order_id'], o['customer_name'], o['product_name'], o['quantity'],
                         f"Rs.{o['total_price']}", o['shipping_address'], o['order_date']]
                        for o in orders
                    ]
                    headers = ["Order ID", "Customer", "Product", "Qty", "Total Price", "Address", "Date"]
                    print("\nAll Orders:")
                    print(tabulate(table, headers=headers, tablefmt="pipe"))
                else:

                    print("No orders found.")


            else:
                print("\n Invalid ! Enter choice from Menu.")
        except CustomerNotFoundException:
            print(" Customer not found !")
        except ProductNotFoundException:
            print(" Product not found !")
        except OrderNotFoundException:
            print(" No orders found !")
        except Exception as e:
            print(" Error:", e)


def main():
    repo=OrderProcesserRepositoryimpl()
    print("\n==== Welcome to the ECOMMERCE  ====")
    while True:
        print("""
           ====== MAIN MENU ======
           1. Customer Menu
           2. Product Menu
           3. Cart Menu
           4. Order Menu
           5. Reports
           0. Exit
           """)
        choice = input("Enter your choice: ")
        try:
            if choice == '1':
                customer_menu(repo)
            elif choice == '2':
                product_menu(repo)
            elif choice == '3':
                cart_menu(repo)
            elif choice == '4':
                order_menu(repo)
            elif choice == '5':
                reports(repo)
            elif choice == '0':
                print("\nThank you for Using. \nVisit Again, Goodbye!")
                break
            else:
                print("Invalid choice !"
                      "\n Enter choice from menu.")

        except CustomerNotFoundException:
            print(" Customer not found !")
        except ProductNotFoundException:
            print(" Product not found !")
        except OrderNotFoundException:
            print(" No orders found !")
        except Exception as e:
            print(" Error:", e)

if __name__ == '__main__':
    main()