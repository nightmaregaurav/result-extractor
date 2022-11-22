import sqlite3

from string import Template
from typing import TextIO

from .templates import SUMMARY_HTML_HEADER, SUMMARY_HTML_BODY, SUMMARY_HTML_FOOTER


def prepare_summary_table_in_result_db(folder_name: str) -> None:
    result_db_path: str = folder_name + "/result.db"
    result_connection: sqlite3.Connection = sqlite3.connect(result_db_path)
    cursor: sqlite3.Cursor = result_connection.cursor()
    # noinspection SqlDialectInspection
    cursor.execute("CREATE TABLE summary ("
                   "    campus_code INTEGER PRIMARY KEY,"
                   "    total_passed INTEGER,"
                   "    FOREIGN KEY (campus_code) REFERENCES campus (campus_code)"
                   ")")
    result_connection.commit()
    result_connection.close()


def fill_summary_data_in_result_db(folder_name: str) -> None:
    result_db_path: str = folder_name + "/result.db"
    result_connection: sqlite3.Connection = sqlite3.connect(result_db_path)
    cursor: sqlite3.Cursor = result_connection.cursor()
    # noinspection SqlDialectInspection
    cursor.execute("SELECT campus_code, COUNT(*) FROM result GROUP BY campus_code")
    summary_data: list = cursor.fetchall()
    for data in summary_data:
        # noinspection SqlDialectInspection
        cursor.execute("INSERT INTO summary VALUES (?, ?)", (data[0], data[1]))
    result_connection.commit()
    result_connection.close()


def create_html_table_file_from_summary(folder_name: str, result_name: str) -> None:
    result_db_path: str = folder_name + "/result.db"
    result_db_connection: sqlite3.Connection = sqlite3.connect(result_db_path)
    cursor: sqlite3.Cursor = result_db_connection.cursor()
    # noinspection SqlDialectInspection
    cursor.execute("SELECT campus.campus_code, campus.campus_name, campus.campus_address, total_passed FROM summary FULL JOIN campus ON summary.campus_code = campus.campus_code ORDER BY total_passed DESC")
    summary_data: list = cursor.fetchall()
    result_db_connection.close()

    summary_html_template: Template = Template(SUMMARY_HTML_HEADER)
    summary_html: str = summary_html_template.substitute(
        result_name=result_name,
    )

    summary_html_template: Template = Template(SUMMARY_HTML_BODY)
    for data in summary_data:
        summary_html += summary_html_template.substitute(
            campus_code=data[0],
            campus_name=data[1],
            campus_address=data[2],
            total_passed_students=data[3],
        )

    summary_html_template: Template = Template(SUMMARY_HTML_FOOTER)
    summary_html += summary_html_template.substitute()

    summary_html_file_path: str = folder_name + "/summary.html"
    summary_html_file: TextIO = open(summary_html_file_path, "w")
    summary_html_file.write(summary_html)
    summary_html_file.close()
