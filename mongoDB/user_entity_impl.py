import qanda
import uuid

class User_Entity_Impl(qanda.UserEntity):

    def __init__(self, db):
        self.db = db
        db["user"]

    def initialize( self ):
        self.db.user.delete_many({})

    def doc_to_userObj(self, cursor):
        users = []
        for entry in cursor:
            id = entry["_id"]
            email = entry["email"]
            password = entry["password"]
            user = qanda.User( id, email, password)
            users.append(user)
        return users

    def get( self, id ):
        cursor = self.db.user.find({"_id": id})
        count = 0
        for user in cursor:
            count += 1
        if count == 1:
            cursor = self.db.user.find({"_id": id})
            return self.doc_to_userObj(cursor)
        else:
            raise KeyError

    def get_all( self ):
        cursor = self.db.user.find()
        return self.doc_to_userObj(cursor)

    def delete( self, id ):
        count = self.db.user.find({"_id": id}).count()
        if count == 1:
            self.db.user.delete_one({"_id": id})
        else:
            raise KeyError

    def rank( self, offset = 0, limit = 10 ):
        pipeline = [
            { "$project":
                  {"_id": 1,
                    "score": {"$cond": { "if":
                            {"$not":{"$gt": ["$score", None]}},
                            "then": None, "else": "$score"  }
                             }
                  }
            },

            { "$sort": { "score": -1 }},

            { "$skip": offset },

            { "$limit": limit }
        ]

        cursor = self.db.user.aggregate(pipeline)
        ranks = []
        for document in cursor:
            id = document["_id"]
            score = document["score"]
            rank = qanda.Rank(id, score)
            ranks.append(rank)
        return ranks

    def new( self, email, passhash = None ):
        count = self.db.user.find({"email": email}).count()
        if count == 0:
            unique_id = uuid.uuid4()
            while unique_id == 0:
                 unique_id = uuid.uuid4()
            user = { "_id": unique_id, "email": email, "password": passhash}
            self.db.user.insert_one(user)
        else:
            raise KeyError
