import requests
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

STATUS_UNKNOWN = 0
STATUS_ACTIVE = 1
STATUS_WRONG_PASSWORD = 2
STATUS_ERROR = 3


def set_status(email, status, error_message=""):
    link = f"{os.getenv('MASTER_API')}/set-status/{email}/{status}?error_message={error_message}"
    return requests.get(link, headers={"APP_KEY": os.getenv('APP_KEY')})


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
