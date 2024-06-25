# from datetime import datetime
# from typing import Optional, List
# from pydantic import BaseModel
# from fastapi import FastAPI, HTTPException
# import mysql.connector
# import json
# from fastapi.responses import HTMLResponse
# import pandas as pd

# app = FastAPI()

# def connect():
#     return mysql.connector.connect(
#         host="localhost",
#         user="root",
#         passwd="",
#         database="tests"
#     )

# conn = connect()
# cursor = conn.cursor(dictionary=True)

# def SQLDatetimeNow():
#     return datetime.now().strftime("%Y%m%d%H%M%S")

# class Product(BaseModel):
#     id: Optional[int]
#     sku: Optional[str]
#     name: str
#     price: float
#     description: Optional[str]
#     category: Optional[str]
#     image_base64: Optional[str]
#     review: Optional[str]
#     seller: Optional[str]
#     colors: Optional[List[str]]
#     rate: Optional[float]
#     quantity: Optional[int]
#     available: Optional[bool]
#     title: Optional[str]

# class User(BaseModel):
#     id_card: str
#     worker_number: str

# @app.post("/login")
# def login(user: User):
#     conn = connect()
#     cursor = conn.cursor(dictionary=True)
    
#     query = "SELECT * FROM users WHERE id_card_number = %s AND worker_number = %s"
#     cursor.execute(query, (user.id_card, user.worker_number))
#     result = cursor.fetchone()
    
#     conn.close()

#     if not result:
#         raise HTTPException(status_code=401, detail="Invalid credentials")

#     return {"message": "Login successful", "user": result}

# @app.get("/product")
# def get_products():
#     conn = connect()
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("SELECT * FROM products")
#     result = cursor.fetchall()
#     conn.close()

#     for product in result:
#         if product['colors']:
#             product['colors'] = json.loads(product['colors'])   
#         else:
#             product['colors'] = []
#         product['available'] = bool(product['available'])  # Ensure available is boolean

#     return {"products": result}

# @app.get("/product/{id}")
# def get_product(id: int):
#     conn = connect()
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("SELECT * FROM products WHERE id = %s", (id,))
#     result = cursor.fetchone()
#     conn.close()

#     if result and result['colors']:
#         result['colors'] = json.loads(result['colors'])
#     else:
#         result['colors'] = []

#     if not result:
#         raise HTTPException(status_code=404, detail="Product not found")

#     return {"product": result}

# @app.post("/product", status_code=201)
# def add_product(prod: Product):
#     conn = connect()
#     cursor = conn.cursor(dictionary=True)

#     query = """ 
#     INSERT INTO products (sku, name, price, description, category, image_base64, review, seller, colors, rate, quantity, available, title)
#     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#     """
#     values = (
#         prod.sku, prod.name, prod.price, prod.description, prod.category, prod.image_base64, 
#         prod.review, prod.seller, json.dumps(prod.colors), prod.rate, prod.quantity, prod.available, prod.title
#     )
    
#     cursor.execute(query, values)
#     conn.commit()
#     conn.close()

#     return {"message": "Product added.", "id": cursor.lastrowid}

# @app.put("/product/{id}")
# def update_product(id: int, prod: Product):
#     conn = connect()
#     cursor = conn.cursor(dictionary=True)

#     query = """
#     UPDATE products 
#     SET sku = %s, name = %s, price = %s, description = %s, category = %s, image_base64 = %s, review = %s, seller = %s, colors = %s, rate = %s, quantity = %s, available = %s, title = %s
#     WHERE id = %s
#     """
#     values = (
#         prod.sku, prod.name, prod.price, prod.description, prod.category, prod.image_base64, 
#         prod.review, prod.seller, json.dumps(prod.colors), prod.rate, prod.quantity, prod.available, prod.title, id
#     )

#     cursor.execute(query, values)
#     conn.commit()
#     conn.close()

#     return {"message": "Product updated."}

# @app.delete("/product/{id}")
# def delete_product(id: int):
#     conn = connect()
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("DELETE FROM products WHERE id = %s", (id,))
#     conn.commit()
#     conn.close()

#     return {"message": "Product deleted."}

# class Category(BaseModel):
#     title: str
#     image_base64: str

# @app.get("/categories")
# def get_categories():
#     conn = connect()
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("SELECT * FROM categories")
#     result = cursor.fetchall()
#     conn.close()
    
#     for category in result:
#         category['title'] = category.get('title', 'Unknown Title')  # Default value if title is null
#         category['image'] = category.get('image', 'not images ')  # Default value if image is null
    
#     return {"categories": result}

# class Photo(BaseModel):
#     image_base64: str

# @app.get("/photos")
# def get_photos():
#     conn = connect()
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("SELECT * FROM photos")
#     result = cursor.fetchall()
#     conn.close()
    
#     return {"photos": result}

# # Payment
# class PreSell(BaseModel):
#     id_card_number: str
#     worker_number: str
#     product_name: str
#     product_sku: str
#     quantity: int

# @app.post("/pre-sell", status_code=201)
# def add_pre_sell(pre_sell: PreSell):
#     conn = connect()
#     cursor = conn.cursor(dictionary=True)

#     query = """
#     INSERT INTO pre_sell (id_card_number, worker_number, product_name, product_sku, quantity)
#     VALUES (%s, %s, %s, %s, %s)
#     """
#     values = (
#         pre_sell.id_card_number, pre_sell.worker_number, pre_sell.product_name, pre_sell.product_sku, pre_sell.quantity
#     )
    
#     cursor.execute(query, values)
#     conn.commit()
#     conn.close()

#     return {"message": "Pre-sell record added."}

# @app.get("/products_table", response_class=HTMLResponse)
# def get_products_table():
#     conn = connect()
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("SELECT * FROM products")
#     result = cursor.fetchall()
#     conn.close()

#     # Convert the result to a pandas DataFrame
#     df = pd.DataFrame(result)

#     # Convert the DataFrame to HTML
#     html_table = df.to_html(index=False)

#     return HTMLResponse(content=html_table, status_code=200)



# @app.post("/search_products")
# def search_products(request: dict):
#     user_input = request['request']
#     results = process_user_input(user_input)

#     conn = connect()
#     cursor = conn.cursor(dictionary=True)
    
#     # Construct the SQL query using processed inputs
#     query = """ 
#     SELECT * FROM products 
#     WHERE Key_Words LIKE %s AND price <= %s
#     LIMIT 
#     """
#     values = (f"%{results['final_arb']}%", results['final_price'])
#     cursor.execute(query, values)
    
#     products = cursor.fetchall()
#     conn.close()
    
#     if products:
#         return {"top_products": products}
#     else:
#         raise HTTPException(status_code=404, detail="No matching product found")


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
    