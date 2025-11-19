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

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List

# Example schemas (retain for reference/testing):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# One Piece streaming app schemas

class Episode(BaseModel):
    """
    Episodes collection schema
    Collection name: "episode"
    """
    number: int = Field(..., ge=1, description="Episode number")
    season: int = Field(1, ge=1, description="Season number")
    title: str = Field(..., description="Episode title")
    synopsis: Optional[str] = Field(None, description="Short description of the episode")
    thumbnail_url: Optional[HttpUrl] = Field(None, description="Thumbnail image URL")
    poster_url: Optional[HttpUrl] = Field(None, description="Poster/banner image URL")
    stream_url: Optional[HttpUrl] = Field(None, description="MP4/HLS URL for streaming")
    duration_minutes: Optional[int] = Field(None, ge=1, le=240, description="Length of episode in minutes")
    tags: List[str] = Field(default_factory=list, description="Search tags like characters, arcs")
    is_featured: bool = Field(False, description="Show in featured carousel")

class Collection(BaseModel):
    """
    Collections/Playlists schema
    Collection name: "collection"
    """
    title: str = Field(..., description="Collection title, e.g., East Blue Saga")
    description: Optional[str] = Field(None, description="Collection description")
    episode_ids: List[str] = Field(default_factory=list, description="List of Episode document IDs")
    cover_url: Optional[HttpUrl] = Field(None, description="Cover image URL")
