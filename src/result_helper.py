import os
import sqlite3
from datetime import datetime
from string import Template
from typing import TextIO

from slugify import slugify

from campus_helper import get_all_campuses, insert_campuses_into_result_db, get_campus_code_from_student_code, \
    prepare_campus_table_in_result_db, get_campus_name_and_address_by_campus_code
from summary_helper import prepare_summary_table_in_result_db, fill_summary_data_in_result_db
from templates import HTML_HEADER, HTML_BODY, HTML_FOOTER


def parse_result_file(file_path: str) -> list:
    result_file: TextIO = open(file_path)
    result: list = [symbol_no.strip().upper() for symbol_no in result_file]
    result_file.close()
    return result


def create_result_folder(name: str) -> str:
    folder_name: str = "Publish-" + slugify(name) + "-" + datetime.now().strftime("%Y%m%d%H%M%S")
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return folder_name


def prepare_result_table_in_result_db(folder_name: str) -> None:
    result_db_path: str = folder_name + "/result.db"
    result_connection: sqlite3.Connection = sqlite3.connect(result_db_path)
    cursor: sqlite3.Cursor = result_connection.cursor()
    # noinspection SqlDialectInspection
    cursor.execute("CREATE TABLE result ("
                   "    symbol_no TEXT PRIMARY KEY,"
                   "    campus_code INTEGER,"
                   "    global_rank INTEGER,"
                   "    FOREIGN KEY (campus_code) REFERENCES campus (campus_code)"
                   ")")
    result_connection.commit()
    result_connection.close()


def insert_results_into_result_db(results: list, folder_name: str) -> None:
    result_db_path: str = folder_name + "/result.db"
    result_connection: sqlite3.Connection = sqlite3.connect(result_db_path)
    cursor: sqlite3.Cursor = result_connection.cursor()
    for index, result in enumerate(results):
        # noinspection SqlDialectInspection
        cursor.execute("INSERT INTO result VALUES (?, ?, ?)", (
            result,
            get_campus_code_from_student_code(result),
            index+1))
    result_connection.commit()
    result_connection.close()


def prepare_result_db_and_return_folder_name(input_filename: str, result_name: str) -> str:
    folder_name: str = create_result_folder(result_name)
    result_db_path: str = folder_name + "/result.db"
    prepare_campus_table_in_result_db(result_db_path)
    prepare_result_table_in_result_db(folder_name)
    prepare_summary_table_in_result_db(folder_name)

    insert_campuses_into_result_db(get_all_campuses(), result_db_path)
    insert_results_into_result_db(parse_result_file(input_filename), folder_name)
    fill_summary_data_in_result_db(folder_name)

    return folder_name


def group_result_by_campus(folder_name: str) -> dict:
    result_db_path: str = folder_name + "/result.db"

    result: dict = {}
    campuses: list = get_all_campuses()
    for campus in campuses:
        result_db_connection: sqlite3.Connection = sqlite3.connect(result_db_path)
        cursor: sqlite3.Cursor = result_db_connection.cursor()
        # noinspection SqlDialectInspection
        cursor.execute("SELECT symbol_no, global_rank FROM result WHERE campus_code = ? ORDER BY global_rank", (campus[0],))

        data: list = cursor.fetchall()
        if len(data) > 0:
            result[campus[0]] = data

        result_db_connection.close()
    return result


def get_total_result_count(folder_name: str) -> int:
    result_db_path: str = folder_name + "/result.db"
    result_db_connection: sqlite3.Connection = sqlite3.connect(result_db_path)
    cursor: sqlite3.Cursor = result_db_connection.cursor()
    # noinspection SqlDialectInspection
    cursor.execute("SELECT COUNT(*) FROM result")
    data: list = cursor.fetchall()
    result_db_connection.close()
    return data[0][0]


def create_html_table_file_for_campus_result(campus_code: int, data: list, folder_name: str, result_name: str) -> None:
    campus_info: list = get_campus_name_and_address_by_campus_code(campus_code)
    campus_name: str = campus_info[0]
    campus_address: str = campus_info[1]

    file_html_template: Template = Template(HTML_HEADER)
    file_html: str = file_html_template.substitute(
        campus_code=campus_code,
        result_name=result_name,
        campus_name=campus_name,
        campus_address=campus_address,
    )

    file_html_template: Template = Template(HTML_BODY)
    for index, row in enumerate(data):
        file_html += file_html_template.substitute(
            global_rank=row[1],
            campus_rank=index+1,
            symbol_number=row[0]
        )

    file_html_template: Template = Template(HTML_FOOTER)
    file_html += file_html_template.substitute(
        total_passed_students_in_campus=len(data),
        total_passed_students=get_total_result_count(folder_name)
    )

    file_path: str = folder_name + "/" + str(campus_code) + ".html"
    file: TextIO = open(file_path, "w")
    file.write(file_html)
    file.close()
