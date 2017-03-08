import os.path
import sqlite3

class DataBase(object):
    '''Requires the path and name of the dataBase to run operations on.'''

    def __init__(self, path, user):
        self.path = path
        self.user = user
        # Checks if the user has a database already.
        if  not os.path.isfile('%s/%s.db' % (self.path, self.user)):
            self.conn = sqlite3.connect('%s.db' % self.user)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            self.commit(self.initTables())
        if os.path.isfile('%s/%s.db' % (self.path, self.user)):
            self.conn = sqlite3.connect('%s.db' % self.user)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()

        self.conn.text_factory = str

    def __enter__(self):
        return self

    def commit(self, change):
        try:
            change
            self.conn.commit()
        except sqlite3.Error, e:
            if self.conn:
                self.conn.rollback()
                print 'Error %s:' % e.args[0]
                exit()

    def initTables(self):
        self.cursor.execute("CREATE TABLE Books(Name TEXT, \
                                                Author TEXT, \
                                                Genre TEXT)")

    def addBook(self, name, author, genre):
        params = (name, author, genre)
        self.cursor.execute("INSERT INTO Books VALUES(?, ?, ?)", params)

    def contents(self):
        self.cursor.execute("SELECT * FROM Books")
        rows = self.cursor.fetchall()
        return rows

    def delete(self, cond):
        self.cursor.execute("DELETE FROM Books WHERE Name=?", (cond,))

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

#with DataBase('C:/Python27/Programs/booklibrary', 'andy') as dataBase:
    # Use database
    #dataBase.commit(dataBase.addBook('Moby Dick', 'Some Dude', 'Old'))
    #print dataBase.cursor.lastrowid
    #print 'test'
