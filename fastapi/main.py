from datetime import datetime
import logging
from typing import Optional, List
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Form, File, UploadFile
import mysql.connector
import json
from fastapi.responses import HTMLResponse
import pandas as pd

import bcrypt
import base64
from fastapi.middleware.cors import CORSMiddleware
from text_processing import process_user_input, final_arb, final_arbz, final_op, final_price

                             

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
logging.basicConfig(level=logging.INFO)

def connect():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="tests"
    )

conn = connect()
cursor = conn.cursor(dictionary=True)

def SQLDatetimeNow():
    return datetime.now().strftime("%Y%m%d%H%M%S")

class Product(BaseModel):
    id: Optional[int]
    sku: Optional[str]
    name: str
    price: float
    description: Optional[str]
    category: Optional[str]
    image_base64: Optional[str]
    review: Optional[str]
    seller: Optional[str]
    colors: Optional[List[str]]
    rate: Optional[float]
    quantity: Optional[int]
    available: Optional[bool]
    title: Optional[str]
    key_words: Optional[str]  # Update the field name to match the database

class User(BaseModel):
    id_card: str            
    worker_number: str

class CreateUser(BaseModel):
    id_card_number: str
    worker_number: str
    name: str
    email: str
    role: str

class UpdateUser(CreateUser):
    id: int

class ProductInput(BaseModel):
    sku: str
    name: str
    price: float
    description: Optional[str]
    category: Optional[str]
    quantity: Optional[int]
    available: Optional[bool]
    Key_Words: Optional[str]
    image_base64: Optional[str]

@app.post("/products", status_code=201)
def add_product(product: ProductInput):
    conn = connect()
    cursor = conn.cursor()
    query = """
    INSERT INTO products (sku, name, price, description, category, quantity, available, Key_Words, image_base64)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        product.sku, product.name, product.price, product.description, product.category, 
        product.quantity, product.available, product.Key_Words, product.image_base64
    )
    cursor.execute(query, values)
    conn.commit()
    conn.close()
    return {"message": "Product added successfully"}

class CategoryInput(BaseModel):
    title: str
    image_base64: Optional[str]

@app.post("/categories", status_code=201)
def add_category(category: CategoryInput):
    conn = connect()
    cursor = conn.cursor()
    query = """
    INSERT INTO categories (title, image_base64)
    VALUES (%s, %s)
    """
    values = (category.title, category.image_base64)
    cursor.execute(query, values)
    conn.commit()
    conn.close()
    return {"message": "Category added successfully"}

@app.put("/products/{id}", status_code=200)
def update_product(id: int, product: ProductInput):
    conn = connect()
    cursor = conn.cursor()
    query = """
    UPDATE products 
    SET sku = %s, name = %s, price = %s, description = %s, category = %s, quantity = %s, 
        available = %s, Key_Words = %s, image_base64 = %s
    WHERE id = %s
    """
    values = (
        product.sku, product.name, product.price, product.description, product.category, 
        product.quantity, product.available, product.Key_Words, product.image_base64, id
    )
    cursor.execute(query, values)
    conn.commit()
    conn.close()
    return {"message": "Product updated successfully"}

@app.delete("/photos/{id}", status_code=204)
def delete_photo(id: int):
    conn = connect()
    cursor = conn.cursor()
    query = "DELETE FROM photos WHERE id = %s"
    cursor.execute(query, (id,))
    conn.commit()
    conn.close()
    return {"message": "Photo deleted successfully"}

@app.delete("/categories/{title}", status_code=204)
def delete_category(title: str):
    conn = connect()
    cursor = conn.cursor()
    query = "DELETE FROM categories WHERE title = %s"
    cursor.execute(query, (title,))
    conn.commit()
    conn.close()
    return {"message": "Category deleted successfully"}

@app.delete("/products/{id}", status_code=204)
def delete_product(id: int):
    conn = connect()
    cursor = conn.cursor()
    query = "DELETE FROM products WHERE id = %s"
    cursor.execute(query, (id,))
    conn.commit()
    conn.close()
    return {"message": "Product deleted successfully"}

class Photo(BaseModel):
    image_base64: str

@app.post("/photos", status_code=201)
def add_photo(photo: Photo):
    conn = connect()
    cursor = conn.cursor()
    query = "INSERT INTO photos (image_base64) VALUES (%s)"
    cursor.execute(query, (photo.image_base64,))
    conn.commit()
    conn.close()
    return {"message": "Photo added successfully"}

@app.get("/photosTest")
def get_photos_test():
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM photos")
    result = cursor.fetchall()
    conn.close()
    return {"photos": result}

@app.post("/login")
def login(user: User):
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM users WHERE id_card_number = %s"
    cursor.execute(query, (user.id_card,))
    result = cursor.fetchone()
    conn.close()
    if not result or not bcrypt.checkpw(user.worker_number.encode('utf-8'), result['worker_number'].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "user": result}

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

@app.post("/addUser")
def add_user(user: CreateUser):
    conn = connect()
    cursor = conn.cursor()
    hashed_worker_number = hash_password(user.worker_number)
    query = """
        INSERT INTO users (id_card_number, worker_number, name, email, role)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (user.id_card_number, hashed_worker_number, user.name, user.email, user.role))
    conn.commit()
    conn.close()
    return {"message": "User added successfully"}

class LoginUser(BaseModel):
    email: str
    worker_number: str

@app.post("/loginDashboard")
def login_dashboard(user: LoginUser):
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM users WHERE email = %s"
    cursor.execute(query, (user.email,))
    result = cursor.fetchone()
    conn.close()
    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not bcrypt.checkpw(user.worker_number.encode('utf-8'), result['worker_number'].encode('utf-8')):
        print("Password verification failed")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "role": result['role']}

@app.put("/orders/confirm/{order_id}")
def confirm_order(order_id: int):
    conn = connect()
    cursor = conn.cursor()
    try:
        query = "UPDATE final_orders SET confirmation = 1 WHERE id = %s"
        cursor.execute(query, (order_id,))
        conn.commit()
        return {"message": "Order confirmed successfully"}
    except mysql.connector.Error as err:
        logging.error(f"Database error: {err}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {err}")
    finally:
        cursor.close()
        conn.close()

@app.delete("/orders/decline/{order_id}")
def decline_order(order_id: int):
    conn = connect()
    cursor = conn.cursor()
    try:
        query = "DELETE FROM final_orders WHERE id = %s"
        cursor.execute(query, (order_id,))
        conn.commit()
        return {"message": "Order declined successfully"}
    except mysql.connector.Error as err:
        logging.error(f"Database error: {err}")
        raise HTTPException(status_code=500, detail="Internal Server Error: {err}")
    finally:
        cursor.close()
        conn.close()

@app.get("/users")
def get_users():
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    result = cursor.fetchall()
    conn.close()
    return result

@app.get("/users/{user_id}")
def get_user(user_id: int):
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    result = cursor.fetchone()
    conn.close()
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return result

@app.put("/users/{user_id}")
def update_user(user_id: int, user: UpdateUser):
    conn = connect()
    cursor = conn.cursor()
    query = """
        UPDATE users
        SET id_card_number = %s, worker_number = %s, name = %s, email = %s, role = %s
        WHERE id = %s
    """
    cursor.execute(query, (user.id_card_number, user.worker_number, user.name, user.email, user.role, user_id))
    conn.commit()
    conn.close()
    return {"message": "User updated successfully"}

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()
    conn.close()
    return {"message": "User deleted successfully"}

@app.get("/product")
def get_products():
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    result = cursor.fetchall()
    conn.close()
    for product in result:
        if product['colors']:
            product['colors'] = json.loads(product['colors'])
        else:
            product['colors'] = []
        product['available'] = bool(product['available'])  # Ensure available is boolean
    return {"products": result}

@app.get("/product/{id}")
def get_product(id: int):
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products WHERE id = %s", (id,))
    result = cursor.fetchone()
    conn.close()
    if result and result['colors']:
        result['colors'] = json.loads(result['colors'])
    else:
        result['colors'] = []
    if not result:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"product": result}

@app.post("/product", status_code=201)
def add_product(prod: Product):
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    query = """ 
    INSERT INTO products (sku, name, price, description, category, image_base64, review, seller, colors, rate, quantity, available, title, Key_Words)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        prod.sku, prod.name, prod.price, prod.description, prod.category, prod.image_base64, 
        prod.review, prod.seller, json.dumps(prod.colors), prod.rate, prod.quantity, prod.available, prod.title, prod.key_words
    )
    cursor.execute(query, values)
    conn.commit()
    conn.close()
    return {"message": "Product added.", "id": cursor.lastrowid}

@app.put("/product/{id}")
def update_product(id: int, prod: Product):
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    query = """
    UPDATE products 
    SET sku = %s, name = %s, price = %s, description = %s, category = %s, image_base64 = %s, review = %s, seller = %s, colors = %s, rate = %s, quantity = %s, available = %s, title = %s, Key_Words = %s
    WHERE id = %s
    """
    values = (
        prod.sku, prod.name, prod.price, prod.description, prod.category, prod.image_base64, 
        prod.review, prod.seller, json.dumps(prod.colors), prod.rate, prod.quantity, prod.available, prod.title, prod.key_words, id
    )
    cursor.execute(query, values)
    conn.commit()
    conn.close()
    return {"message": "Product updated."}

@app.delete("/product/{id}")
def delete_product(id: int):
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("DELETE FROM products WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return {"message": "Product deleted."}

class Category(BaseModel):
    title: str
    image_base64: str

@app.get("/categories")
def get_categories():
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM categories")
    result = cursor.fetchall()
    conn.close()
    for category in result:
        category['title'] = category.get('title', 'Unknown Title')  # Default value if title is null
        category['image'] = category.get('image', 'not images ')  # Default value if image is null
    return {"categories": result}

class Photo(BaseModel):
    image_base64: str

@app.get("/photos")
def get_photos():
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM photos")
    result = cursor.fetchall()
    conn.close()
    return {"photos": result}

class PreSell(BaseModel):
    id_card_number: str
    worker_number: str
    product_name: str
    product_sku: str
    quantity: int

@app.post("/pre-sell", status_code=201)
def add_pre_sell(pre_sell: PreSell):
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    query = """
    INSERT INTO pre_sell (id_card_number, worker_number, product_name, product_sku, quantity)
    VALUES (%s, %s, %s, %s, %s)
    """
    values = (
        pre_sell.id_card_number, pre_sell.worker_number, pre_sell.product_name, pre_sell.product_sku, pre_sell.quantity
    )
    cursor.execute(query, values)
    conn.commit()
    conn.close()
    return {"message": "Pre-sell record added."}

class FinalOrder(BaseModel):
    id: int
    name: str
    address: str
    city: str
    postal_code: str
    phone_number: str
    user_id_card: str
    product_skus: List[str]
    product_quantities: List[int]
    product_categories: List[str]
    facilite: List[int]
    total_price: float
    payment_method: Optional[str] = None    

class FinalOrders(BaseModel):
    name: str
    address: str
    city: str
    postal_code: str
    phone_number: str
    user_id_card: str
    product_skus: List[str]
    product_quantities: List[int]
    product_categories: List[str]
    facilite: List[int]
    total_price: float
    payment_method: Optional[str] = None 

@app.get("/orders", response_model=List[FinalOrder])
def get_unconfirmed_orders():
    try:
        conn = connect()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM final_orders WHERE confirmation = 0"
        cursor.execute(query)
        result = cursor.fetchall()
        for order in result:
            order['product_skus'] = json.loads(order['product_skus']) if order['product_skus'] else []
            order['facilite'] = json.loads(order['facilite']) if order['facilite'] else []
            order['product_quantities'] = json.loads(order['product_quantities']) if order['product_quantities'] else []
            order['product_categories'] = json.loads(order['product_categories']) if order['product_categories'] else []
        conn.close()
        return result
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/orderss", response_model=List[FinalOrder])
def get_confirmed_orders():
    try:
        conn = connect()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM final_orders WHERE confirmation = 1"
        cursor.execute(query)
        result = cursor.fetchall()
        for order in result:
            order['product_skus'] = json.loads(order['product_skus']) if order['product_skus'] else []
            order['facilite'] = json.loads(order['facilite']) if order['facilite'] else []
            order['product_quantities'] = json.loads(order['product_quantities']) if order['product_quantities'] else []
            order['product_categories'] = json.loads(order['product_categories']) if order['product_categories'] else []
        conn.close()
        return result
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/final-order", status_code=201)
def add_final_order(final_order: FinalOrders):
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    query = """
    INSERT INTO final_orders (name, address, city, postal_code, phone_number, user_id_card, product_skus, product_quantities, product_categories, facilite, total_price, confirmation)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    confirmation = final_order.payment_method == "cash_on_delivery"
    values = (
        final_order.name, final_order.address, final_order.city, final_order.postal_code, final_order.phone_number,
        final_order.user_id_card, json.dumps(final_order.product_skus), json.dumps(final_order.product_quantities),
        json.dumps(final_order.product_categories), json.dumps(final_order.facilite), final_order.total_price, confirmation
    )
    cursor.execute(query, values)
    conn.commit()
    conn.close()
    return {"message": "Final order added."}

@app.get("/products_table", response_class=HTMLResponse)
def get_products_table():
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT name, price, description, category FROM products")
    result = cursor.fetchall()
    conn.close()
    df = pd.DataFrame(result)
    html_table = df.to_html(index=False)
    return HTMLResponse(content=html_table, status_code=200)

@app.post("/search_products")
def search_products(request: dict):
    user_input = request['request']
    results = process_user_input(user_input)

    conn = connect()
    cursor = conn.cursor(dictionary=True)
    
    # Construct the SQL query based on whether final_arbz has a value
    if results['final_arbz']:
        query = """ 
        SELECT * FROM products 
        WHERE Key_Words LIKE %s AND (description LIKE %s OR name LIKE %s) AND price <= %s 
        LIMIT 3
        """
        values = (f"%{results['final_arb']}%", f"%{results['final_arbz']}%", f"%{results['final_arbz']}%", results['final_price'])
    else:
        query = """ 
        SELECT * FROM products 
        WHERE Key_Words LIKE %s AND price <= %s
        LIMIT 3
        """
        values = (f"%{results['final_arb']}%", results['final_price'])

    cursor.execute(query, values)
    
    products = cursor.fetchall()
    conn.close()
    
    if products:
        return {"top_products": products}
    else:
        raise HTTPException(status_code=404, detail="No matching product found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
