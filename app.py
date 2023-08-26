from fastapi import FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import mysql.connector

app = FastAPI()

# Dummy cart data
cart = []

# Initialize database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="hmcharsh42",
    database="pandeyji_eatery"
)

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="templates")

@app.on_event("shutdown")
def close_db_connection():
    db.close()

@app.post("/add_to_cart")
async def add_to_cart(item_id: int = Form(...), quantity: int = Form(...)):
    cursor = db.cursor()
    cursor.execute("SELECT name, price FROM food_items WHERE item_id = %s", (item_id,))
    item = cursor.fetchone()

    if item:
        total_price = item[1] * quantity
        cart.append({"item_id": item_id, "name": item[0], "quantity": quantity, "price": item[1], "total_price": total_price})
        cursor.close()
        return {"message": "Item added to cart"}

    cursor.close()
    return {"message": "Item not found"}

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM food_items")
    menu_items = cursor.fetchall()
    cursor.close()

    return templates.TemplateResponse("home.html", {"request": request, "cart": cart, "menu_items": menu_items})

@app.get("/cart", response_class=HTMLResponse)
async def view_cart(request: Request):
    total_price = sum(item["total_price"] for item in cart)
    return templates.TemplateResponse("cart.html", {"request": request, "cart": cart, "total_price": total_price})
