import sqlite3
import os
import weasyprint
import pdf2image

original_input = input


# noinspection PyShadowingBuiltins
def input(text, default):
    if __name__ == "__main__":
        return original_input(text)
    else:
        return default


def publish_result(_year, _campus_code, _campus_name="", _campus_address="", _mode="2", _action="N"):
    _campus_code = int(_campus_code)
    _campus_name = str(_campus_name)
    _campus_address = str(_campus_address)
    _year = str(_year)
    _mode = str(_mode)
    _action = str(_action)

    result_file = open("BCA_RESULT_ALL_RAW.txt")
    merit_list = [symbol_no.strip() for symbol_no in result_file]
    result_file.close()

    merit_set = set(merit_list)
    if len(merit_list) != len(merit_set):
        print(f"Total Repeated Symbol Numbers: {len(merit_list) - len(merit_set)}")
        print(f"Repeated Symbol Numbers: ")
        repeated = set([x for x in merit_list if merit_list.count(x) > 1])
        for sym in repeated:
            print(f"{sym}, ")

    year = input("Input Result Year: ", _year)
    mode = input("What do you want to do?\n"
                 "\t1. Publish single result of new campus.\n"
                 "\t2. Publish single result of old campus.\n"
                 "\t3. Publish result of all campuses in db.\n"
                 "Your Input [default: 3] >>> ", _mode)

    campus_list = dict()
    if mode == '1':
        __cc = input("Input the symbol no of campus(eg. 02): ", _campus_code)
        campus_list[int(__cc)] = {
            'campus_name': input("Input the name campus(eg. Mechi Multiple Campus): ", _campus_name),
            'campus_address': input("Input the address campus(eg. Bhadrapur, Jhapa.): ", _campus_address),
            'merit_list': list()
        }
    elif mode == '2':
        conn = sqlite3.connect('campus.db')
        __cc = input("Input the symbol no of campus(eg. 02): ", _campus_code)
        # noinspection SqlDialectInspection,SqlNoDataSourceInspection
        cursor = conn.execute(f'''SELECT code, name, address from campus WHERE code = "{int(__cc)}"''')
        row = cursor.fetchone()
        if row is None:
            raise ValueError("Given campus code does not exist in database.")
        campus_list[int(row[0])] = {
            'campus_name': row[1],
            'campus_address': row[2],
            'merit_list': list()
        }
        conn.close()
    else:
        conn = sqlite3.connect('campus.db')
        # noinspection SqlDialectInspection,SqlNoDataSourceInspection
        cursor = conn.execute("SELECT code, name, address from campus ORDER BY code")
        for row in cursor:
            campus_list[int(row[0])] = {
                'campus_name': row[1],
                'campus_address': row[2],
                'merit_list': list()
            }
        conn.close()

    tu_rank = 0
    for symbol_no in merit_set:
        tu_rank += 1
        campus_code = int(symbol_no.split("-")[0])
        try:
            campus_list[campus_code]['merit_list'].append({"tu_rank": tu_rank, "symbol_no": symbol_no})
        except KeyError:
            campus_list[campus_code] = {}
            campus_list[campus_code]['merit_list'] = list()
            campus_list[campus_code]['merit_list'].append({"tu_rank": tu_rank, "symbol_no": symbol_no})

    unknown_campus_list = list()
    if mode != '1' and mode != '2':
        try:
            os.remove("summary.db")
        except FileNotFoundError:
            pass

        summary_db = sqlite3.connect('summary.db')
        summary_cursor = summary_db.cursor()
        # noinspection SqlNoDataSourceInspection,SqlDialectInspection
        summary_cursor.execute('''CREATE TABLE IF NOT EXISTS "summary" ("code" INTEGER NOT NULL UNIQUE, "name" TEXT, "address" TEXT, "passed students" INTEGER NOT NULL, PRIMARY KEY("code"))''')
        summary_db.commit()

    for campus_code in campus_list:
        try:
            campus_name = campus_list[campus_code]['campus_name']
            campus_name = " ".join(campus_name.replace(" ,", ",").replace(",", ", ").split()).title()
            _campus_name = campus_name
            campus_address = campus_list[campus_code]['campus_address']
            campus_address = " ".join(campus_address.replace(" ,", ",").replace(",", ", ").split()).title()
            _campus_address = campus_address
        except KeyError:
            unknown_campus_list.append(campus_code)
            continue

        text_file_content = f"BCA Entrance Result: {year}\n" \
                            f"Campus: {campus_name}\n" \
                            f"Address: {campus_address}\n" \
                            f"Code: {campus_code}\n"
        html_file_content = "<!DOCTYPE html>\n" \
                            "<html>\n" \
                            "<head>\n" \
                            f"	<title>{campus_code} BCA Entrance Result: {year}</title>\n" \
                            "</head>\n" \
                            "<body>\n" \
                            "	<center>\n" \
                            "		<table border='2px' style='margin-left: auto; margin-right: auto;'>\n" \
                            "			<thead>\n" \
                            "				<tr>\n" \
                            "					<th colspan='3'>\n" \
                            f"						BCA Entrance Result: {year}\n" \
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
                            "						| All Nepal Rank |\n" \
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
        text_file_content += "\nAllNepalRank\t CampusRank\t SymbolNo\n"
        campus_rank = 0
        campus_merit_list: list = campus_list[campus_code]['merit_list']
        for entry in campus_merit_list:
            campus_rank += 1

            tu_rank = entry['tu_rank']
            symbol_no = entry['symbol_no']

            text_file_content += f"{tu_rank}\t {campus_rank}\t {symbol_no}\n"
            html_file_content += "<tr>\n" \
                                 f"	<td>{tu_rank}</td>\n" \
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
        post_file_content += f"Total Passed student(TU): {len(merit_set)}\n" \
                             f"Total Passed student(This Campus): {campus_rank}\n\n" \
                             f"Search your campus' result using hashtag<campus code>(eg. #BCA{year}TU_{campus_code})\n" \
                             f"If result for your campus is not published, inbox us your campus' code/symbol no to get it published.\n" \
                             f"#BCA #EntranceResult{year} #BCATU\n\n" \
                             f"Extracted By: Gaurav Nyaupane (MMC BCA 2017)"
        text_file_content += f"\nTotal Passed student(TU): {len(merit_set)}" \
                             f"\nTotal Passed student(This Campus): {campus_rank}" \
                             f"\n\nExtracted By: Gaurav Nyaupane (MMC BCA 2017)"
        print(f"Total Passed Students in ({campus_code}) {campus_name}, {campus_address}: {campus_rank}")
        if mode != '1' and mode != '2':
            # noinspection SqlDialectInspection,SqlNoDataSourceInspection,PyUnboundLocalVariable
            summary_cursor.execute(f"INSERT INTO summary VALUES({campus_code}, '{campus_name}', '{campus_address}', {campus_rank})")

        if campus_rank != 0:
            os.makedirs("result_outputs", exist_ok=True)
            os.makedirs("result_outputs_post_files", exist_ok=True)
            post_file = open(f"result_outputs_post_files/{campus_code}_post_file.txt", "w")
            text_file = open(f"result_outputs/{campus_code}.txt", "w")
            html_file = open(f"result_outputs/{campus_code}.html", "w")

            post_file.write(post_file_content)
            text_file.write(text_file_content)
            html_file.write(html_file_content)

            post_file.close()
            text_file.close()
            html_file.close()

            weasyprint.HTML(f'result_outputs/{campus_code}.html').write_pdf(f'result_outputs/{campus_code} - {_campus_name}, {_campus_address}'.strip() + '.pdf')

            os.makedirs(f"result_outputs_post_files/{campus_code} - {_campus_name}, {_campus_address}".strip(), exist_ok=True)
            images = pdf2image.convert_from_path(f'result_outputs/{campus_code} - {_campus_name}, {_campus_address}'.strip() + '.pdf')
            for i in range(len(images)):
                images[i].save(f'result_outputs_post_files/{campus_code} - {_campus_name}, {_campus_address}'.strip() + '/Page {i+1}.jpg', "JPEG")

        if mode == '1':
            conn = sqlite3.connect('campus.db')
            # noinspection SqlDialectInspection,SqlNoDataSourceInspection
            cursor = conn.execute(f"SELECT COUNT(*) FROM campus where code = '{campus_code}'")
            count = cursor.fetchone()[0]

            if count == 0:
                action = input("Do you want to save this campus? (Y for yes): ", _action)
            else:
                action = input("Do you want to update this campus with new details? (Y for yes): ", _action)

            if action.lower() == 'y':
                if count == 0:
                    # noinspection SqlDialectInspection,SqlNoDataSourceInspection
                    conn.execute(
                        f"INSERT INTO campus(code,name,address) VALUES('{campus_code}', '{campus_name}','{campus_address}')")
                else:
                    # noinspection SqlDialectInspection,SqlNoDataSourceInspection
                    conn.execute(
                        f"UPDATE campus SET name = '{campus_name}', address = '{campus_address}' WHERE code = '{campus_code}'")

                conn.commit()

            conn.close()

    if mode != '1' and mode != '2':
        print(f"\nTotal Unique Symbol Numbers: {len(merit_set)}")
        if len(unknown_campus_list) > 0:
            print(f"You are missing campus codes of {len(unknown_campus_list)} campuses:")
            for campus_code in unknown_campus_list:
                print(f"\tCampus Code: {campus_code}")
                print(f"\tTotal passed Students in {campus_code}: {len(campus_list[campus_code]['merit_list'])}\n")
                # noinspection SqlDialectInspection,SqlNoDataSourceInspection
                summary_cursor.execute(f"INSERT INTO summary VALUES({campus_code}, '', '', {len(campus_list[campus_code]['merit_list'])})")

        # noinspection PyUnboundLocalVariable
        summary_db.commit()
        summary_db.close()

    print(f"\n\nDear admin, \n"
          f"Upload PDF, HTML, and TXT files of campus' result which are inside 'result_outputs' folder of your current directory to google drive.\n"
          f"Share the files so anyone with the link may access them.\n"
          f"Copy the PDF links of each PDFs.\n"
          f"Replace <<replace_me>> in fifth line of 'result_outputs_post_files/<<campus_code>>_post_file.txt with the link copied for corresponding files to PDF.\n"
          f"Copy and paste whatever is in 'result_outputs_post_files/<<campus_code>>_post_file.txt' and post it in the facebook page after attaching photos in 'result_outputs_post_files/<<campus_code>> - <<campus_name>>, <<campus_address>>' folder of your current directory.")

    if mode != '1' and mode != '2':
        print(f"A summary of the report is written in summary.db in current directory.")

    print(f"\n\tRegards\n\t-Gaurav Nyaupane\n\n")


if __name__ == "__main__":
    publish_result("", 0)
