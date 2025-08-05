import random
import re


def generate_password(name: str, mobile_number: str) -> dict:
    if not name or not mobile_number:
        return {
            "valid": False,
            "password": None,
            "message": "Name or mobile number is missing.",
        }

    formatted_name = name.replace(" ", "")
    capitalized_name = formatted_name.capitalize()

    first_part = capitalized_name[:3]
    while len(first_part) < 3:
        first_part += str(random.randint(0, 9))

    last_four_digits = mobile_number[-4:]

    password = f"{first_part}@{last_four_digits}"

    password_regex = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@]).{8,}$")
    if not password_regex.match(password):
        return {
            "valid": False,
            "password": None,
            "message": "Password does not meet the required criteria.",
        }

    return {
        "valid": True,
        "password": password,
        "message": "Password generated successfully.",
    }
