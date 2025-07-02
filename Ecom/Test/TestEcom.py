import unittest
from Dao.OrderProcessorRepositoryImpl import OrderProcesserRepositoryimpl
from Entity.customers import customers
from Entity.products import products
from Exception.custom_exceptions import CustomerNotFoundException, ProductNotFoundException
from Util.db_connection import DBconnection

class TestEcommerceSystem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.repo = OrderProcesserRepositoryimpl()
        cls.test_customer = customers(name="UnitTestCustomer", email="unittest@example.com", password="password123")
        cls.test_product = products(name="UnitTestProduct", price=100.0, description="TestDesc", stockquantity=20)

        cls.repo.createCustomer(cls.test_customer)
        cls.repo.createProduct(cls.test_product)

        conn = DBconnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT customer_id FROM customers WHERE email = 'unittest@example.com'")
        cls.test_customer.set_customer_id(cursor.fetchone()["customer_id"])
        cursor.execute("SELECT product_id FROM products WHERE name = 'UnitTestProduct'")
        cls.test_product.set_product_id(cursor.fetchone()["product_id"])
        cursor.close()

    def test_create_customer_success(self):
        c = customers(name="CustomerX", email="x@test.com", password="Xyz@1234")
        self.assertTrue(self.repo.createCustomer(c))

    def test_create_product_success(self):
        p = products(name="ProductX", price=80.0, description="Product X", stockquantity=10)
        self.assertTrue(self.repo.createProduct(p))

    def test_add_to_cart_with_valid_stock(self):
        result = self.repo.addToCart(self.test_customer, self.test_product, 1)
        self.assertTrue(result)

    def test_add_to_cart_with_excess_quantity(self):
        result = self.repo.addToCart(self.test_customer, self.test_product, 9999)
        self.assertFalse(result)



    def test_get_all_customers(self):
        customers_list = self.repo.getAllCustomers()
        self.assertIsInstance(customers_list, list)

    def test_get_all_products(self):
        products_list = self.repo.getAllProducts()
        self.assertIsInstance(products_list, list)

    def test_delete_customer_invalid(self):
        with self.assertRaises(CustomerNotFoundException):
            self.repo.deleteCustomer(999999,"password123")

    def test_delete_product_invalid(self):
        with self.assertRaises(ProductNotFoundException):
            self.repo.deleteProduct(999999)

    @classmethod
    def tearDownClass(cls):
        conn = DBconnection.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cart WHERE customer_id = %s", (cls.test_customer.get_customer_id(),))
        cursor.execute("DELETE FROM order_items WHERE product_id = %s", (cls.test_product.get_product_id(),))
        cursor.execute("DELETE FROM orders WHERE customer_id = %s", (cls.test_customer.get_customer_id(),))
        cursor.execute("DELETE FROM customers WHERE email LIKE 'unittest@example.com' OR email LIKE 'x@test.com'")
        cursor.execute("DELETE FROM products WHERE name LIKE 'UnitTestProduct' OR name LIKE 'ProductX'")
        conn.commit()
        cursor.close()

if __name__ == '__main__':
    unittest.main()
