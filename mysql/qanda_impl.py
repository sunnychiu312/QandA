import qanda, user_entity_impl, question_entity_impl, answer_entity_impl
import mysql.connector


class QandA_Impl(qanda.QandA):

    def __init__(self):
        self.connect() #initialize connection and cursor
        self.answer_entity_impl = answer_entity_impl.Answer_Entity_Impl(self.cursor)
        self.question_entity_impl = question_entity_impl.Question_Entity_Impl(self.cursor)

        self.user_entity_impl = user_entity_impl.User_Entity_Impl(self.cursor)

    def connect(self):
        self.connection = mysql.connector.connect(user='sunny', password='root',
                              host='127.0.0.1',
                              database='qanda')

        assert self.connection is not None
        self.connection.autocommit = True
        self.connection.set_charset_collation( "utf8mb4", "utf8mb4_bin" )
        self.cursor = self.connection.cursor(buffered=True)

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

    def close_connection( self ):
        self.connection.close()
        return
