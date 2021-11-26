from typing import List

from db.db_creator import conn

c = conn.cursor()

def add_user(id: int, nick: str) -> None:
    with conn:
        c.execute("INSERT INTO users VALUES (?, ?, ?)", (id, nick, ''))

def remove_user(id: int) -> None:
    with conn:
        c.execute("DELETE FROM users WHERE id=?", (id,))

def get_user_by_id(id: int) -> List:
    with conn:
        c.execute("SELECT * FROM users where id=?", (id,))
        return c.fetchone()

def get_user_by_project(message_id: int) -> List:
    with conn:
        c.execute("SELECT * FROM users WHERE projects LIKE ?",
        (f"%{message_id}%",))
    
    return c.fetchone()

def add_project_to_user(user_id: int, message_id: int) ->  None:
    with conn:
        c.execute("SELECT * FROM users where id=?", (user_id,))
        user = c.fetchone()

        PROJECTS = 2
        if user[PROJECTS]:
            projects = user[PROJECTS] + f", {message_id}"

        else:
            projects = f"{message_id}"

        c.execute("UPDATE users SET projects=? WHERE id=?", (projects, user_id,))

def remove_project_from_user(user_id: int, message_id: int) -> None:
    with conn:
        c.execute("SELECT * FROM users where id=?", (user_id,))
        user = c.fetchone()

        PROJECTS = 2
        projects = user[PROJECTS].split(', ')
        if str(message_id) not in projects:
            raise ValueError(f"user with user_id {user_id} does not contain project with message_id {message_id}")

        projects.remove(str(message_id))
        
        c.execute("UPDATE users SET projects=? WHERE id=?", (', '.join(projects), user_id,))

def update_user_name(id: int, nick: str) -> None:
    with conn:
        c.execute("UPDATE users SET nick=? WHERE id=?",
            (nick, id,))

def view_db() -> None:
    with conn:
        c.execute("SELECT * FROM users")
        users = c.fetchall()
        
        for user in users:
            print(user)