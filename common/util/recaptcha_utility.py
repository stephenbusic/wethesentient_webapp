from django.conf import settings
import logging
import requests
import json


# Function to check if a given request passes recaptcha
def pass_recaptcha(request):
    try:
        result = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data={
                'secret': settings.RECAPTCHA_SECRET_KEY,
                'response': request.POST.get("g-recaptcha-response"),
            }
        ).content
    except ConnectionError:  # Handle your error state
        logging.getLogger("error").error("Connection error while trying to validate with Recaptcha!")
        result = ""

    # Will throw ValueError if we can't parse Google's response
    result = json.loads(result)

    # If recaptcha state is success and score is good, return true.
    return result['success'] and result['score'] >= 0.5
