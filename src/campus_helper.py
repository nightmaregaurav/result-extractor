import sqlite3

DEFAULT_CAMPUS_DB = "campus.db"


def get_campus_code_from_student_code(student_code: str) -> int:
    return int(student_code.split("-")[0])


def get_all_campuses() -> list:
    conn: sqlite3.Connection = sqlite3.connect(DEFAULT_CAMPUS_DB)
    cursor: sqlite3.Cursor = conn.cursor()
    # noinspection SqlDialectInspection
    cursor.execute("SELECT * FROM campus ORDER BY code")
    campuses: list = cursor.fetchall()
    conn.close()
    return campuses


def add_campus(campus_code: int, campus_name: str, campus_address: str) -> None:
    try:
        conn: sqlite3.Connection = sqlite3.connect(DEFAULT_CAMPUS_DB)
        cursor: sqlite3.Cursor = conn.cursor()
        # noinspection SqlDialectInspection
        cursor.execute("INSERT INTO campus VALUES (?, ?, ?)", (campus_code, campus_name, campus_address))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        print("Campus code already exists. Please try again.")


def prepare_campus_table_in_result_db(db_path: str = DEFAULT_CAMPUS_DB) -> None:
    result_connection: sqlite3.Connection = sqlite3.connect(db_path)
    cursor: sqlite3.Cursor = result_connection.cursor()
    # noinspection SqlDialectInspection
    cursor.execute("CREATE TABLE campus ("
                   "    campus_code INTEGER PRIMARY KEY,"
                   "    campus_name TEXT,"
                   "    campus_address TEXT"
                   ")")
    result_connection.commit()
    result_connection.close()


def insert_campuses_into_result_db(campuses: list, db_path: str = DEFAULT_CAMPUS_DB) -> None:
    result_connection: sqlite3.Connection = sqlite3.connect(db_path)
    cursor: sqlite3.Cursor = result_connection.cursor()
    for campus in campuses:
        # noinspection SqlDialectInspection
        cursor.execute("INSERT INTO campus VALUES (?, ?, ?)", (campus[0], campus[1], campus[2]))
    result_connection.commit()
    result_connection.close()


def get_campus_name_and_address_by_campus_code(campus_code: int) -> (str, str):
    conn: sqlite3.Connection = sqlite3.connect(DEFAULT_CAMPUS_DB)
    cursor: sqlite3.Cursor = conn.cursor()
    # noinspection SqlDialectInspection
    cursor.execute("SELECT name, address FROM campus WHERE code = ?", (campus_code,))
    result: tuple = cursor.fetchone()
    conn.close()
    return result
