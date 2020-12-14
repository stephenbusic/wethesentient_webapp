import re

def validate_email(email):
    if email is None:
        return "Email is required."
    elif not re.match(r"^\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$", email):
        return "Invalid Email Address."
    else:
        return None