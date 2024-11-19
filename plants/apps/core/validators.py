from django.core.exceptions import ValidationError


def str_checker(value):

    numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    name_list = list(value)

    for letter in name_list:
        if letter in numbers:
            raise ValidationError("name must contain only charecters")


def special_characters_check(value):
    sp_char = [
        "!",
        "@",
        "#",
        "$",
        "%",
        "^",
        "&",
        "*",
        "()",
        "-",
        "+",
        "=",
        "/",
        "?",
        ">",
        "<",
        ",",
        ".",
        "|",
        "~",
    ]
    point = 0
    for element in value:
        if element in sp_char:
            point += 1
    if point == 0:
        raise ValidationError("password must contain at least one special character !")
