from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def str_checker(value):

    numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    name_list = list(value)

    for letter in name_list:
        if letter in numbers:
            raise ValidationError(_("name must contain only characters"))


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
        '_',
    ]
    point = 0
    for element in value:
        if element in sp_char:
            point += 1
    if point == 0:
        raise ValidationError(_("password must contain at least one special character !"))
