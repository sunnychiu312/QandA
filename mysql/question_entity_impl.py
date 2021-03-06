import qanda
import mysql
import uuid

class Question_Entity_Impl(qanda.QuestionEntity):

    def __init__(self, cursor):
        self.cursor = cursor
        stmt =  "CREATE TABLE IF NOT EXISTS question (id VARCHAR(36), body TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_bin, uid VARCHAR(36), PRIMARY KEY(id) );"
        self.cursor.execute(stmt)

    def initialize( self ):
        """create question table and delete all data"""

        stmt = "DELETE FROM question;"
        self.cursor.execute(stmt)

    def count_exist(self, query, params, target):
        """checks if element exists in the table because select and
        delete does not return an error for a non-existent element"""

        if params:
            self.cursor.execute(query,params)
        else:
            self.cursor.execute(query).fetchone()[0]

        count = self.cursor.fetchone()[0]
        return count == target

    def dbRow_To_QuestionObj(self, results):
        """convert rows from question table to a Question object """

        questions = []
        for row in results:
            id = row[0]
            body = row[1]
            question = qanda.Question(id,body)
            questions.append(question)
        return questions

    def get( self, id ):
        """return Question object with matching id"""

        check_question = "SELECT count(*) FROM question WHERE id = %s"
        if self.count_exist(check_question, (id,), 1):
            stmt = "SELECT FROM question where id =%s"
            result = self.cursor.execute(stmt,(id,)).fetchone()
            return self.dbRow_To_QuestionObj(result)[0]
        else:
            raise KeyError

    def get_all( self ):
        """return all Question objects from the question table"""

        stmt = "SELECT * FROM question"
        self.cursor.execute(stmt)
        results=self.cursor.fetchall()
        return self.dbRow_To_QuestionObj(results)

    def delete( self, id ):

        check = "SELECT count(*) FROM question WHERE id = %s"
        if self.count_exist(check, (id,), 1):
            stmt = "DELETE FROM question WHERE id =%s"
            self.cursor.execute(stmt,(id,))

            stmt = "DELETE FROM answer WHERE qid =%s"
            self.cursor.execute(stmt,(id,))
        else:
            raise KeyError

    def rank( self, offset = 0, limit = 10 ):

        #Selects questions that have answers and without answers
        stmt = """SELECT qid, count(*) AS c FROM answer GROUP BY qid UNION
        SELECT id, 0 AS c FROM question where id not in
        (SELECT qid FROM answer group by qid) ORDER BY c DESC LIMIT %s OFFSET %s"""

        self.cursor.execute(stmt, (limit , offset ))
        rows = self.cursor.fetchall()
        ranks = []
        for row in rows:
            id = row[0]
            score = row[1]
            rank = qanda.Rank(id, score)
            ranks.append(rank)
        return ranks

    def new( self, user_id, text ):
        unique_id = str(uuid.uuid4())
        while unique_id == 0: #unique id can never be 0
            unique_id = str(uuid.uuid4())

        check = "SELECT count(*) FROM user WHERE id = %s"

        if self.count_exist(check, (user_id,), 1):
            stmt = "INSERT INTO question (id, body, uid) VALUES (%s,%s,%s)"
            self.cursor.execute(stmt,(unique_id, text, user_id))
            return unique_id
        else:
            raise KeyError
