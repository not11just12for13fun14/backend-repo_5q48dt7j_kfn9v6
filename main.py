import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Product as ProductSchema, Seller as SellerSchema, Order as OrderSchema

app = FastAPI(title="Marketplace API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CreateProduct(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    seller_name: str
    image_url: Optional[str] = None

@app.get("/")
def read_root():
    return {"message": "Marketplace backend running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

@app.post("/api/sellers", response_model=dict)
def create_seller(seller: SellerSchema):
    inserted_id = create_document("seller", seller)
    return {"id": inserted_id}

@app.get("/api/products", response_model=List[dict])
def list_products(category: Optional[str] = None):
    filter_q = {"category": category} if category else {}
    products = get_documents("product", filter_q)
    # Convert ObjectId to string
    for p in products:
        p["_id"] = str(p.get("_id"))
    return products

@app.post("/api/products", response_model=dict)
def create_product(data: CreateProduct):
    payload = ProductSchema(
        title=data.title,
        description=data.description,
        price=data.price,
        category=data.category,
        seller_name=data.seller_name,
        image_url=data.image_url,
        in_stock=True,
    )
    inserted_id = create_document("product", payload)
    return {"id": inserted_id}

class CreateOrder(BaseModel):
    buyer_name: str
    shipping_address: str
    items: List[dict]

@app.post("/api/orders", response_model=dict)
def create_order(order: CreateOrder):
    # Basic validation of items
    if not order.items:
        raise HTTPException(status_code=400, detail="Order must contain at least one item")

    payload = OrderSchema(
        buyer_name=order.buyer_name,
        shipping_address=order.shipping_address,
        items=order.items,  # OrderItem schema will validate
        status="placed",
    )
    inserted_id = create_document("order", payload)
    return {"id": inserted_id}

@app.get("/api/orders", response_model=List[dict])
def list_orders():
    orders = get_documents("order")
    for o in orders:
        o["_id"] = str(o.get("_id"))
    return orders

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
