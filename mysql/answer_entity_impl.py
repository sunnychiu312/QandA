import qanda
import mysql
import uuid

class Answer_Entity_Impl(qanda.AnswerEntity):

    def __init__(self, cursor):
        self.cursor = cursor

        stmt =  """CREATE TABLE IF NOT EXISTS answer
        (id VARCHAR(36), body TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_bin, qid VARCHAR(36), uid VARCHAR(36),  PRIMARY KEY(id) );"""
        self.cursor.execute(stmt)

        stmt =  """CREATE TABLE IF NOT EXISTS vote
        (uid VARCHAR(36), aid VARCHAR(36), vote INT(1), PRIMARY KEY(uid, aid) );"""
        self.cursor.execute(stmt)

    def initialize( self ):
        """create answer and vote tables and delete all data"""

        stmt = "DELETE FROM answer;"
        self.cursor.execute(stmt)

        stmt = "DELETE FROM vote;"
        self.cursor.execute(stmt)

    def count_exist(self, query, params, target):
        """checks if element exists in the table because select and
        delete does not return an error for a non-existent element"""

        if params:
            self.cursor.execute(query,params)
        else:
            self.cursor.execute(query)

        count = self.cursor.fetchone()[0]
        return count == target


    def dbRow_To_AnswerObj(self, results):
        """convert each row from the answer table to an Answer Object"""

        answers = []
        for row in results:
            id = row[0]
            body = row[1]
            vote = self.vote_tally(id)
            up_vote = vote[0]
            down_vote = vote[1]
            answer = qanda.Answer(id,body,up_vote,down_vote)
            answers.append(answer)
        return answers


    def get( self, id ):
        """return Answer object with matching id"""

        check_answer = "SELECT count(*) FROM answer WHERE id = %s"
        if self.count_exist(check_answer, (id,), 1):
            stmt = "SELECT * FROM answer where id = %s"
            result = self.cursor.execute(stmt,(id,)).fetchone()
            return self.dbRow_To_AnswerObj(result)[0]
        else:
            raise KeyError

    def get_all( self ):
        """return all Answer objects from the Answer table"""

        answers = []
        stmt = "SELECT * FROM answer"
        self.cursor.execute(stmt)
        results = self.cursor.fetchall()
        return self.dbRow_To_AnswerObj(results)

    def delete( self, id ):
        check = "SELECT count(*) FROM answer WHERE id = %s"
        if self.count_exist(check, (id,), 1):
            stmt = "DELETE FROM answer WHERE id = %s"
            self.cursor.execute(stmt,(id,))
        else:
            raise KeyError

    def rank( self, offset = 0, limit = 10 ):

        #Select answers with vote or without votes from left joinning
        #the answer table and vote table
        stmt = """SELECT a.id, SUM(v.vote) AS rank FROM answer a LEFT JOIN vote v
        on a.id=v.aid GROUP BY a.id ORDER BY rank DESC LIMIT %s OFFSET %s"""

        self.cursor.execute(stmt, (limit , offset ))
        rows = self.cursor.fetchall()
        ranks = []
        for row in rows:
            id = row[0]
            score = row[1]
            rank = qanda.Rank(id, score)
            ranks.append(rank)
        return ranks

    def new( self, user_id, question_id, text ):
        unique_id = str(uuid.uuid4())
        while unique_id == 0: #unique id can never be 0
            unique_id = str(uuid.uuid4())

        check_user = "SELECT count(*) FROM user WHERE id = %s"
        count_user = self.count_exist(check_user, (user_id,), 1)

        check_question = "SELECT count(*) FROM question WHERE id = %s"
        count_question = self.count_exist(check_question, (question_id,), 1)

        if (count_user and count_question):
            stmt = "INSERT INTO answer (id, body, qid ,uid) VALUES (%s,%s,%s,%s)"
            self.cursor.execute(stmt,(unique_id, text, question_id, user_id))
            return unique_id
        else:
            raise KeyError

    def get_answers( self, question_id ):
        """return all Answers objects to a question"""

        check_question = "SELECT count(*) FROM question WHERE id = %s"
        if self.count_exist(check_question, (question_id,), 1):
            stmt = "SELECT * FROM answer WHERE qid = %s"
            results = self.cursor.execute(stmt, (question_id,)).fetchall()
            return self.dbRow_To_AnswerObj(results)
        else:
            raise KeyError

    def vote( self, user_id, answer_id, vote ):
        """insert vote into the vote table"""

        check_user = "SELECT count(*) FROM user WHERE id = %s"
        count_user = self.count_exist(check_user, (user_id,), 1)

        check_answer = "SELECT count(*) FROM answer WHERE id = %s"
        count_answer = self.count_exist(check_answer, (answer_id,), 1)

        if (count_user and count_answer):
            stmt = "INSERT INTO vote (uid, aid, vote) VALUES (%s,%s,%s)"
            self.cursor.execute(stmt,(user_id, answer_id, vote.value))
        else:
            raise KeyError

    def vote_tally(self, answer_id):
        """return sum all up and down votes from an answer"""

        check_up_vote = "SELECT SUM(vote) FROM vote WHERE vote = 1 AND aid = %s"
        self.cursor.execute(check_up_vote,(answer_id,))
        count_up_vote = self.cursor.fetchone()[0]
        if not count_up_vote:
            count_up_vote = 0

        check_down_vote = "SELECT SUM(vote) FROM vote WHERE vote = -1 AND aid = %s"
        self.cursor.execute(check_down_vote,(answer_id,))
        count_down_vote = self.cursor.fetchone()[0]
        if not count_down_vote:
            count_down_vote = 0

        return (count_up_vote, count_down_vote)
