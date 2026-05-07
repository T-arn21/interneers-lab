from pymongo import MongoClient

def run_migration():
    client = MongoClient("mongodb://root:example@localhost:27019/admin")
    db = client["interneers_lab"]
    collection = db["products"]

    cursor = collection.find({"category_ref": {"$exists": True}})
    count = 0
    for doc in cursor:
        old_ref = doc.get("category_ref")
        if old_ref:
            collection.update_one(
                {"_id": doc["_id"]},
                {
                    "$set": {"categories_ref": [old_ref]},
                    "$unset": {"category_ref": ""}
                }
            )
            count += 1
        else:
            collection.update_one(
                {"_id": doc["_id"]},
                {
                    "$set": {"categories_ref": []},
                    "$unset": {"category_ref": ""}
                }
            )
            count += 1
            
    print(f"Migration completed. Updated {count} product documents.")

if __name__ == "__main__":
    run_migration()
