# OrderProcessorRepository interface/abstract class with methods for
# adding/removing products to/from the cart and placing orders.

from abc import ABC, abstractmethod
from Entity.products import products
from Entity.customers import customers

class OderProcessorRespository(ABC):

    @abstractmethod
    def createProduct(self,products:products) -> bool:
        "Creating new product"
        pass

    def createCustomer(self,customers:customers) -> bool:
        "Creating New customer"
        pass

    def deleteProduct(self,product_id:int) ->bool:
        "Deleting the product from the product table"
        pass

    def deleteCustomer(self, customer_id: int, password: str) -> bool:
        "Deleting the customer from teh customer table"
        pass

    def addToCart(self,customers:customers,products:products,quantity: int) -> bool:
        "Adding the product to the cart"
        pass

    def removeFromCart(self, customers: customers, products:products) -> bool:
        "Removing or deleting the product from the cart"
        pass

    def getAllFromCart(self,customers:customers) -> list[products]:
        "Listing all the item or product in the cart for the customer"
        pass

    def placeOrder(self,customers:customers,item:dict[products,int],shippingAddress:str) -> bool:
        "Updating the order table and order_item table by placing the order"
        pass

    def getOrdersByCustomer(self,customer_id) -> list[dict[str,any]]:
        "List of orders and details by the customer"
        pass

    def getAllProducts(self) -> list[products]:
        pass

    def cancelOrder(self, order_id: int) -> bool:
        pass

    def getOrderById(self, order_id: int) -> dict:
        pass

    def getCartById(self, cart_id: int) -> dict:
        pass

    def updateStock(self, product_id: int, new_quantity: int) -> bool:
        pass

    def updateCustomerEmail(self, customer_id: int, password: str, new_email: str) -> bool:
        pass

    def getAllCustomers(self) -> list[customers]:
        pass

    def updateCustomerPassword(self, customer_id: int, current_password: str, new_password: str) -> bool:
        pass

    def updateProductPrice(self, product_id: int, new_price: float) -> bool:
        pass

    def getCustomerById(self, customer_id: int):
        pass

    def updateCart(self, cart_id: int, action: str, quantity: int) -> bool:
        pass

    def removeFromCartByCartId(self, cart_id: int) -> bool:
        pass

    def placeOrder(self, customers: customers, cart_id: int, shippingAddress: str) -> bool:
        pass

    def updateShippingAddress(self, order_id: int, new_address: str) -> bool:
        pass

# Reports

    def getCustomersByProductId(self, product_id: int) -> list[dict]:
        pass

    def getCustomerOrderCounts(self) -> list[dict]:
        pass

    def getProductsWithStock(self) -> list[dict]:
        pass

    def getProductsWithZeroStock(self) -> list[dict]:
        pass

    def getFrequentlyOrderedProducts(self) -> list[dict]:
        pass

    def getProductsNotOrdered(self) -> list[dict]:
        pass

    def getCartsByProductId(self, product_id: int) -> list[dict]:
        pass

    def getOrdersByCustomer(self, customer_id: int) -> list[dict]:
        pass

    def getOrdersByProductId(self, product_id: int) -> list[dict]:
        pass

    def getOrdersByDate(self, order_date: str) -> list[dict]:
        pass

    def getOrdersInDateRange(self, start_date: str, end_date: str) -> list[dict]:
        pass

    def getAllOrders(self) -> list[dict]:
        pass
