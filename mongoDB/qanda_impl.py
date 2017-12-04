import qanda, user_entity_impl, question_entity_impl, answer_entity_impl
from pymongo import MongoClient


class QandA_Impl(qanda.QandA):

    def __init__(self):
        self.connection()
        self.question_entity_impl = question_entity_impl.Question_Entity_Impl(self.db)
        self.answer_entity_impl = answer_entity_impl.Answer_Entity_Impl(self.db)
        self.user_entity_impl = user_entity_impl.User_Entity_Impl(self.db)

    def connection(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['qanda']

    def initialize( self ):
        self.user_entity_impl.initialize()
        self.question_entity_impl.initialize()
        self.answer_entity_impl.initialize()

    def user_entity( self ):
        """return an object that implements UserEntity"""
        return self.user_entity_impl

    def question_entity( self ):
        """return an object that implements QuestionEntity"""
        return self.question_entity_impl

    def answer_entity( self ):
        """return an object that implements AnswerEntity"""
        return self.answer_entity_impl
