from mongoengine import connect

def initialize_db():
    connect(
        db="mydb",
        host="localhost",
        port=27017
    )