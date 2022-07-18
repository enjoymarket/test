import os, sys, getopt, json
import time
from concurrent.futures import ThreadPoolExecutor
import requests
# from starlette.exceptions import HTTPException
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
from api import api
from Gmail import Gmail
import httpx
import random
from dotenv import load_dotenv
load_dotenv()

from fastapi import BackgroundTasks, FastAPI
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def index():
    return "Hello, this is the index page, that's mean that all things are installed fine!"


@app.get("/login/{id}")
def login(id: int):
    result = api.get_login_info(id)
    if result.text != '[]':
        profile = json.loads(result.text)
        while True:
            driver = get_driver(profile.get('email'))
            return 'Finish!'
        # return 'finish!'
        # gmail = Gmail(driver, profile.get('email'), profile.get('password'), profile.get('recovery_email'))
        # api.set_current_process(profile.get('email'), 'do login...')
        # gmail.go_to_login_page()
        # login_result = gmail.do_login()
        # if login_result is True:
        #     time.sleep(1)
        #     driver.close()
        #     time.sleep(5)
        #     driver.quit()
        #     api.set_current_process(profile.get('email'), '')
        #     return True
        # elif login_result == "Captcha":
        #     driver.quit()
        #     continue
        # else:
        #     time.sleep(1)
        #     driver.quit()
        #     api.set_current_process(profile.get('email'), '')
        #     return False


def random_sleep(x, y):
    time.sleep(random.uniform(x, y))


def get_driver(email):
    options = Options()
    options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    options.add_argument('--no-first-run --no-service-autorun --password-store=basic')
    options.add_argument(f"--start-maximized")
    options.add_argument(
        f"--user-data-dir={os.path.join(os.path.dirname(__file__), 'profiles', email)}")
    # options.add_argument(f"--user-agent={ua.chrome()}")
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    options.page_load_strategy = 'eager'
    driver = uc.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=options)

    driver.get('https://www.google.com')
    driver.save_screenshot('screen.png')

    # stealth(driver,
    #         languages=["en-US", "en"],
    #         vendor="Google Inc.",
    #         platform="Win32",
    #         webgl_vendor="Intel Inc.",
    #         renderer="Intel Iris OpenGL Engine",
    #         fix_hairline=True,
    #         )
    driver.set_page_load_timeout(30)
    handles = driver.window_handles
    if len(handles) > 1:
        driver.close()
        handles = driver.window_handles
        driver.switch_to.window(handles[0])
    return driver


# def login(profile):
#     email, password, recovery_email = profile.split(';')
#     while True:
#         driver = get_driver(email)
#         gmail = Gmail(driver, email, password, recovery_email)
#         gmail.go_to_login_page()
#         login_result = gmail.do_login()
#         if login_result is True:
#             time.sleep(1)
#             return gmail
#         elif login_result == "Captcha":
#             driver.quit()
#             continue
#         else:
#             time.sleep(1)
#             driver.quit()
#             return False


def get_creatives():
    rootdir = 'creatives'
    creatives = []
    for file in os.listdir(rootdir):
        d = os.path.join(rootdir, file)
        if os.path.isdir(d):
            try:
                subject = open(f'{os.path.join(os.path.dirname(__file__), d, "subject.txt")}').read()
                creative = open(f'{os.path.join(os.path.dirname(__file__), d, "creative.txt")}').read()
                creatives.append({
                    'subject': subject,
                    'creative': creative
                })
            except:
                pass
    return creatives


def get_creative(creatives, subject):
    for creative in creatives:
        if creative.get('subject') in subject:
            return creative.get('creative')
    return None


def reply(profile, creatives):
    gmail = login(profile)
    if gmail is not False:
        while True:
            # try:
            random_sleep(1, 3)
            first_message = gmail.get_message_number(1)
            first_message.click()
            subject = gmail.inside_get_subject()
            creative = get_creative(creatives, subject)
            if creative is not None:
                # random_sleep(1, 2)
                gmail.reply(creative)
            time.sleep(1)
            gmail.inside_delete_button()

            # time.sleep(3)
            # gmail.quit()
            # except:
            #     pass


# if __name__ == '__main__':
#     creatives = get_creatives()
#     processes = open('accounts.txt')
#     for process in processes:
#         reply(process, creatives)
