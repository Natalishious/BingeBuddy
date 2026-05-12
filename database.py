import sqlite3

DB_NAME = "users.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    # Row factory gör så att vi kan läsa user["username"] istället för att indexera user[0] t.ex
    conn.row_factory = sqlite3.Row
    # Ifall try/except på create_user och user redan finns kraschar inte programmet. Returnerar bool.
    # Blir lättare för login senare
    return conn


def init_db():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)  # Skapar en users tabell om det inte redan finns

    conn.commit()
    conn.close()


def create_user(username, password):  # Måste ha med username, password

    conn = get_connection(
    )

    try:
        conn.execute(
            # Frågetecken är placeholders för values. Första username, andra passw.
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()
        return True  # Måste returnera True eller false
    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()


# def delete_user():
#     pass
#     # Del users


def get_user(username):
    conn = get_connection()
    user = conn.execute(
        "SELECT id, username, password FROM users WHERE username = ?",
        # Använder ett kommatecken här för att säga till Python att vi skickar med en tuple.
        (username,)
        # Annars tror Python att det är en enkel variabel.
    ).fetchone()

    conn.close()
    return user
