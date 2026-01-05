from bson import ObjectId
from backend.database import db
from pymongo.errors import BulkWriteError
from pymongo import UpdateOne


collection = db["matches"]
collection.create_index("event_id", unique=True)

def create_match(match: dict):
    result = collection.insert_one(match)
    return str(result.inserted_id)

# def create_matches(matches: list[dict]):
#     try:
#         result = collection.insert_many(matches, ordered=False)
#         return [str(_id) for _id in result.inserted_ids]
#     except BulkWriteError as e:
#         # Extract successfully inserted IDs
#         return []


def create_matches(matches: list[dict]):
    """
    Bulk insert or update matches based on event_id.
    Returns a list of inserted_ids for newly created documents.
    """
    operations = [
        UpdateOne(
            {"event_id": match["event_id"]},  # filter
            {"$set": match},                  # update data
            upsert=True                        # insert if not exists
        )
        for match in matches
    ]

    inserted_ids = []
    try:
        result = collection.bulk_write(operations, ordered=False)
        # bulk_write does not return inserted_ids for existing documents
        if hasattr(result, 'upserted_ids'):
            # result.upserted_ids is a dict: index -> ObjectId
            inserted_ids = [str(_id) for _id in result.upserted_ids.values()]
    except BulkWriteError as e:
        # Handle write errors if needed
        print("Bulk write error:", e.details)
    
    return inserted_ids

def get_match_by_event_id(event_id):
    return collection.find_one({"event_id": event_id})

def get_stats():
    pipeline = [
        {
            "$group": {
                "_id": None,
                "total": {"$sum": "$EW"}
            }
        }
    ]

    result = list(collection.aggregate(pipeline))

    total_sum = result[0]["total"] if result else 0
    print(total_sum)