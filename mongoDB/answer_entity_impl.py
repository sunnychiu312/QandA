import qanda
import pymongo
import uuid
from pprint import pprint

class Answer_Entity_Impl(qanda.AnswerEntity):

    def __init__(self, db):
        self.db = db

    def initialize( self ):
        self.db.question.delete_many( { "answer" : {"$elemMatch": { "_id": { "$exists" : True } } } } )

    def doc_to_ansObj(self, cursor):
        answers = []
        for entry in cursor:
            for i in range(len(entry["answer"])):
                id = entry["answer"][i]["_id"]
                body = entry["answer"][i]["text"]

                votes = entry["answer"][i]["vote"]
                vote_tally = self.vote_tally(votes)

                up_vote = vote_tally[0]
                down_vote = vote_tally[1]
                answer = qanda.Answer(id,body, up_vote, down_vote)
                answers.append(answer)
        return answers

    def vote_tally(self, votes):
        up_vote = 0
        down_vote = 0
        for vote in votes:
            if vote["num"] == 1:
                up_vote += vote["num"]
            else:
                down_vote += vote["num"]
        return (up_vote, down_vote)


    def get( self, id ):
        count = self.db.question.find({ "answer" : {"$elemMatch": { "_id": id } } }).count()

        if count == 1:
            cursor = self.db.question.find({ "answer" : {"$elemMatch": { "_id": id } } })
            return self.doc_to_AnsObj(cursor)
        else:
            raise KeyError

    def get_all( self ):
        cursor = self.db.question.find({ "answer" : {"$elemMatch": { "_id": { "$exists" : True } } } } )
        return self.doc_to_ansObj(cursor)


    def delete( self, id ):
        cursor = self.db.question.find({ "answer" : {"$elemMatch": { "_id": id } } })
        count = 0
        user_id = ""

        for answer in cursor:
            user_id =answer["answer"][0]["uid"]
            count += 1

        if count == 1:
            self.db.question.update({ "answer" : {"$elemMatch": { "_id": id } } },
                {"$pull":{ "answer": {"$elemMatch": { "_id": id } }}}
                )
            self.dec_user_score(user_id)
        else:
            raise KeyError

    def dec_user_score(self, uid):
        self.db.user.update_one(
            { "_id" : uid},
            { "$inc": { "score": -1 }},
            True
            )

    def rank( self, offset = 0, limit = 10 ):
        pipeline = [
            { "$unwind": { "path" : "$answer"}},

            { "$unwind": { "path" : "$answer.vote", "preserveNullAndEmptyArrays" : True}},

            { "$group": { "_id" : "$answer._id", "score" : { "$sum" : "$answer.vote.num" }}},

            { "$project":
                  {"_id": 1,
                    "score": {"$cond": { "if": {"$and":[
                                {"$eq":["$score", 0]},
                                {"$not":{"$gt": ["$answer.vote", None]}}
                            ]}, "then": None, "else": "$score"  }
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
            score = document["score"]
            rank = qanda.Rank(id, score)
            ranks.append(rank)
        return ranks


    def new( self, user_id, question_id, text ):
        user_count = self.db.user.find({"_id": user_id}).count()

        cursor = self.db.question.find({"_id": question_id})
        question_count = 0
        quid = ""
        for question in cursor:
            quid = question["uid"]
            question_count += 1

        if user_count != 0 and question_count != 0:
            self.inc_user_score(user_id,quid)
            unique_id = uuid.uuid4()
            while unique_id == 0: #unique id can never be 0
                 unique_id = uuid.uuid4()
            answer = {"_id": unique_id, "uid": user_id, "text": text, "vote": []}
            self.db.question.update_one(
                {"_id": question_id},
                { "$addToSet":{ "answer": answer }}
                )
        else:
            raise KeyError

    def inc_user_score(self, uid, quid):
        if uid != quid:
            self.db.user.update_one(
                { "_id" : uid},
                { "$inc": { "score": 1 }},
                True
                )

    def get_answers( self, question_id ):
        count = self.db.question.find({"_id": question_id}).count()
        if count == 1:
            cursor = self.db.question.find({"_id": question_id})
            return self.doc_to_ansObj(cursor)
        else:
            raise KeyError

    def vote( self, user_id, answer_id, vote ):
        user_count = self.db.user.find({"_id": user_id}).count()
        answer_count = self.db.question.find({ "answer" : {"$elemMatch": { "_id": answer_id } } }).count()

        if user_count == 1 and answer_count ==1:
            user_vote = {"_id": user_id, "num": vote.value}
            self.db.question.update_one(
                {"answer" : {"$elemMatch": { "_id": answer_id } }},
                { "$push":{ "answer.$.vote": user_vote }}
                )
        else:
            raise KeyError
