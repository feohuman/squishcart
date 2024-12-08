import qrcode
import json

class User:
    def __init__(self, id, username, password, is_admin, basket, history):
        self.id = id
        self.username = username
        self.password = password
        self.is_admin = is_admin
        self.history = history


class Product:
    def __init__(self, name, quantity, price=0, expiration_date=None):
        self.name = name
        self.quantity = quantity
        self.qr = None
        self.price = price
        self.expiration_date = expiration_date

    def create_qr(self):
        name = self.name
        name += ".png"
        qr = qrcode.make(self.name + "\n" + str(self.price) + "\n" + str(self.expiration_date))
        qr.save(name)
        self.qr = name

    def jsonify(self):
        return {
            "name": self.name,
            "quantity": self.quantity,
            "price": self.price,
            "expiration_date": self.expiration_date
        }

class Basket:
    def __init__(self, id, user_id, quantity=0, total_price=0):
        self.id = id
        self.user_id = user_id
        self.quantity = quantity
        self.total_price = total_price

class BasketItem:
    def __init__(self, id, basket_id, product_id, quantity=0, total_price=0):
        self.id = id
        self.basket_id = basket_id
        self.product_id = product_id
        self.quantity = quantity
        self.total_price = total_price


class Recipe:
    def __init__(self, name, items, instructions):
        self.name = name
        self.items = items
        self.instructions = instructions

