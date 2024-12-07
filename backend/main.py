from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models import *
from database import engine, get_db
from auth import verify_password, get_password_hash, create_access_token, verify_token
from datetime import date


# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# OAuth2PasswordBearer is used to get the token from the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

class UserOut(BaseModel):
    id: int
    username: str
    is_admin: int

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    username: str
    password: str
    is_admin: int
    
class LoginRequest(BaseModel):
    username: str
    password: str
    
class ProductCreate(BaseModel):
    name: str
    price: float
    stock: int
    category: str
    expiration_date: date
    
class ProductUpdate(BaseModel):
    name: str
    price: float
    stock: int
    category: str
    expiration_date: date
    
class BasketCreate(BaseModel):
    user_id: int
    
class BasketUpdate(BaseModel):
    user_id: int

class BasketItemCreate(BaseModel):
    basket_id: int
    product_id: int
    quantity: int

class BasketItemUpdate(BaseModel):
    basket_id: int
    product_id: int
    quantity: int
    
class StockUpdate(BaseModel):
    stock: int

@app.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, password=hashed_password, is_admin=user.is_admin)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login")
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer", "is_admin": user.is_admin}

@app.post("/logout")
def logout(token: str = Depends(oauth2_scheme)):
    # JWT doesn't require a server-side logout mechanism, but you can implement blacklisting tokens if needed
    verify_token(token)  # If this line runs without an exception, the token is valid
    return {"msg": "Successfully logged out"}

@app.get("/users/me", response_model=UserOut)
def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = verify_token(token)
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/users/{user_id}", response_model=UserOut)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users", response_model=list[UserOut])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@app.get("/users/{user_id}/basket")
def read_user_basket(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    basket = db.query(Basket).filter(Basket.user_id == user_id).first()
    if not basket:
        raise HTTPException(status_code=404, detail="Basket not found")
    return basket


@app.get("/products")
def read_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    products = db.query(Product).offset(skip).limit(limit).all()
    return products

@app.get("/products/{product_id}")
def read_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.post("/products")
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.name == product.name, Product.expiration_date == product.expiration_date).first()
    if db_product:
        raise HTTPException(status_code=400, detail="Product already registered")
    new_product = Product(**product.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@app.put("/products/{product_id}")
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in product.dict().items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product

# increase stock of a product
@app.put("/products/{product_id}/stock/increase")
def increase_stock(product_id: int, stock: StockUpdate, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db_product.stock += stock.stock
    db.commit()
    db.refresh(db_product)
    return db_product

# decrease stock of a product
@app.put("/products/{product_id}/stock/decrease")
def decrease_stock(product_id: int, stock: StockUpdate, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    if db_product.stock < stock.stock:
        raise HTTPException(status_code=400, detail="Not enough stock available")
    db_product.stock -= stock.stock
    db.commit()
    db.refresh(db_product)
    return db_product

@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    return {"msg": "Product deleted"}

@app.post("/basket")
def create_basket(basket: BasketCreate, db: Session = Depends(get_db)):
    db_basket = db.query(Basket).filter(Basket.user_id == basket.user_id).first()
    if db_basket:
        raise HTTPException(status_code=400, detail="Basket already exists")
    
    if not db.query(User).filter(User.id == basket.user_id).first():
        raise HTTPException(status_code=404, detail="User not found")
    
    new_basket = Basket(**basket.dict())
    db.add(new_basket)
    db.commit()
    db.refresh(new_basket)
    return new_basket

@app.put("/basket/{basket_id}")
def update_basket(basket_id: int, basket: BasketUpdate, db: Session = Depends(get_db)):
    db_basket = db.query(Basket).filter(Basket.id == basket_id).first()
    if not db_basket:
        raise HTTPException(status_code=404, detail="Basket not found")
    for key, value in basket.dict().items():
        setattr(db_basket, key, value)
    db.commit()
    db.refresh(db_basket)
    return db_basket

@app.delete("/basket/{basket_id}")
def delete_basket(basket_id: int, db: Session = Depends(get_db)):
    db_basket = db.query(Basket).filter(Basket.id == basket_id).first()
    if not db_basket:
        raise HTTPException(status_code=404, detail="Basket not found")
    db.delete(db_basket)
    db.commit()
    return {"msg": "Basket deleted"}

@app.post("/basket/{basket_id}/items")
def add_basket_item(basket_id: int, item: BasketItemCreate, db: Session = Depends(get_db)):
    db_basket = db.query(Basket).filter(Basket.id == basket_id).first()
    if not db_basket:
        raise HTTPException(status_code=404, detail="Basket not found")
    db_product = db.query(Product).filter(Product.id == item.product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # check if enough stock is available
    if db_product.stock < item.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock available")
    
    db_product.stock -= item.quantity
    # if item already exists in the basket, update the quantity and total price of basket item and basket
    db_item = db.query(BasketItem).filter(BasketItem.basket_id == basket_id, BasketItem.product_id == item.product_id).first()
    if db_item:
        db_item.quantity += item.quantity
        db_item.total_price += db_product.price * item.quantity
        db_basket.total_price += db_product.price * item.quantity
        db_basket.quantity += item.quantity
        db.commit()
        db.refresh(db_item)
        return db_item
    
    new_item = BasketItem(**item.dict())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@app.put("/basket/{basket_id}/items/{item_id}")
def update_basket_item(basket_id: int, item_id: int, item: BasketItemUpdate, db: Session = Depends(get_db)):
    db_item = db.query(BasketItem).filter(BasketItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    for key, value in item.dict().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/basket/{basket_id}/items/{item_id}")
def delete_basket_item(basket_id: int, item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(BasketItem).filter(BasketItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db_product = db.query(Product).filter(Product.id == db_item.product_id).first()
    db_product.stock += db_item.quantity
    db_basket = db.query(Basket).filter(Basket.id == basket_id).first()
    db_basket.total_price -= db_item.total_price
    db_basket.quantity -= db_item.quantity
    db.delete(db_item)
    db.commit()
    return {"msg": "Item deleted"}

# remove n items from basket (n as link parameter)
@app.put("/basket/{basket_id}/items/{item_id}/remove/{quantity}")
def remove_basket_item(basket_id: int, item_id: int, quantity: int, db: Session = Depends(get_db)):
    db_item = db.query(BasketItem).filter(BasketItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db_product = db.query(Product).filter(Product.id == db_item.product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db_product.stock += quantity
    db_item.quantity -= quantity
    db_item.total_price -= db_product.price * quantity
    db_basket = db.query(Basket).filter(Basket.id == basket_id).first()
    db_basket.total_price -= db_product.price * quantity
    db_basket.quantity -= quantity
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/basket/{basket_id}/items")
def read_basket_items(basket_id: int, db: Session = Depends(get_db)):
    items = db.query(BasketItem).filter(BasketItem.basket_id == basket_id).all()
    return items

@app.get("/basket/{basket_id}/items/{item_id}")
def read_basket_item(basket_id: int, item_id: int, db: Session = Depends(get_db)):
    item = db.query(BasketItem).filter(BasketItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.get("/basket/{basket_id}")
def read_basket(basket_id: int, db: Session = Depends(get_db)):
    basket = db.query(Basket).filter(Basket.id == basket_id).first()
    if not basket:
        raise HTTPException(status_code=404, detail="Basket not found")
    return basket

@app.get("/baskets")
def read_baskets(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    baskets = db.query(Basket).offset(skip).limit(limit).all()
    return baskets