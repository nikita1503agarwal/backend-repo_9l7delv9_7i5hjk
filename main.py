import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Episode, Collection

app = FastAPI(title="One Piece Hub API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "One Piece Hub API is running"}

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
            response["database_url"] = "✅ Configured"
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

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

# Helper to convert Mongo _id to string

def serialize_doc(doc: dict):
    if not doc:
        return doc
    d = doc.copy()
    if "_id" in d:
        d["id"] = str(d.pop("_id"))
    return d

# Seed some demo episodes if the collection is empty
@app.post("/seed", tags=["admin"]) 
async def seed_demo():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    count = db["episode"].count_documents({})
    if count > 0:
        return {"seeded": False, "message": "Episodes already exist"}

    demo = [
        {
            "number": 1,
            "season": 1,
            "title": "I'm Luffy! The Man Who's Gonna Be King of the Pirates!",
            "synopsis": "Luffy sets out to sea and meets Coby.",
            "thumbnail_url": "https://images.unsplash.com/photo-1545972152-7051e70f47c9?q=80&w=1200&auto=format&fit=crop",
            "poster_url": "https://images.unsplash.com/photo-1520975922215-2305b8d0b7b6?q=80&w=1600&auto=format&fit=crop",
            "stream_url": "https://www.w3schools.com/html/mov_bbb.mp4",
            "duration_minutes": 24,
            "tags": ["luffy", "east blue"],
            "is_featured": True
        },
        {
            "number": 2,
            "season": 1,
            "title": "Enter the Great Swordsman! Pirate Hunter Roronoa Zoro!",
            "synopsis": "Luffy seeks out the famed swordsman.",
            "thumbnail_url": "https://images.unsplash.com/photo-1612036782180-6f0b6a9a8d2e?q=80&w=1200&auto=format&fit=crop",
            "poster_url": "https://images.unsplash.com/photo-1522199710521-72d69614c702?q=80&w=1600&auto=format&fit=crop",
            "stream_url": "https://www.w3schools.com/html/mov_bbb.mp4",
            "duration_minutes": 24,
            "tags": ["zoro", "east blue"],
            "is_featured": True
        },
        {
            "number": 3,
            "season": 1,
            "title": "Morgan versus Luffy! Who's the Mysterious Beautiful Young Girl?",
            "synopsis": "The Straw Hats face Captain Morgan.",
            "thumbnail_url": "https://images.unsplash.com/photo-1606112219348-204d7d8b94ee?q=80&w=1200&auto=format&fit=crop",
            "poster_url": "https://images.unsplash.com/photo-1520975922215-2305b8d0b7b6?q=80&w=1600&auto=format&fit=crop",
            "stream_url": "https://www.w3schools.com/html/mov_bbb.mp4",
            "duration_minutes": 24,
            "tags": ["nami", "east blue"],
            "is_featured": False
        }
    ]
    db["episode"].insert_many(demo)
    return {"seeded": True, "count": len(demo)}

# Episodes
@app.get("/episodes", response_model=List[Episode])
async def list_episodes(tag: Optional[str] = None, featured: Optional[bool] = None, limit: int = 50):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    query = {}
    if tag:
        query["tags"] = {"$in": [tag]}
    if featured is not None:
        query["is_featured"] = featured
    cursor = db["episode"].find(query).limit(limit)
    items = []
    async for _ in []:  # no async driver; keep sync
        pass
    items = [serialize_doc(d) for d in cursor]
    # Map to Episode model fields (ignore id)
    return [Episode(**{k: v for k, v in d.items() if k != "id"}) for d in items]

@app.get("/episodes/raw")
async def list_episodes_raw(limit: int = 100):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    cursor = db["episode"].find({}).limit(limit)
    return [serialize_doc(d) for d in cursor]

# Collections
@app.get("/collections")
async def list_collections(limit: int = 50):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    cursor = db["collection"].find({}).limit(limit)
    return [serialize_doc(d) for d in cursor]

class CreateCollectionRequest(BaseModel):
    title: str
    description: Optional[str] = None
    episode_ids: List[str] = []
    cover_url: Optional[str] = None

@app.post("/collections")
async def create_collection(payload: CreateCollectionRequest):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    data = payload.dict()
    # Validate episode_ids are valid ObjectId format where present
    valid_ids = []
    for eid in data.get("episode_ids", []):
        try:
            valid_ids.append(str(ObjectId(eid)))
        except Exception:
            continue
    data["episode_ids"] = valid_ids
    inserted_id = create_document("collection", data)
    return {"id": inserted_id}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
