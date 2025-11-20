"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

# Core marketplace schemas

class Seller(BaseModel):
    """
    Sellers collection schema
    Collection name: "seller"
    """
    name: str = Field(..., description="Seller display name")
    email: Optional[str] = Field(None, description="Contact email")
    address: Optional[str] = Field(None, description="Business address")
    is_active: bool = Field(True, description="Whether seller account is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product"
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")
    seller_name: str = Field(..., description="Name of the seller offering this product")
    image_url: Optional[str] = Field(None, description="Public image URL of the product")

class OrderItem(BaseModel):
    product_id: str = Field(..., description="Product _id as string")
    quantity: int = Field(1, ge=1, description="Quantity of the product")

class Order(BaseModel):
    """
    Orders collection schema
    Collection name: "order"
    """
    buyer_name: str = Field(..., description="Name of the buyer")
    shipping_address: str = Field(..., description="Shipping address")
    items: List[OrderItem] = Field(..., description="Products purchased in this order")
    status: str = Field("placed", description="Order status")

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
