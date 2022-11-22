import re

from yaspin import yaspin
from yaspin.core import Yaspin


def get_user_input_or_set_default_with_validation(prompt_message: str, default_value: str, regex: str = ".*") -> str:
    if default_value != "" and default_value is not None:
        prompt_message += " [default: " + default_value + "]: "

    input_from_user: str = default_value

    first_time: bool = True
    while first_time or not re.match(regex, input_from_user):
        if not first_time:
            print(f"Invalid input `{input_from_user}` for pattern `{regex}`. Please try again.")
        first_time = False

        user_input: str = input(prompt_message)
        input_from_user = user_input if user_input.strip() != "" else default_value

    return input_from_user.strip()


def get_repeated_contents_from_list(main_list: list) -> list:
    return list(set([x for x in main_list if main_list.count(x) > 1]))


def filter_duplicates_from_list(input_list: list) -> list:
    filtered_list: list = []
    for item in input_list:
        if item not in filtered_list:
            filtered_list.append(item)
    return filtered_list


def start_progress_spinner(message: str):
    sp: Yaspin = yaspin(text=message, color="yellow")
    return sp


def stop_progress_spinner(spinner: Yaspin, message: str = "") -> None:
    spinner.ok("✔ " + message)
