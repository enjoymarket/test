import requests
import os
# import httpx
from dotenv import load_dotenv

load_dotenv()

STATUS_UNKNOWN = 0
STATUS_ACTIVE = 1
STATUS_WRONG_PASSWORD = 2
STATUS_ERROR = 3


def set_status(email, status, error_message=""):
    link = f"{os.getenv('MASTER_API')}/set-status/{email}/{status}?error_message={error_message}"
    return requests.get(link, headers={"APP_KEY": os.getenv('APP_KEY')})


def get_user_agent(email):
    link = f"{os.getenv('MASTER_API')}/get-user-agent/{email}"
    return requests.get(link, headers={"APP_KEY": os.getenv('APP_KEY')}).text


def set_current_process(email, message=""):
    link = f"{os.getenv('MASTER_API')}/set-current-process/{email}?message={message}"
    return requests.get(link, headers={"APP_KEY": os.getenv('APP_KEY')})


def set_password(email, password):
    link = f"{os.getenv('MASTER_API')}/set-password/{email}/{password}"
    return requests.get(link, headers={"APP_KEY": os.getenv('APP_KEY')})


def set_recovery_email(email, recovery_email):
    link = f"{os.getenv('MASTER_API')}/set-recovery-email/{email}/{recovery_email}"
    return requests.get(link, headers={"APP_KEY": os.getenv('APP_KEY')})


def get_operation(id):
    link = f"{os.getenv('MASTER_API')}/get-operation/{id}"
    try:
        return requests.get(link, headers={"APP_KEY": os.getenv('APP_KEY')}).json()
    except:
        return None


def get_login_info(id):
    link = f"{os.getenv('MASTER_API')}/get-login-info/{id}"
    return requests.get(link, headers={"APP_KEY": os.getenv('APP_KEY')})


def get_from(id):
    link = f"{os.getenv('MASTER_API')}/get-from/{id}"
    response = requests.get(link, headers={"APP_KEY": os.getenv('APP_KEY')})
    print(response.text)
    if response.text == "0":
        return None
    return response.json()


def get_reply_subject(id):
    link = f"{os.getenv('MASTER_API')}/get-reply-subject/{id}"
    # print(f'subject link {link}')
    return requests.get(link, headers={"APP_KEY": os.getenv('APP_KEY')}).text


def get_reply_body(id):
    link = f"{os.getenv('MASTER_API')}/get-reply-body/{id}"
    return requests.get(link, headers={"APP_KEY": os.getenv('APP_KEY')}).json()


def get_reply_operation_status(id):
    link = f"{os.getenv('MASTER_API')}/get-reply-operation-status/{id}"
    return requests.get(link, headers={"APP_KEY": os.getenv('APP_KEY')}).text


def increase_total_replies(email):
    link = f"{os.getenv('MASTER_API')}/increase-total-replies/{email}"
    return requests.get(link, headers={"APP_KEY": os.getenv('APP_KEY')}).text


def add_blocked_sender(email, sender):
    link = f"{os.getenv('MASTER_API')}/add-blocked-sender/{email}/{sender}"
    return requests.get(link, headers={"APP_KEY": os.getenv('APP_KEY')}).text


def is_sender_blocked(email, sender):
    link = f"{os.getenv('MASTER_API')}/is-sender-blocked/{email}/{sender}"
    if requests.get(link, headers={"APP_KEY": os.getenv('APP_KEY')}).text == '1':
        return True
    return False


def add_bounce(email):
    link = f"{os.getenv('MASTER_API')}/add-bounce/{email}"
    return requests.get(link, headers={"APP_KEY": os.getenv('APP_KEY')}).text


def is_bounce(email):
    link = f"{os.getenv('MASTER_API')}/is-bounce/{email}"
    if requests.get(link, headers={"APP_KEY": os.getenv('APP_KEY')}).text == '1':
        return True
    return False


def set_limit_exceeded(email):
    link = f"{os.getenv('MASTER_API')}/set-limit-exceeded/{email}"
    return requests.get(link, headers={"APP_KEY": os.getenv('APP_KEY')})


def is_limit_exceeded(email):
    link = f"{os.getenv('MASTER_API')}/is-limit-exceeded/{email}"
    return int(requests.get(link, headers={"APP_KEY": os.getenv('APP_KEY')}).text)
