import qanda
import mysql
import uuid

class User_Entity_Impl(qanda.UserEntity):

    def __init__(self, cursor):
        self.cursor = cursor

        stmt = "CREATE TABLE IF NOT EXISTS user (id VARCHAR(36), email VARCHAR(255), password VARCHAR(36), PRIMARY KEY(id) );"
        self.cursor.execute(stmt)

        #Create a view of users that answer their own question
        stmt = """
            CREATE OR REPLACE VIEW ans_own_quest_view AS
            SELECT a.uid, a.id FROM answer a WHERE a.id NOT IN
            (SELECT a.id FROM answer a JOIN question q on a.uid = q.uid and a.qid = q.id);
        """
        self.cursor.execute(stmt)


    def initialize( self ):
        """create user table and delete all data"""

        stmt = "DELETE FROM user;"
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

    def dbRow_To_UserObj(self, results):
        """convert rows from user table to a User object """

        users = []
        for row in results:
            id = row[0]
            email = row[1]
            password = row[2]
            user = qanda.User(id,email,password)
            users.append(user)
        return users

    def get( self, id ):
        """return User object with matching id"""

        check_user = "SELECT count(*) FROM user WHERE id = %s;"
        if self.count_exist(check_user, (id,), 1):
            stmt = "SELECT FROM question where id =%s;"
            result = self.cursor.execute(stmt,(id,)).fetchone()
            return self.dbRow_To_UserObj(result)[0]
        else:
            raise KeyError

    def get_all( self ):
        """return all User objects from the user table"""

        stmt = "SELECT * FROM user;"
        self.cursor.execute(stmt)
        results = self.cursor.fetchall()
        return self.dbRow_To_UserObj(results)

    def delete( self, id ):

        check = "SELECT count(*) FROM user WHERE id = %s;"
        if self.count_exist(check, (id,), 1):
            stmt = "DELETE FROM user WHERE id =%s;"
            self.cursor.execute(stmt,(id,))
        else:
            raise KeyError

    def rank( self, offset = 0, limit = 10 ):

        #Creates a temp view of users who did not answer their own questions
        #Then joins it with users that did not answer any questions to select
        #all users that answer other's questions or no question

        stmt1 = """

            SELECT u.id, s.score FROM user u LEFT JOIN
            (SELECT uid, COUNT(*) AS score FROM ans_own_quest_view GROUP BY uid) s
            on u.id = s.uid ORDER BY s.score DESC LIMIT %s OFFSET %s;
            """

        self.cursor.execute(stmt1, (limit, offset))
        rows = self.cursor.fetchall()
        ranks = []
        for row in rows:
            id = row[0]
            score = row[1]
            rank = qanda.Rank(id, score)
            ranks.append(rank)
        return ranks

    def new( self, email, passhash = None ):
        unique_id = str(uuid.uuid4())
        while unique_id == 0: #unique id can never be 0
            unique_id = str(uuid.uuid4())

        check = "SELECT count(*) FROM user WHERE email = %s;"
        if self.count_exist(check, (email,), 0):
            stmt = "INSERT INTO user (id, email, password) VALUES (%s,%s,%s);"
            self.cursor.execute(stmt,(unique_id, email, passhash))
            return unique_id
        else:
            raise KeyError
