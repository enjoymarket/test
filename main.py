import os, sys, getopt, json
from os.path import exists
import time
from datetime import datetime
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


@app.get("/kill/{email}")
def kill(email):
    os.system("pkill chrome")
    api.set_current_process(email, '')


@app.get("/screen")
def screen():
    file_name = 'screen.png'
    if exists(file_name):
        return FileResponse(path=file_name, filename=file_name, media_type='image/png')
    else:
        return 'File not found'


@app.get("/logs")
def logs():
    file_name = 'logs.txt'
    if exists(file_name):
        return FileResponse(path=file_name, filename=file_name, media_type='image/txt')
    else:
        return 'File not found'


@app.get("/login/{id}")
async def login(id: int, background_tasks: BackgroundTasks):
    background_tasks.add_task(do_login, id)
    # do_login(id)
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
                    api.set_current_process(profile.get('email'), 'Change Language to English...')
                    gmail.change_language('English', 'United States')
                    api.set_current_process(profile.get('email'), 'Delete all filters...')
                    gmail.delete_all_filters()
                    api.set_current_process(profile.get('email'), 'Create inbox filter...')
                    gmail.create_filter_for_reply()
                    api.set_current_process(profile.get('email'), 'Read Security Alert emails...')
                    gmail.security_alert()
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
                driver.save_screenshot('screen.png')
                with open('logs.txt', 'a+') as f:
                    f.write(f'{ex}\n')
                    f.flush()
                    f.close()
                api.set_current_process(profile.get('email'), 'Error: Somethings wrong!')
                return ex


@app.get("/reply/{account_id}/{reply_id}")
async def reply(account_id, reply_id, background_tasks: BackgroundTasks):
    background_tasks.add_task(do_reply, account_id, reply_id)
    # do_reply(account_id, reply_id)
    return {"message": "The operation will be processed in the background"}


def do_reply(account_id, reply_id):
    result = api.get_login_info(account_id)
    if result.text != '[]':
        profile = json.loads(result.text)
        while True:
            driver = get_driver(profile.get('email'))
            # return True
            gmail = Gmail(driver, profile.get('email'), profile.get('password'), profile.get('recovery_email'))
            # try:
            api.set_current_process(profile.get('email'), 'do login...')
            print('do login')
            gmail.go_to_login_page()
            login_result = gmail.do_login()
            if login_result is True:
                random_sleep(4, 6)
                if gmail.is_account_need_rest():
                    time.sleep(900)
                from_response = api.get_from(reply_id)
                if from_response is not None:
                    api.set_current_process(profile.get('email'), 'setup new from name and from email...')
                    gmail.set_new_from(from_response.get('from_name'), from_response.get('from_email'))

                subject = api.get_reply_subject(reply_id)

                count = 0
                pack_count_for_check = 0
                pack_count_for_limit = 0

                # do bounce, block, limit check in certain moment
                do_check = random.randint(3, 10)
                limit_check = 3
                print(f'Do Check after {do_check} replies pack')

                # reply_pack mean how many replies in reply_seconds
                reply_pack = 3
                reply_seconds = 60

                start_datetime = datetime.now()
                print(f'Start datetime: {start_datetime}')
                while True:
                    try:
                        # Sleep when the limit is exceeded
                        time.sleep(api.is_limit_exceeded(profile.get('email')))

                        status = api.get_reply_operation_status(reply_id)
                        print(f'Status => {status}')
                        if int(status) == 2:
                            print('paused')
                            api.set_current_process(profile.get('email'), 'Replies paused...')
                            time.sleep(10)
                            continue
                        elif int(status) == 0:
                            api.set_current_process(profile.get('email'), 'Replies stopped...')
                            break
                        elif int(status) == 1:
                            print('Reply process')
                            if count < reply_pack:
                                api.set_current_process(profile.get('email'), 'Filter By Subject...')
                                print(f'Filter By this subject: {subject}')
                                gmail.filter_by_subject(subject=subject)

                                random_sleep(1, 3)
                                first_message = gmail.get_message_number(1)
                                print(f'first msg => {first_message}')
                                if first_message is not False:
                                    first_message.click()
                                    api.set_current_process(profile.get('email'), 'Doing replies...')
                                    body = api.get_reply_body(reply_id)
                                    if gmail.reply(body.get('body'), body.get('attachment')):
                                        api.increase_total_replies(profile.get('email'))
                                        count = count + 1
                                else:
                                    if gmail.is_account_need_rest(True):
                                        time.sleep(900)
                                    else:
                                        print('Finish!')
                                        break

                            if count == reply_pack:
                                count = 0
                                pack_count_for_check = pack_count_for_check + 1
                                pack_count_for_limit = pack_count_for_limit + 1

                                if pack_count_for_limit == limit_check:
                                    pack_count_for_limit = 0
                                    api.set_current_process(profile.get('email'), 'Check for bounce messages...')
                                    print('Check for bounce messages...')
                                    if gmail.detect_limit():
                                        print('Enter to if: limit')
                                        api.set_limit_exceeded(profile.get('email'))

                                if pack_count_for_check == do_check:
                                    pack_count_for_check = 0
                                    do_check = random.randint(3,  10)
                                    api.set_current_process(profile.get('email'), 'Check if sender was blocked...')
                                    print('Check if sender was blocked...')
                                    blocked_senders = gmail.detect_sender_blocked()
                                    if blocked_senders is not None:
                                        print('Enter to if: blocked sender')
                                        for blocked_sender in blocked_senders:
                                            api.add_blocked_sender(blocked_sender.get('email'),
                                                                   blocked_sender.get('sender'))

                                    api.set_current_process(profile.get('email'), 'Check for bounce messages...')
                                    print('Check for bounce messages...')
                                    bounces = gmail.detect_bounce()
                                    if bounces is not None:
                                        print('Enter to if: bounce')
                                        for bounce in bounces:
                                            api.add_bounce(bounce)

                                    print(f'Do Check after {do_check} replies pack')

                                # Calculate the difference between first reply and last reply it should be more than 60s
                                end_datetime = datetime.now()
                                difference = end_datetime - start_datetime
                                if difference.total_seconds() < reply_seconds:
                                    # sleep the rest of seconds
                                    print(f'Sleeping {reply_seconds - difference.total_seconds()} seconds')
                                    time.sleep(reply_seconds - difference.total_seconds())
                                start_datetime = datetime.now()
                                print(f'End datetime: {end_datetime}')
                                print(f'--------------------------------')
                                print(f'Start datetime: {start_datetime}')
                    except TimeoutError as error:
                        print('Timeout Error')

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
            # except Exception as ex:
            #     driver.save_screenshot('screen.png')
            #     with open('logs.txt', 'a+') as f:
            #         f.write(f'{ex}\n')
            #         f.flush()
            #         f.close()
            #     api.set_current_process(profile.get('email'), 'Error: Somethings wrong!')
            #     gmail.quit()
            #     return ex


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

    ua = api.get_user_agent(email)
    options.add_argument(f"--user-agent={ua}")

    options.add_argument(f"--user-data-dir={os.path.join(os.path.dirname(__file__), 'profiles', email)}")
    # options.add_argument(f"--profile-directory=Default")

    options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
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
    driver = uc.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=options)
    # driver = uc.Chrome(options=options)

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
