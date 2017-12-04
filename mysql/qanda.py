from enum import Enum
import abc 

class Vote( Enum ):
  Down = -1
  Up = 1

class User( object ):
  def __init__( self, id = None, email = None, passhash = None ):
    self.id = id
    self.email = email
    self.passhash = passhash

class Question( object ):
  def __init__( self, id = None, text = None ):
    self.id = id
    self.text = text

class Answer( object ):
  def __init__( self, id = None, text = None, up_vote = 0, down_vote = 0 ):
    self.id = id
    self.text = text
    self.up_vote = up_vote
    self.down_vote = down_vote

class Rank( object ):
  # use None for score if there is no rank
  def __init__( self, id = None, score = None ):
    self.id = id
    self.score = score

class QandA( metaclass = abc.ABCMeta ):

  @abc.abstractmethod
  def initialize( self ):
    """make sure database is empty by deleting all existing rows"""
    return 
  
  @abc.abstractmethod
  def user_entity( self ):
    """return an object that implements UserEntity"""
    return 

  @abc.abstractmethod
  def question_entity( self ):
    """return an object that implements QuestionEntity"""
    return 

  @abc.abstractmethod
  def answer_entity( self ):
    """return an object that implements AnswerEntity"""
    return 

class Entity( metaclass = abc.ABCMeta ):

  @abc.abstractmethod
  def initialize( self ):
    """create table for this class if necessary"""
    """delete all rows in the table for this class"""
    return 
  
  @abc.abstractmethod
  def get( self, id ):
    """return object with matching id"""
    """KeyError exception should be thrown if id not found"""
    return  

  @abc.abstractmethod
  def get_all( self ):
    """return all objects in an array"""
    """if no user objects are found, returned array should be empty"""
    return  
    
  @abc.abstractmethod
  def delete( self, id ):
    """delete object with matching id"""
    """KeyError exception should be thrown if id not found"""
    return   

  @abc.abstractmethod
  def rank( self, offset = 0, limit = 10 ):
    """return entity ids in order of their ranking"""
    """offset limits the return to start at the offset-th rank"""
    """limit parameter limits the maximum number of user ids to be returned"""
    return

class UserEntity( Entity ):

  @abc.abstractmethod
  def new( self, email, passhash = None ):
    """create a new instance in db using the given parameters"""
    """unique user id is returned"""
    """if email already exists, KeyError exception will be thrown"""
    return 
    
class QuestionEntity( Entity ):  

  @abc.abstractmethod
  def new( self, user_id, text ):
    """allow a user to pose a question"""
    """unique question id is returned"""
    """KeyError exception should be thrown if user_id not found"""
    return   
    
class AnswerEntity( Entity ):

  @abc.abstractmethod
  def new( self, user_id, question_id, text ):
    """allow a user to answer a question"""
    """unique answer id is returned"""
    """KeyError exception should be thrown if user_id or question_id not found"""
    return   

  @abc.abstractmethod
  def get_answers( self, question_id ):
    """find all answers to a question"""
    """answers are returned as an array of Answer objects"""
    """KeyError exception should be thrown if question_id not found"""
    return     

  @abc.abstractmethod
  def vote( self, user_id, answer_id, vote ):
    """allow a user to vote on a question; vote is of class Vote"""
    """up and down votes are returned as a pair"""
    """KeyError exception should be thrown if user_id or answer_id not found"""
    return   
