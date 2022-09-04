import re
import sqlite3
import os
import weasyprint
import pdf2image
from slugify import slugify
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


# noinspection PyShadowingBuiltins
def input_for_script(text, default):
    if __name__ == "__main__":
        input_from_user = input(text)
        if input_from_user.strip() == "":
            return default
        return input_from_user
    else:
        return default


def get_repeated_contents(array):
    return set([x for x in array if array.count(x) > 1])


def get_campus_code(symbol_no):
    return int(symbol_no.split("-")[0])


def get_merit_list():
    result_file = open("IN.txt")
    merit_list = [symbol_no.strip().upper() for symbol_no in result_file]
    result_file.close()

    merit_set = set(merit_list)
    if len(merit_list) != len(merit_set):
        print("Duplicate Symbol numbers found in the merit list.")
        print(f"Total processed Symbol numbers: {len(merit_list)}")
        print(f"Total unique Symbol numbers: {len(merit_set)}")
        print(f"Total Repeated Symbol Numbers: {len(merit_list) - len(merit_set)}")
        print(f"Repeated Symbol Numbers:")
        for sym in get_repeated_contents(merit_list):
            print(f"\t{sym}")
        assert False
    return merit_list


def get_campus_dict():
    campus_dict = {}
    conn = sqlite3.connect('campus.db')
    # noinspection SqlDialectInspection,SqlNoDataSourceInspection
    cursor = conn.execute("SELECT code, name, address from campus ORDER BY code")
    for row in cursor:
        campus_dict[int(row[0])] = {
            'campus_name': row[1],
            'campus_address': row[2],
            'merit_list': list()
        }
    conn.close()
    return campus_dict


def get_drive_auth():
    auth = GoogleAuth()
    auth.LoadCredentialsFile("credentials.txt")
    if auth.credentials is None:
        auth.LocalWebserverAuth()
    elif auth.access_token_expired:
        auth.Refresh()
    else:
        auth.Authorize()
    auth.SaveCredentialsFile("credentials.txt")
    drive = GoogleDrive(auth)
    return drive


def upload_to_drive(drive, files, folder, folder_id=None):
    folder_link = None
    if folder_id is None:
        folder = drive.CreateFile({'title': folder, 'mimeType': 'application/vnd.google-apps.folder'})
        folder.Upload()
        folder.InsertPermission({
            'type': 'anyone',
            'value': 'anyone',
            'role': 'reader'
        })
        folder_id = folder.get('id')
        folder_link = folder.get('alternateLink')

    file_link = ""
    for file in files:
        file_drive = drive.CreateFile({'parents': [{'id': folder_id}], 'title': file.split("/")[-1]})
        file_drive.SetContentFile(file)
        file_drive.Upload()
        file_drive.InsertPermission({
            'type': 'anyone',
            'value': 'anyone',
            'role': 'reader'
        })
        if file.endswith(".pdf"):
            file_link = file_drive.get('alternateLink')

    return folder_link, folder_id, file_link


def publish_result(_year, _campus_code, _campus_name="", _campus_address="", _mode=2, _action="N", _result_name="BCA Entrance Result", _upload="N"):
    assert type(_year) == str
    assert type(_campus_code) == int
    assert type(_campus_name) == str
    assert type(_campus_address) == str
    assert type(_mode) == int
    assert type(_action) == str
    assert type(_result_name) == str
    assert type(_upload) == str

    _year = _year.strip()
    _campus_name = _campus_name.strip()
    _campus_address = _campus_address.strip()
    _action = _action.strip().upper()
    _result_name = _result_name.strip()
    _upload = _upload.strip().upper()
    assert _action in ["N", "Y"]

    upload = input_for_script(f"Do you want to upload the result to Google Drive? (Y/N) [default: {_upload}]: ", _upload)
    upload = upload.strip().upper()
    assert upload in ["N", "Y"]

    drive_auth = None
    if upload == "Y":
        if os.path.exists("client_secrets.json"):
            drive_auth = get_drive_auth()
        else:
            print("client_secrets.json not found. Falling back to NO-UPLOAD Mode.")

    merit_list = get_merit_list()

    year = input_for_script("Input Result Year: ", _year)
    result_name = input_for_script(f"Input Result Name [default: {_result_name}]: ", _result_name)
    mode = input_for_script("What do you want to do?\n"
                            "\t1. Publish result of specific campus.\n"
                            "\t2. Publish result of all campuses in db.\n"
                            f"Your Input [default: {_mode}] >>> ", _mode)
    mode = int(mode)
    assert mode in [1, 2]
    campus_dict_to_work_on = dict()
    new_campus_codes = []
    unknown_campus_codes = []
    _campus_dict = get_campus_dict()

    if mode == 1:
        __cc = input_for_script("Input the symbol no of campus(eg. 02): ", _campus_code)
        if int(__cc) in _campus_dict:
            campus_dict_to_work_on[int(__cc)] = _campus_dict[int(__cc)]
        else:
            new_campus_codes.append(int(__cc))
            campus_dict_to_work_on[int(__cc)] = {
                'campus_name': input_for_script("Input the name campus(eg. Mechi Multiple Campus): ", _campus_name),
                'campus_address': input_for_script("Input the address campus(eg. Bhadrapur, Jhapa.): ", _campus_address),
                'merit_list': list(),
            }
    else:
        campus_dict_to_work_on = _campus_dict

    global_rank = 0
    for symbol_no in merit_list:
        global_rank += 1
        campus_code = get_campus_code(symbol_no)

        try:
            campus_dict_to_work_on[campus_code]['merit_list'].append({
                "global_rank": global_rank,
                "symbol_no": symbol_no
            })
        except KeyError:
            campus_dict_to_work_on[campus_code] = {
                'campus_name': "",
                'campus_address': "",
            }
            campus_dict_to_work_on[campus_code]['merit_list'] = list()
            campus_dict_to_work_on[campus_code]['merit_list'].append({
                "global_rank": global_rank,
                "symbol_no": symbol_no
            })
            unknown_campus_codes.append(campus_code)

    if mode == 2:
        try:
            os.remove("summary.db")
        except FileNotFoundError:
            pass

        summary_db = sqlite3.connect('summary.db')
        summary_cursor = summary_db.cursor()
        # noinspection SqlNoDataSourceInspection,SqlDialectInspection
        summary_cursor.execute('''
        CREATE TABLE IF NOT EXISTS "summary" (
            "code" INTEGER NOT NULL UNIQUE,
            "name" TEXT,
            "address" TEXT,
            "passed students" INTEGER NOT NULL,
            PRIMARY KEY("code")
        )''')
        summary_db.commit()

    folder_link, folder_id = None, None
    for campus_code in campus_dict_to_work_on:
        campus_name = campus_dict_to_work_on[campus_code]['campus_name']
        campus_name = " ".join(campus_name.replace(" ,", ",").replace(",", ", ").split()).title()
        campus_name = re.sub(' +', ' ', campus_name)

        campus_address = campus_dict_to_work_on[campus_code]['campus_address']
        campus_address = " ".join(campus_address.replace(" ,", ",").replace(",", ", ").split()).title()
        campus_address = re.sub(' +', ' ', campus_address)

        text_file_content = f"{result_name}: {year}\n" \
                            f"Campus: {campus_name}\n" \
                            f"Address: {campus_address}\n" \
                            f"Code: {campus_code}\n"
        html_file_content = "<!DOCTYPE html>\n" \
                            "<html>\n" \
                            "<head>\n" \
                            f"	<title>{campus_code} {result_name}: {year}</title>\n" \
                            "</head>\n" \
                            "<body>\n" \
                            "	<center>\n" \
                            "		<table border='2px' style='margin-left: auto; margin-right: auto;'>\n" \
                            "			<thead>\n" \
                            "				<tr>\n" \
                            "					<th colspan='3'>\n" \
                            f"						{result_name}: {year}\n" \
                            "					</th>\n" \
                            "				</tr>\n" \
                            "				<tr>\n" \
                            "					<th colspan='3'>\n" \
                            f"						Campus: {campus_name}\n" \
                            "					</th>\n" \
                            "				</tr>\n" \
                            "				<tr>\n" \
                            "					<th colspan='3'>\n" \
                            f"						Address: {campus_address}\n" \
                            "					</th>\n" \
                            "				</tr>\n" \
                            "				<tr>\n" \
                            "					<th colspan='3'>\n" \
                            f"						Code: {campus_code}\n" \
                            "					</th>\n" \
                            "				</tr>\n" \
                            "				<tr>\n" \
                            "					<th colspan='3'>\n" \
                            "						" \
                            "					</th>\n" \
                            "				</tr>\n" \
                            "				<tr>\n" \
                            "					<th>\n" \
                            "						| Global Rank |\n" \
                            "					</th>\n" \
                            "					<th>\n" \
                            "						| Campus Rank |\n" \
                            "					</th>\n" \
                            "					<th>\n" \
                            "						| Symbol No |\n" \
                            "					</th>\n" \
                            "				</tr>\n" \
                            "			</thead>\n" \
                            "			<tbody>\n"

        post_file_content = text_file_content
        post_file_content += "PDF Link: <<replace_me>>\n"
        text_file_content += "\nGlobalRank\t CampusRank\t SymbolNo\n"

        campus_rank = 0
        campus_merit_list: list = campus_dict_to_work_on[campus_code]['merit_list']
        for entry in campus_merit_list:
            campus_rank += 1

            global_rank = entry['global_rank']
            symbol_no = entry['symbol_no']

            text_file_content += f"{global_rank}\t {campus_rank}\t {symbol_no}\n"
            html_file_content += "<tr>\n" \
                                 f"	<td>{global_rank}</td>\n" \
                                 f"	<td>{campus_rank}</td>\n" \
                                 f" <td>{symbol_no}</td>\n" \
                                 "</tr>\n"

        html_file_content += "			</tbody>\n" \
                             "          <tfoot>\n" \
                             "            <tr><td colspan='3'></td></tr>\n" \
                             "            <tr><td colspan='3'></td></tr>\n" \
                             "            <tr>\n" \
                             "                <td colspan='3' style='text-align: center;'><small><i>Extracted by: <b>Gaurav Nyaupane (MMC BCA 2017)</b></i><small></td>\n" \
                             "            </tr>\n" \
                             "          </tfoot>\n" \
                             "		</table>\n" \
                             "	</center>\n" \
                             "</body>\n" \
                             "</html>\n"

        post_file_content += f"Total Passed students: {len(merit_list)}\n" \
                             f"Total Passed students(This Campus): {campus_rank}\n\n" \
                             f"Search your campus' result using hashtag<campus code>(eg. #{slugify(result_name).replace('-', '_')}_{year}_{campus_code})\n" \
                             f"If result for your campus is not published, inbox us your campus' code/symbol no to get it published.\n" \
                             f"Extracted By: Gaurav Nyaupane (MMC BCA 2017)"
        text_file_content += f"\nTotal Passed students: {len(merit_list)}" \
                             f"\nTotal Passed students(This Campus): {campus_rank}" \
                             f"\n\nExtracted By: Gaurav Nyaupane (MMC BCA 2017)"

        print(f"Total Passed Students in ({campus_code}) {campus_name}, {campus_address}: {campus_rank}")

        if mode == 2:
            # noinspection SqlDialectInspection,SqlNoDataSourceInspection,PyUnboundLocalVariable
            summary_cursor.execute(
                f"INSERT INTO summary VALUES({campus_code}, '{campus_name}', '{campus_address}', {campus_rank})")

        if campus_rank != 0:
            campus_dir = f"result_outputs_post_files/{campus_code} - {campus_name}, {campus_address}".strip()

            os.makedirs("result_outputs", exist_ok=True)
            os.makedirs("result_outputs_post_files", exist_ok=True)
            os.makedirs(f"{campus_dir}", exist_ok=True)

            text_file = open(f"result_outputs/{campus_code}.txt", "w")
            html_file = open(f"result_outputs/{campus_code}.html", "w")

            text_file.write(text_file_content)
            html_file.write(html_file_content)

            text_file.close()
            html_file.close()

            weasyprint.HTML(f'result_outputs/{campus_code}.html').write_pdf(f'result_outputs/{campus_code}.pdf')
            images = pdf2image.convert_from_path(f'result_outputs/{campus_code}.pdf')
            for i in range(len(images)):
                images[i].save(f'{campus_dir}/Page {i + 1}.jpg', "JPEG")

            if drive_auth is not None:
                _folder_link, folder_id, file_link = upload_to_drive(drive_auth, [f"result_outputs/{campus_code}.pdf", f"result_outputs/{campus_code}.html", f"result_outputs/{campus_code}.txt"], f"{result_name} {year}", folder_id)
                if _folder_link is not None:
                    folder_link = _folder_link
                post_file_content.replace("<<replace_me>>", file_link)

            post_file = open(f"{campus_dir}/post_file.txt", "w")
            post_file.write(post_file_content)
            post_file.close()

    if mode == 2:
        # noinspection PyUnboundLocalVariable
        summary_db.commit()
        summary_db.close()

        print(f"\nTotal Unique Symbol Numbers: {len(merit_list)}")
        if len(unknown_campus_codes) > 0:
            print(f"You are missing campus codes of {len(unknown_campus_codes)} campuses:")
            for campus_code in unknown_campus_codes:
                print(f"\tCampus Code: {campus_code}")
                print(
                    f"\tTotal passed Students in {campus_code}: {len(campus_dict_to_work_on[campus_code]['merit_list'])}\n")
                # noinspection SqlDialectInspection,SqlNoDataSourceInspection

    if folder_link is None:
        upload_text = "Upload PDF, HTML, and TXT files of campus' result which are inside 'result_outputs' folder of your current directory to google drive."
        replace_text = "Replace <<replace_me>> in fifth line of 'result_outputs_post_files/<<campus_code>> - <<campus_name>>, <<campus_address>>/post_file.txt with the link copied for corresponding files to PDF.\n"
    else:
        upload_text = f"Files are upload to google drive. You can access them from here: {folder_link}"
        replace_text = ""

    print(f"\n\nDear admin, \n"
          f"{upload_text}\n"
          f"Share the files so anyone with the link may access them.\n"
          f"Copy the PDF links of each PDFs.\n"
          f"{replace_text}"
          f"Copy and paste whatever is in 'result_outputs_post_files/<<campus_code>> - <<campus_name>>, <<campus_address>>/post_file.txt' and post it in the facebook page after attaching photos in 'result_outputs_post_files/<<campus_code>> - <<campus_name>>, <<campus_address>>' folder of your current directory.")

    if mode == 2:
        print(f"\nA summary of the report is written in summary.db in current directory.")

    print(f"\n\tRegards\n\t-Gaurav Nyaupane\n\n")

    if len(new_campus_codes) > 0:
        print(f"New campus codes detected:")
    for campus_code in new_campus_codes:
        print(f"\t{campus_code}\n")
    if len(new_campus_codes) > 0:
        action = input_for_script(f"Do you want to add these campus codes to database? (Y/N) [default: {_action}]: ",
                                  _action)
        assert action in ["Y", "N"]
        if action.upper() == "Y":
            conn = sqlite3.connect('campus.db')
            for campus_code in new_campus_codes:
                campus_name = campus_dict_to_work_on[campus_code]["campus_name"]
                campus_address = campus_dict_to_work_on[campus_code]["campus_address"]
                # noinspection SqlDialectInspection,SqlNoDataSourceInspection
                conn.execute(
                    f"INSERT INTO campus(code,name,address) VALUES('{campus_code}', '{campus_name}','{campus_address}')")
            conn.commit()
            conn.close()


if __name__ == "__main__":
    publish_result("", 0)
