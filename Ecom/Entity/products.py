
class products:
    def __init__(self,product_id=None,name='',price=0.0,description='',stockquantity=0):
        self.__product_id=product_id
        self.__name=name
        self.__price=price
        self.__description=description
        self.__stockquantity=stockquantity

    # getters
    def get_product_id(self):
        return self.__product_id

    def get_name(self):
        return self.__name

    def get_price(self):
        return self.__price

    def get_description(self):
        return self.__description

    def get_stockquantity(self):
        return self.__stockquantity

    # setters
    def set_product_id(self,product_id):
        self.__product_id=product_id

    def set_name(self,name):
        self.__name=name

    def set_price(self,price):
        self.__price=price

    def set_description(self,description):
        self.__description=description

    def set_stock_quantity(self,stockquantity):
        self.__stockquantity=stockquantity


