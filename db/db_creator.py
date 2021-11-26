import sqlite3
import os

path = os.path.dirname(os.path.realpath(__file__))

conn = sqlite3.connect(path + '/' + 'users.db')

#######################################################################

# conn.cursor().execute("""CREATE TABLE users
#              (id integer,
#               nick text,
#               projects text,
#               singleplayer_wins int,
#               coop_wins int,
#               vs_wins int,
#               tic_tac_toe_wins int,
#               thumbs_ups int)""")

#######################################################################
