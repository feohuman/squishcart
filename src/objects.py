import qrcode
import json

class Product:
    def __init__(self, name, price, exp_date):
        self.name = name
        self.price = price
        self.exp_date = exp_date
        self.qr = None

    def create_qr(self):
        name = self.name
        name += ".png"
        qr = qrcode.make(self.name + "\n" + str(self.price) + "\n" + str(self.exp_date))
        qr.save(name)
        self.qr = name

    def jsonify(self):
        return {
            "name": self.name,
            "price": self.price,
            "exp_date": self.exp_date,
            "qr": self.qr.url
        }


class Customer:
