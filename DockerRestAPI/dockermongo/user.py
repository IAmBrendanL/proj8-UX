import pymongo
from flask_login import UserMixin
from Auth.password import verify_password, hash_password
from bson.objectid import ObjectId

client = pymongo.MongoClient("db", 27017)
db = client.btimes


class User(UserMixin):
    '''
    Represents a user
    Defaults implementations of the required instance methods suffice
    '''

    def __init__(self, name, id):
        self.id = id
        self.name = name

    @staticmethod
    def validate_user(username, password):
        """
        Class method, takes in a username and password
        returns a new User instance if the user exists in
        the database, else None
        """
        if username:
            user = db.users.find_one({"username": username})
            if user and password and verify_password(password, user["password_hash"]):
                return User(name=user["username"], id=user["_id"])
        return None

    @staticmethod
    def get_user_by_id(id):
        if id:
            user = db.users.find_one({"_id": ObjectId(id)})
            return User(name=user["username"], id=user["_id"]) if user else None
        return None

    @staticmethod
    def register_user(username, password):
        """
        Class method, registers a new user if the username does not exist
        else, creates a new user with username and password
        """
        if not username or not password:
            return None
        elif db.users.find_one({"username": username}):
            return None
        else:
            id = db.users.insert_one({"username": username, "password_hash": hash_password(password)}).inserted_id
            return User.get_user_by_id(id)

