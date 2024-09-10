HTML_HEADER = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>$campus_name ($campus_code) : $result_name</title>
</head>
<body>
    <center>
    <table border='2px' style='margin-left: auto; margin-right: auto;'>
        <thead>
            <tr>
                <th colspan='3' style='text-align: center;'>
                    $result_name
                </th>
            </tr>
            <tr>
                <th colspan='3' style='text-align: center;'>
                    $campus_name ($campus_code)
                </th>
            </tr>
            <tr>
                <th colspan='3' style='text-align: center;'>
                    $campus_address
                </th>
            </tr>
            <tr>
                <th colspan='3' style='text-align: center;'>
                </th>
            </tr>
            <tr>
                <th style='text-align: center;'>
                    | Rank |
                </th>
                <th style='text-align: center;'>
                    | Campus Rank |
                </th>
                <th style='text-align: center;'>
                    | Symbol Number |
                </th>
            </tr>
        </thead>
        <tbody>
"""

HTML_FOOTER = """
        </tbody>
        <tfoot>
            <tr>
                <td colspan='3' style='text-align: center;'>
                    Total Passed students: $total_passed_students
                </td>
            </tr>
            <tr>
                <td colspan='3' style='text-align: center;'>
                    Total Passed students(This Campus): $total_passed_students_in_campus
                </td>
            </tr>
            <tr><td colspan='3'></td></tr>
            <tr><td colspan='3'></td></tr>
            <tr>
                <td colspan='3' style='text-align: center;'>
                    <small>Extracted using <a href='https://github.com/nightmaregaurav/result-extractor'>result-extractor</a></small>
                    <br>
                    <small>A tool by <a href='https://www.gauravnyaupane.com.np'>Gaurav Nyaupane</a></small>
                </td>
            </tr>
        </tfoot>
    </table>
    </center>
</body>
</html>
"""

HTML_BODY = """
            <tr>
                <td style='text-align: center;'>
                    $rank
                </td>
                <td style='text-align: center;'>
                    $campus_rank
                </td>
                <td style='text-align: center;'>
                    $symbol_number
                </td>
            </tr>
"""

SUMMARY_HTML_HEADER = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>$result_name : SUMMARY</title>
    <style type="text/css">
        @page {
            size: landscape;
        }
    </style>
</head>
<body>
    <center>
    <table border='2px' style='margin-left: auto; margin-right: auto;'>
        <thead>
            <tr>
                <th colspan='4' style='text-align: center;'>
                    $result_name : SUMMARY
                </th>
            </tr>
            <tr>
                <th colspan='4' style='text-align: center;'>
                </th>
            </tr>
            <tr>
                <th style='text-align: center;'>
                    | Code |
                </th>
                <th style='text-align: center;'>
                    | Name |
                </th>
                <th style='text-align: center;'>
                    | Address |
                </th>
                <th style='text-align: center;'>
                    | Passed |
                </th>
            </tr>
        </thead>
        <tbody>
"""

SUMMARY_HTML_FOOTER = """
        </tbody>
        <tfoot>
            <tr><td colspan='4'></td></tr>
            <tr><td colspan='4'></td></tr>
            <tr>
                <td colspan='4' style='text-align: center;'>
                    <small>Extracted using <a href='https://github.com/nightmaregaurav/result-extractor'>result-extractor</a></small>
                    <br>
                    <small>A tool by <a href='https://www.gauravnyaupane.com.np'>Gaurav Nyaupane</a></small>  
                </td>
            </tr>
        </tfoot>
    </table>
    </center>
</body>
</html>
"""

SUMMARY_HTML_BODY = """
            <tr>
                <td style='text-align: center;'>
                    $campus_code
                </td>
                <td style='text-align: left;'>
                    $campus_name
                </td>
                <td style='text-align: left;'>
                    $campus_address
                </td>
                <td style='text-align: center;'>
                    $total_passed_students
                </td>
            </tr>
"""
