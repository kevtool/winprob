from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from backend.database import db

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_methods=["*"],
    allow_headers=["*"],
)

collection = db["matches"]

@app.get("/api/hello")
def hello():
    return {"message": "Hello from backend!"}


# should optimize this if there are too many matches
@app.get("/api/matches")
def get_matches(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200)
):
    skip = (page - 1) * limit

    cursor = (
        collection
        .find({})
        .sort("date", -1)   # newest first
        .skip(skip)
        .limit(limit)
    )


    matches = []
    for match in cursor:

        match["_id"] = str(match["_id"])
        matches.append(match)

    totalEntries = collection.count_documents({})
    totalPages = (totalEntries + limit - 1) // limit

    return {
        "matches": matches,
        "totalPages": totalPages
    }