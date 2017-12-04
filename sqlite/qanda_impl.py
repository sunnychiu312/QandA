import qanda, user_entity_impl, question_entity_impl, answer_entity_impl
import sqlite3


class QandA_Impl(qanda.QandA):

    def __init__(self):
        self.connect() #initialize connection and cursor

    def connect(self):
        db_file = 'qanda.db'
        self.connection = sqlite3.connect(db_file, isolation_level=None)
        assert self.connection is not None
        self.cursor = self.connection.cursor()

    def initialize( self ):
        """Create all tables and delete all data"""
        user_entity_impl.User_Entity_Impl.initialize(self)
        question_entity_impl.Question_Entity_Impl.initialize(self)
        answer_entity_impl.Answer_Entity_Impl.initialize(self)

    def user_entity( self ):
        """return an object that implements UserEntity"""
        return user_entity_impl.User_Entity_Impl(self.cursor)

    def question_entity( self ):
        """return an object that implements QuestionEntity"""
        return question_entity_impl.Question_Entity_Impl(self.cursor)


    def answer_entity( self ):
        """return an object that implements AnswerEntity"""
        return answer_entity_impl.Answer_Entity_Impl(self.cursor)
