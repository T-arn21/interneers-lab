from mongoengine import connect

def initialize_db():
    connect(
        db="mydb",  # database name
        host="localhost",
        port=27017
    )