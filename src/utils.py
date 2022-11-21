import re


def get_user_input_or_set_default_with_validation(prompt_message: str, default_value: str, regex: str = ".*", name: str = None) -> str:
    if default_value != "" and default_value is not None:
        prompt_message += " [default: " + default_value + "]: "

    input_from_user: str = default_value

    if name == "__main__":
        first_time: bool = True
        while first_time or not re.match(regex, input_from_user):
            if not first_time:
                print("Invalid input. Please try again.")
            input_from_user = input(prompt_message)

    return input_from_user.strip()


def get_repeated_contents_from_list(main_list: list) -> list:
    return list(set([x for x in main_list if main_list.count(x) > 1]))


def filter_duplicates_from_list(input_list: list) -> list:
    filtered_list: list = []
    for item in input_list:
        if item not in filtered_list:
            filtered_list.append(item)
    return filtered_list
