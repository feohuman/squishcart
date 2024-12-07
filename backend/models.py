from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    is_admin = Column(Integer, default=0)
    
    
class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float, default=0)
    stock = Column(Integer, default=0)
    category = Column(String)
    expiration_date = Column(Date)
    
class Basket(Base):
    __tablename__ = "basket"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    quantity = Column(Integer, default=0)
    total_price = Column(Float, default=0)
    
class BasketItem(Base):
    __tablename__ = "basket_items"
    
    id = Column(Integer, primary_key=True, index=True)
    basket_id = Column(Integer, ForeignKey("basket.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=0)
    total_price = Column(Float, default=0)
    
