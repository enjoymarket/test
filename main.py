import os, sys, getopt, json
from os.path import exists
import time
from concurrent.futures import ThreadPoolExecutor
import requests
# from starlette.exceptions import HTTPException
import undetected_chromedriver as uc
# from selenium import webdriver as uc
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
from fastapi.responses import FileResponse
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def index():
    return "Hello, this is the index page, that's mean that all things are installed fine!"


@app.get("/screen")
def screen():
    file_name = 'screen.png'
    if exists(file_name):
        return FileResponse(path=file_name, filename=file_name, media_type='image/png')
    else:
        return 'File not found'


@app.get("/login/{id}")
async def login(id: int, background_tasks: BackgroundTasks):
    background_tasks.add_task(do_login, id)
    return {"message": "The operation will be processed in the background"}


def do_login(id):
    result = api.get_login_info(id)
    if result.text != '[]':
        profile = json.loads(result.text)
        while True:
            driver = get_driver(profile.get('email'))
            # return True
            gmail = Gmail(driver, profile.get('email'), profile.get('password'), profile.get('recovery_email'))
            api.set_current_process(profile.get('email'), 'do login...')
            gmail.go_to_login_page()
            try:
                login_result = gmail.do_login()
                driver.save_screenshot('screen.png')
                if login_result is True:
                    time.sleep(5)
                    driver.close()
                    time.sleep(5)
                    driver.quit()
                    api.set_current_process(profile.get('email'), '')
                    return True
                elif login_result == "Captcha":
                    driver.quit()
                    continue
                else:
                    time.sleep(1)
                    driver.quit()
                    api.set_current_process(profile.get('email'), 'Logged Process terminated, in failed.')
                    return False
            except Exception as ex:
                return ex


@app.get("/reply/{account_id}/{reply_id}")
async def reply(account_id, reply_id, background_tasks: BackgroundTasks):
    background_tasks.add_task(do_reply, account_id, reply_id)
    return {"message": "The operation will be processed in the background"}


def do_reply(account_id, reply_id):
    result = api.get_login_info(account_id)
    if result.text != '[]':
        profile = json.loads(result.text)
        while True:
            driver = get_driver(profile.get('email'))
            # return True
            gmail = Gmail(driver, profile.get('email'), profile.get('password'), profile.get('recovery_email'))
            try:
                api.set_current_process(profile.get('email'), 'do login...')
                gmail.go_to_login_page()
                login_result = gmail.do_login()
                if login_result is True:
                    random_sleep(4, 6)
                    api.set_current_process(profile.get('email'), 'setup new from name and from email...')
                    from_response = api.get_from(reply_id)
                    gmail.set_new_from(from_response.get('from_name'), from_response.get('from_email'))

                    api.set_current_process(profile.get('email'), 'Filter By Subject...')
                    subject = api.get_reply_subject(reply_id)
                    gmail.filter_by_subject(subject=subject)
                    while True:
                        # try:
                        random_sleep(1, 3)
                        driver.refresh()
                        first_message = gmail.get_message_number(1)
                        if first_message is not False:
                            first_message.click()
                            status = api.get_reply_operation_status(reply_id)
                            if int(status) == 1:
                                api.set_current_process(profile.get('email'), 'Doing replies...')
                                body = api.get_reply_body(reply_id)
                                gmail.reply(body.get('body'), body.get('attachment'))
                                api.increase_total_replies(profile.get('email'))
                                time.sleep(1)
                                gmail.inside_delete_button()
                            elif int(status) == 2:
                                print('paused')
                                api.set_current_process(profile.get('email'), 'Replies paused...')
                                time.sleep(5)
                            elif int(status) == 0:
                                api.set_current_process(profile.get('email'), 'Replies stopped...')
                                break
                        else:
                            break
                        # except:
                        #     break

                    time.sleep(5)
                    driver.quit()
                    api.set_current_process(profile.get('email'), '')
                    return True
                elif login_result == "Captcha":
                    driver.quit()
                    continue
                else:
                    time.sleep(1)
                    driver.quit()
                    api.set_current_process(profile.get('email'), 'Logged Process terminated, in failed.')
                    return False
            except:
                driver.save_screenshot('screen.png')
                gmail.quit()


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


def random_sleep(x, y):
    time.sleep(random.uniform(x, y))


def get_driver(email):
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    options.add_argument("--disable-pu")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-extensions")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-device-discovery-notifications")
    options.add_argument("--dns-prefetch-disable")
    options.add_argument("--single-process")
    options.add_argument("--disk-cache-size=0")
    options.add_argument("--lang=en")
    options.add_argument("log-level=3")
    options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/37.0.2062.94 Chrome/81.0.4044.113 Safari/537.36")

    options.add_argument(f"--user-data-dir={os.path.join(os.path.dirname(__file__), 'profiles', email)}")
    # options.add_argument(f"--profile-directory=Default")

    # options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    # options.add_argument('--no-first-run --no-service-autorun --password-store=basic')
    # options.add_argument(f"--start-maximized")
    # options.add_argument(
    #     f"--user-data-dir={os.path.join(os.path.dirname(__file__), 'profiles', email)}")
    # options.add_argument(f"--user-agent={ua.chrome()}")
    # user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
    # options.add_argument(f"--user-agent={user_agent}")
    # options.add_argument('--headless')
    # options.add_argument('--no-sandbox')
    # options.add_argument('--disable-dev-shm-usage')

    options.page_load_strategy = 'eager'
    # driver = uc.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=options)
    driver = uc.Chrome(options=options)

    # stealth(driver,
    #         languages=["en-US", "en"],
    #         vendor="Google Inc.",
    #         platform="Win32",
    #         webgl_vendor="Google Inc. (NVIDIA)",
    #         renderer="ANGLE (NVIDIA, NVIDIA Quadro 2000 Direct3D11 vs_5_0 ps_5_0, D3D11)",
    #         fix_hairline=False,
    #         )

    # driver.get('https://bot.sannysoft.com')
    # time.sleep(5)
    # driver.save_screenshot('screen.png')
    #
    # driver.quit()

    driver.set_page_load_timeout(30)
    handles = driver.window_handles
    if len(handles) > 1:
        driver.close()
        handles = driver.window_handles
        driver.switch_to.window(handles[0])
    return driver

# if __name__ == '__main__':
#     login_normal()
    # creatives = get_creatives()
    # processes = open('accounts.txt')
    # for process in processes:
    #     reply(process, creatives)
