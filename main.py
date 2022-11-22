#!/usr/bin/env python3
import os
import sys

from yaspin.core import Yaspin

from src.campus_helper import add_campus
from src.google_drive_helper import upload_folder_to_drive_recursively
from src.result_helper import prepare_result_db_and_return_folder_name, group_result_by_campus, create_html_table_file_for_campus_result, process_result_htmls
from src.summary_helper import create_html_table_file_from_summary
from src.utils import get_user_input_or_set_default_with_validation, start_progress_spinner, stop_progress_spinner


def publish_result(_upload: str = None, _result_name: str = None, _input_filename: str = None) -> None:
    result_name: str = get_user_input_or_set_default_with_validation("Result Name:", _result_name)
    result_name = result_name.strip().title()

    if os.path.exists("client_secrets.json"):
        upload: str = get_user_input_or_set_default_with_validation("Do you want to upload the result to Google Drive? (Y/N):", _upload, "[Y|N]")
    else:
        print("client_secrets.json not found. Falling back to NO-UPLOAD Mode.")
        upload: str = "N"

    input_filename: str = get_user_input_or_set_default_with_validation("Result File Name:", _input_filename, r".+\.txt$")
    input_filename = input_filename.strip()

    progress_thread: Yaspin = start_progress_spinner("Preparing Result DB")
    result_folder: str = prepare_result_db_and_return_folder_name(input_filename, result_name)
    stop_progress_spinner(progress_thread, "Done!")

    progress_thread = start_progress_spinner("Creating Result Summary HTML")
    create_html_table_file_from_summary(result_folder, result_name)
    stop_progress_spinner(progress_thread, "Done!")

    with start_progress_spinner("Creating Result HTMLs") as progress_thread:
        result_group: dict = group_result_by_campus(result_folder)
        for code in result_group:
            create_html_table_file_for_campus_result(code, result_group[code], result_folder, result_name)
        stop_progress_spinner(progress_thread, "Done!")

    with start_progress_spinner("Processing Result HTMLs to PDFs and Images") as progress_thread:
        process_result_htmls(result_folder)
        stop_progress_spinner(progress_thread, "Done!")

    with start_progress_spinner("Saving Results") as progress_thread:
        if upload == "Y":
            folder_info: list = upload_folder_to_drive_recursively(result_folder)
            folder_link: str = folder_info[1]
            print(f"Result is uploaded to google drive. You can access it from here: {folder_link}")
        else:
            print(f"Result is stored in {result_folder} folder.")
        stop_progress_spinner(progress_thread, "Done!")


def process_add_campus(_args: list) -> None:
    if len(_args) > 2:
        campus_code: str = _args[2]
    else:
        campus_code: str = get_user_input_or_set_default_with_validation("Enter Campus Code:", "", "[0-9]*")

    if len(_args) > 3:
        campus_name: str = _args[3]
    else:
        campus_name: str = get_user_input_or_set_default_with_validation("Enter Campus Name:", "")

    if len(_args) > 4:
        campus_address: str = _args[4]
    else:
        campus_address: str = get_user_input_or_set_default_with_validation("Enter Campus Address:", "")

    campus_name = campus_name.strip().title()
    campus_address = campus_address.strip().title()

    add_campus(int(campus_code), campus_name, campus_address)


if __name__ == '__main__':
    args: list = sys.argv

    if len(args) == 1:
        publish_result("N", "Result", "IN.txt")
    elif 2 <= len(args) <= 5 and args[1] == "add-campus":
        process_add_campus(args)
    else:
        print(f"Invalid arguments. Please use 'python {args[0]}'"
              f" or 'python {args[0]} add-campus [campus-code] [campus-name] [campus-address]' {{Where [] are optional}}")
