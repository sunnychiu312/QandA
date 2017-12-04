import qanda
import uuid

class Question_Entity_Impl(qanda.QuestionEntity):

    def __init__(self, db):
        self.db = db
        db["question"]

    def initialize( self ):
        self.db.question.delete_many({})

    def doc_to_QuestObj(self, cursor):
        questions = []
        for entry in cursor:
            id = entry["_id"]
            text = entry["text"]
            question = qanda.Question( id, text )
            questions.append(question)
        return questions

    def get( self, id ):
        cursor = self.db.question.find({"_id": id})
        count = 0
        for question in cursor:
            count += 1
        if count == 1:
            cursor = self.db.question.find({"_id": id})
            return self.doc_to_QuestObj(cursor)
        else:
            raise KeyError

    def get_all( self ):
        cursor = self.db.question.find()
        return self.doc_to_QuestObj(cursor)

    def delete( self, id ):
        cursor = self.db.question.find({"_id": id})
        count = 0
        user_ids = []
        for question in cursor:
            for i in range(len(question["answer"])):
                user_ids.append(question["answer"][i]["uid"])
            count += 1
        if count == 1:
            self.db.question.delete_one({"_id": id})
            self.dec_user_score(user_ids)
        else:
            raise KeyError
        return

    def dec_user_score(self, user_ids):
        for user in user_ids:
            self.db.user.update_one(
                { "_id" : user},
                { "$inc": { "score": -1 }},
                True
                )

    def rank( self, offset = 0, limit = 10 ):
        pipeline = [
            { "$unwind": {"path":"$answer", "preserveNullAndEmptyArrays": True}},

            { "$group": {
                "_id" : "$_id",
                "score" : {"$sum" : 1},
                "answer": {"$first": "$answer"}
            }},

            { "$project":
                  {"_id": 1,
                    "score": { "$cond" : { "if" :{ "$and" : [
                                {"$eq" :["$score", 1]},
                                {"$not" :{ "$gt" : ["$answer", None] }}
                            ]}, "then": 0, "else": "$score"  }
                            }
                  }
            },

            { "$sort": { "score": -1 }},

            { "$skip": offset },

            { "$limit": limit }
            ]

        cursor = self.db.question.aggregate(pipeline)
        ranks = []
        for document in cursor:
            id = document["_id"]
            score = 0
            score = document["score"]
            rank = qanda.Rank(id, score)
            ranks.append(rank)
        return ranks

    def new( self, user_id, text ):
        count = self.db.user.find({"_id": user_id}).count()
        if count == 1:
            unique_id = uuid.uuid4()
            while unique_id == 0:
                 unique_id = uuid.uuid4()
            question = { "_id": unique_id, "uid": user_id, "text": text}
            self.db.question.insert_one(question)
        else:
            raise KeyError
