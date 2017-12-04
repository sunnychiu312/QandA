# to run this test, execute the command "python3 -m unittest -v <this file>"
import pprint, random, string, unittest
import qanda, qanda_impl # implementation of QandA

n_questions = 100
n_answers = 5 * n_questions
n_emails = int( n_questions / 10 )
domains = [ "@gmail.com", "@icloud.com", "@yahoo.com", "@msn.com" ]
emails = [ "{0}{1}{2}".format( "u", i, random.choice( domains ) ) \
  for i in range( 0, n_emails ) ]

def random_text( ):
  # generate a random string from printable characters that is between 10 and 255
  # characters long
  n_chars = random.randint( 10, 255 )
  return "".join( [ random.choice( string.printable ) for i in range( n_chars ) ] )

class TestQandA( unittest.TestCase ):

  # setUp will be called by the test framework before every test
  def setUp ( self ):
    self.qanda = qanda_impl.QandA_Impl( )
    self.user_entity = self.qanda.user_entity( )
    self.question_entity = self.qanda.question_entity( )
    self.answer_entity = self.qanda.answer_entity( )
    pass

  # setUp will be called by the test framework after every test
  def tearDown( self ):
    pass

  # each test must be self-contained and cannot depend on another
  # tests are executed in lexical order
  def test_01_populate_user( self ):
    self.qanda.initialize( )
    uids = [ self.user_entity.new( email ) for email in emails ]
    users = self.user_entity.get_all( )
    self.assertEqual( len( users ), len( emails ) )

  def test_02_populate_question( self ):
    users = self.user_entity.get_all( )
    howmany = int( n_questions / n_emails )
    for user in users:
      [ self.question_entity.new( user.id, random_text( ) ) for i in range( howmany ) ]
    questions = self.question_entity.get_all( )
    self.assertEqual( len( questions ), n_questions )

  def test_03_populate_answers( self ):
    u_ids = [ user.id for user in self.user_entity.get_all( ) ]
    q_ids = [ question.id for question in self.question_entity.get_all( ) ]
    for i in range( n_answers ):
      self.answer_entity.new( random.choice( u_ids ), random.choice( q_ids ), \
        random_text( ) )
    answers = self.answer_entity.get_all( )
    self.assertEqual( len( answers ), n_answers )

  def test_04_rank_questions( self ):
    batch = int( n_questions / 5 )
    ranks = [ ]
    for i in range( 0, n_questions, batch ):
      ranks = ranks + self.question_entity.rank( i, batch )
    scores = [ r.score for r in ranks ]
    self.assertTrue( sum( scores ) == n_answers and len( scores ) == n_questions )
    self.assertEqual( sorted( scores, reverse = True ), scores )
    # test questions that have not been answered and confirm they receive a rank of 0
    u_ids = [ user.id for user in self.user_entity.get_all( ) ]
    qid = self.question_entity.new( u_ids[0], random_text( ) )
    ranks = self.question_entity.rank( len( scores ), batch )
    self.assertTrue( len( ranks ) == 1 and ranks[0].score == 0 )

  def test_05_rank_answers( self ):
    # vote randomly first
    u_ids = [ user.id for user in self.user_entity.get_all( ) ]
    aids = [ answer.id for answer in self.answer_entity.get_all( ) ]
    # each user is to vote 40 times randomly
    aggregate_score = 0
    n_samples= 40
    for uid in u_ids:
      aids_sample = random.sample( aids, n_samples )
      for i in range( n_samples ):
        # make up vote twice as likely as down vote
        v = random.choice( ( qanda.Vote.Up, qanda.Vote.Up, qanda.Vote.Down ) )
        self.answer_entity.vote( uid, aids_sample[ i ], v )
        aggregate_score += v.value
    # rank answers by the difference of Up and Down votes
    batch = int( n_answers / 50 )
    ranks = [ ]
    for i in range( 0, n_answers, batch ):
      ranks = ranks + self.answer_entity.rank( i, batch )
    scores = [ r.score for r in ranks ]
    self.assertTrue( len( scores ) == len( aids ) )
    # scores may contain null scores which are not acceptable to sort or sum function
    real_scores = [ s for s in scores if s is not None ]
    self.assertTrue( sum( real_scores ) == aggregate_score )
    self.assertEqual( sorted( real_scores, reverse = True ), real_scores )

  def test_06_rank_users( self ):
    ranks = self.user_entity.rank( 0, n_emails )
    scores = [ r.score for r in ranks ]
    # scores may contain null scores which are not acceptable to sort or sum function
    real_scores = [ s for s in scores if s is not None ]
    self.assertTrue( len( real_scores ) == n_emails )
    self.assertEqual( sorted( real_scores, reverse = True ), real_scores )
    # add a new user and verify the score of this new user
    self.user_entity.new( "new@abc.biz" )
    ranks = self.user_entity.rank( n_emails, 1 )
    self.assertTrue( len( ranks ) == 1 and ranks[0].score is None )
