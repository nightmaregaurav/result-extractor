import re


def get_campus_code_from_student_code(student_code: str, pattern_with_group_to_get_campus_code: str) -> int:
    campus_code: int = 0
    match: re.Match = re.search(pattern_with_group_to_get_campus_code, student_code)
    if match is not None:
        campus_code = int(match.group(1))
    return campus_code
