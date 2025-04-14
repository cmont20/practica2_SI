import sqlite3

database = "data.db"
schema = "schema.sql"


def database_creation():
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    with open(schema, "r", encoding="utf-8") as file:
        cursor.executescript(file.read())

    conn.commit()
    conn.close()
    print("Database created")


if __name__ == "__main__":
    database_creation()
