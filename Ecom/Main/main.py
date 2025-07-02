from Dao.OrderProcessorRepositoryImpl import OrderProcesserRepositoryimpl
from Entity.products import products
from Entity.customers import customers
from Exception.custom_exceptions import CustomerNotFoundException,ProductNotFoundException,OrderNotFoundException
import re
def is_valid_name(name):
    if not name.strip():
        return False
    return bool(re.match(r'^[A-Za-z ]{2,}$', name))

def main():
    repo=OrderProcesserRepositoryimpl()
    print("\n==== Welcome to the ECOMMERCE  ====")
    while True:
        print("\n ===== ECOMMERCE APP MENU =====")
        print("""
                1. Register Customer
                2. Create Product 
                3. View all products
                4. Update the Stock
                5. Add to Cart
                6. View Cart by Customer ID
                7. View cart by Cart ID
                8. Remove from Cart
                9. place Order
                10. View Order by customer ID
                11. View Order by Order ID
                12. Cancel Order
                13. Delete Customer
                14. Delete Product
                15. Exit
                """)
        choice= input("Enter Your Choice: ")

        try :
                # Creating new customer
            if choice=="1":
                while True:
                    name = input("Enter Customer name: ")
                    if not is_valid_name(name): print("Invalid name !")
                    else: break
                while True:
                    email = input("Enter Customer email: ")
                    if not re.match(r"^[a-zA-Z0-9._%+-]+@gmail\.com$", email):
                        print("Invalid email! Please use a valid Gmail address.")
                    else: break
                while True:
                    password=input("Enter password: ")
                    if len(password)>5: break
                    print("The password must be minimum six character !")
                c=customers(password,name,email,password)
                if repo.createCustomer(c):
                    print("\n Customer Created successfully")

            elif choice == '2':
                while True:
                    name = input("Enter Product name: ")
                    if not is_valid_name(name): print("Invalid name !")
                    else: break
                while True:
                    price = float(input("Enter price: "))
                    if price >0: break
                    print("Invalid price !")
                desc = input("Enter description: ")
                while True:
                    stockQuantity = int(input("Enter stock quantity: "))
                    if stockQuantity > -1: break
                    print("\nThe quantity must be greater than 0")
                p = products(desc,name , price, desc,stockQuantity)
                if repo.createProduct(p):
                    print("\nProduct created successfully")

            elif choice == '3':

                products_list = repo.getAllProducts()
                if products_list:
                    print("\nAll Products:")
                    for prod in products_list:
                        print(
                            f"ID: {prod.get_product_id()}, Name: {prod.get_name()}, Price: Rs.{prod.get_price()}, Stock: {prod.get_stockquantity()}")
                else:
                    print("\n No products Found ")

            elif choice == "4":
                products_list = repo.getAllProducts()
                if products_list:
                    print("\nAll Products:")
                    for prod in products_list:
                        print(
                            f"ID: {prod.get_product_id()}, Name: {prod.get_name()}, Price: Rs.{prod.get_price()}, Stock: {prod.get_stockquantity()}")
                    pid = int(input("Enter Product ID to update: "))
                    new_qty = int(input("Enter new stock quantity: "))
                    if repo.updateStock(pid, new_qty):
                        print("Stock updated successfully")
                    else:
                        print("\n No products Found ")



            elif choice == '5':
                cust_id = int(input("Enter customer ID: "))
                products_list = repo.getAllProducts()
                if products_list:
                    print("\nList of Products:")
                    for prod in products_list:
                        print(
                            f"ID: {prod.get_product_id()}, Name: {prod.get_name()}, Price: Rs.{prod.get_price()}, Stock: {prod.get_stockquantity()}")
                    prod_id = int(input("Enter product ID: "))
                    qty = int(input("Enter quantity: "))
                    c = customers(customer_id=cust_id)
                    p = products(product_id=prod_id)
                    if repo.addToCart(c, p, qty):
                        print("\nProduct added to cart")
                else:
                    print("No product!")

            elif choice == '6':
                cust_id = int(input("Enter customer ID: "))
                c = customers(customer_id=cust_id)
                cart_items = repo.getAllFromCart(c)
                for item in cart_items:
                    print(f"{item.get_name()} - Rs. {item.get_price()} ({item.get_stockquantity()} in stock)")

            elif choice == "7":
                cart_id = int(input("Enter Cart ID: "))
                cart = repo.getCartById(cart_id)
                if cart:
                    print(f"Cart ID: {cart['cart_id']}, Customer ID: {cart['customer_id']}, "
                          f"Product: {cart['name']}, Quantity: {cart['quantity']}, "
                          f"Price: {cart['price']}, Description: {cart['description']}")


            elif choice == '8':
                cust_id = int(input("Enter customer ID: "))
                prod_id = int(input("Enter product ID: "))
                c = customers(customer_id=cust_id)
                p = products(product_id=prod_id)
                if repo.removeFromCart(c, p):
                    print("\nProduct removed from cart")

            elif choice == '9':
                cust_id = int(input("Enter customer ID: "))
                c = customers(customer_id=cust_id)
                shipping = input("Enter shipping address: ")
                cart = repo.getAllFromCart(c)
                items = {p: 1 for p in cart}  # assuming 1 qty each for simplicity
                if repo.placeOrder(c, items, shipping):
                    print("\nOrder placed successfully")

            elif choice == '10':
                cust_id = int(input("Enter customer ID: "))
                orders = repo.getOrdersByCustomer(cust_id)
                for o in orders:
                    print(
                        f"Order #{o['order_id']} - {o['product_name']} x {o['quantity']} @ Rs. {o['total_price']} on {o['order_date']}")

            elif choice == '11':
                order_id = int(input("Enter Order ID to view: "))
                order = repo.getOrderById(order_id)
                print(f"\nOrder ID: {order['order_id']}")
                print(f"Customer ID: {order['customer_id']}")
                print(f"Date: {order['order_date']}")
                print(f"Shipping Address: {order['shipping_address']}")
                print(f"Total Price: Rs. {order['total_price']}")
                print("Items:")
                for item in order['items']:
                    print(f" - {item['product_name']} x {item['quantity']} @ Rs. {item['price']}")

            elif choice == '12':
                order_id = int(input("Enter Order ID to cancel: "))
                if repo.cancelOrder(order_id):
                    print("\nOrder cancelled successfully.")

            elif choice == "13":

                cid = int(input("Enter customer ID to delete: "))

                if repo.deleteCustomer(cid):
                    print("\nCustomer deleted successfully")


            elif choice == "14":

                pid = int(input("Enter product ID to delete: "))
                if repo.deleteProduct(pid):
                    print("\nProduct deleted successfully")

            elif choice == '15':
                print("\n=== Thank you for Using ==="
                      "\n=== Visit Again,Goodbye! ===")
                break



            else:
                print("\nInvalid choice !"
                      "\nKindly, Enter the choice from the menu")

        except CustomerNotFoundException:
            print(" Customer not found !")
        except ProductNotFoundException:
            print(" Product not found !")
        except OrderNotFoundException:
            print(" No orders found !")
        except Exception as e:
            print(" Error:",e)

if __name__ == '__main__':
    main()