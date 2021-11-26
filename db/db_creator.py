import sqlite3
import os

path = os.path.dirname(os.path.realpath(__file__))

conn = sqlite3.connect(path + '/' + 'users.db')

#######################################################################

# conn.cursor().execute("""CREATE TABLE users
#              (id integer,
#               nick text,
#               projects text)""")

#######################################################################
