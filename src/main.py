#!/usr/bin/env python3
import os
import sys

from file_helper import make_pdf_files, make_image_files, move_pdfs_in_pdf_folder, move_htmls_in_html_folder, \
    move_folders_to_images_folder
from google_drive_helper import upload_folder_to_drive_recursively
from result_helper import prepare_result_db_and_return_folder_name, group_result_by_campus, \
    create_html_table_file_for_campus_result
from campus_helper import add_campus
from summary_helper import create_html_table_file_from_summary
from utils import get_user_input_or_set_default_with_validation


def publish(_upload: str = None, _result_name: str = None, _input_filename: str = None) -> None:
    result_name: str = get_user_input_or_set_default_with_validation("Result Name:", _result_name, name="__main__")
    result_name = result_name.strip().title()

    if os.path.exists("client_secrets.json"):
        upload: str = get_user_input_or_set_default_with_validation("Do you want to upload the result to Google Drive? (Y/N):", _upload, "[Y|N]", name="__main__")
    else:
        print("client_secrets.json not found. Falling back to NO-UPLOAD Mode.")
        upload: str = "N"

    input_filename: str = get_user_input_or_set_default_with_validation("Result File Name:", _input_filename, "\\.txt$", name="__main__")
    input_filename = input_filename.strip()

    result_folder: str = prepare_result_db_and_return_folder_name(input_filename, result_name)

    create_html_table_file_from_summary(result_folder, result_name)

    result_group: dict = group_result_by_campus(result_folder)
    for code in result_group:
        create_html_table_file_for_campus_result(code, result_group[campus_code], result_folder, result_name)

    make_pdf_files(result_folder)
    make_image_files(result_folder)
    move_pdfs_in_pdf_folder(result_folder)
    move_htmls_in_html_folder(result_folder)
    move_folders_to_images_folder(result_folder)

    if upload == "Y":
        folder_info: list = upload_folder_to_drive_recursively(result_folder)
        folder_link: str = folder_info[1]
        print(f"Result is uploaded to google drive. You can access it from here: {folder_link}")
    else:
        print(f"Result is stored in {result_folder} folder.")

    print("Done!")


if __name__ == '__main__':
    args: list = sys.argv

    if len(args) == 1:
        publish("N", "Result", "IN.txt")
    elif 2 <= len(args) <= 5 and args[1] == "add-campus":
        if len(args) > 2:
            campus_code: str = args[2]
        else:
            campus_code: str = ""

        if len(args) > 3:
            campus_name: str = args[3]
        else:
            campus_name: str = ""

        if len(args) > 4:
            campus_address: str = args[4]
            name = "__main__"
        else:
            campus_address: str = ""
            name = ""

        campus_code: str = get_user_input_or_set_default_with_validation("Enter Campus Code:", campus_code, "[0-9]*", name)
        campus_name: str = get_user_input_or_set_default_with_validation("Enter Campus Name:", campus_name, name)
        campus_address: str = get_user_input_or_set_default_with_validation("Enter Campus Address:", campus_address, name)

        campus_name = campus_name.strip().title()
        campus_address = campus_address.strip().title()

        add_campus(int(campus_code), campus_name, campus_address)
    else:
        print(f"Invalid arguments. Please use 'python {args[0]}' or 'python {args[0]} add-campus'")
