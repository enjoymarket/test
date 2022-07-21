import random
import time
import urllib.parse
from urllib.error import URLError
from urllib.request import urlopen
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from api import api


def sleep():
    time.sleep(random.uniform(1, 5))


def random_sleep(x, y):
    time.sleep(random.uniform(x, y))


def wait_until_internet_connectivity_is_good():
    pass
    # while True:
    #     try:
    #         urlopen('https://api.ipify.org/', timeout=5)
    #         break
    #     except URLError as err:
    #         time.sleep(3)


class AnyEc:
    """ Use with WebDriverWait to combine expected_conditions
        in an OR.
    """

    def __init__(self, *args):
        self.ecs = args

    def __call__(self, driver):
        for fn in self.ecs:
            try:
                res = fn(driver)
                if res:
                    return True
                    # Or return res if you need the element found
            except:
                pass


class Gmail:
    def __init__(self, driver, email, password, recovery):
        self.driver = driver
        self.email = email
        self.password = password
        self.recovery = recovery

    def slow_type(self, element: WebElement, text: str, delay: float = 0.1):
        """Send a text to an element one character at a time with a delay."""
        for character in text:
            element.send_keys(character)
            time.sleep(delay)

    def wait_login_page_to_load(self):
        try:
            WebDriverWait(self.driver, 30).until(
                AnyEc(
                    EC.presence_of_element_located((By.XPATH, f'//div[@data-challengetype="12"]')),
                    EC.url_contains('https://mail.google.com/mail/'),
                    EC.url_contains('https://myaccount.google.com/signinoptions/recovery-options-collection'),
                    EC.url_contains('https://accounts.google.com/signin/v2/deniedsigninrejected'),
                    EC.url_contains('https://accounts.google.com/speedbump/idvreenable'),
                    EC.url_contains('https://accounts.google.com/signin/v2/disabled'),
                    EC.presence_of_element_located((By.XPATH, '//div[@jsname="h9d3hd"]//*[name()="svg"]')),
                    EC.presence_of_element_located((By.XPATH, '//div[@jsname="B34EJ"]//*[name()="svg"]')),
                    EC.presence_of_element_located((By.XPATH, '//img[@id="captchaimg" and @src]'))
                )
            )
            return True
        except:
            return False

    def wait_page_to_load(self):
        wait = WebDriverWait(self.driver, 15)
        try:
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            print("page loaded")
        except Exception as e:
            pass

    def wait_until_load_new_messages(self):
        while True:
            try:
                self.driver.find_element(By.XPATH, '//div[@class="vY"]/div[@style=""]')
                time.sleep(0.2)
            except:
                print('Loaded...')
                return True

    def go_to_login_page(self):
        wait_until_internet_connectivity_is_good()
        try:
            self.driver.get('https://www.gmail.com/')
        except:
            self.go_to_login_page()
        wait_until_internet_connectivity_is_good()
        if "https://mail.google.com/mail" in self.driver.current_url:
            random_sleep(0.5, 1.5)
            try:
                self.driver.find_element(By.XPATH, '//span[@id="link_enable_notifications_hide"]').click()
            finally:
                return True
        try:
            random_sleep(0.5, 1.5)
            self.driver.find_element(By.XPATH, '//a[contains(@href,"https://accounts.google.com/AccountChooser'
                                               '/signinchooser")]').click()
        except:
            pass

    def do_login(self):
        # try:
        random_sleep(1, 2)
        self.driver.save_screenshot('screen1.png')
        if "https://mail.google.com/mail" in self.driver.current_url:
            return True
        random_sleep(1, 2)
        if "https://accounts.google.com/ServiceLogin/signinchooser" in self.driver.current_url:
            self.driver.find_element(By.XPATH, f'//div[@data-email="{self.email}"]').click()
        else:
            while True:
                try:
                    login_elem = self.driver.find_element(By.XPATH, '//input[@type="email"]')
                    login_elem.clear()
                    login_elem.send_keys(self.email)
                    wait_until_internet_connectivity_is_good()
                    login_elem.send_keys(Keys.ENTER)
                    break
                except TimeoutException as ex:
                    self.driver.refresh()

        WebDriverWait(self.driver, 60).until(
            AnyEc(
                EC.presence_of_element_located((By.XPATH, '//img[@id="captchaimg" and @src]')),
                EC.presence_of_element_located((By.XPATH, '//div[@jsname="B34EJ"]//*[name()="svg"]')),
                EC.url_contains('https://accounts.google.com/signin/v2/deniedsigninrejected'),
                EC.presence_of_element_located((By.NAME, 'password'))
            )
        )

        if len(self.driver.find_elements(By.XPATH, '//div[@jsname="B34EJ"]//*[name()="svg"]')) > 0:
            api.set_status(self.email, api.STATUS_ERROR, "Email not found")
            # self.save_in('email-not-found.txt')
            return False

        if 'https://accounts.google.com/signin/v2/deniedsigninrejected' in self.driver.current_url:
            error_message_elem = self.driver.find_element(By.XPATH, '//h1[@id="headingText"]/span')
            api.set_status(self.email, api.STATUS_ERROR, error_message_elem.text)
            # self.save_in('deactivated.txt')
            return False

        if len(self.driver.find_elements(By.XPATH, '//img[@id="captchaimg" and @src]')) > 0:
            print('Captcha found, retry...')
            return "Captcha"

        while True:
            try:
                random_sleep(2, 4)
                password_elem = self.driver.find_element(By.NAME, 'password')
                password_elem.send_keys(self.password)

                wait_until_internet_connectivity_is_good()
                password_elem.send_keys(Keys.ENTER)
                break
            except TimeoutException as ex:
                self.driver.refresh()

        if not self.wait_login_page_to_load():
            return False

        if len(self.driver.find_elements(By.XPATH, '//img[@id="captchaimg" and @src]')) > 0:
            print('Captcha found, retry...')
            return "Captcha"

        if len(self.driver.find_elements(By.XPATH, '//div[@jsname="h9d3hd"]//*[name()="svg"]')) > 0:
            api.set_status(self.email, api.STATUS_WRONG_PASSWORD, "Wrong password")
            # self.save_in('wrong-password.txt')
            return False

        if 'https://accounts.google.com/signin/v2/deniedsigninrejected' in self.driver.current_url:
            error_message_elem = self.driver.find_element(By.XPATH, '//h1[@id="headingText"]/span')
            print(error_message_elem.text)
            api.set_status(self.email, api.STATUS_ERROR, error_message_elem.text)
            # self.save_in('verify-its-you.txt')
            return False

        if "https://accounts.google.com/signin/v2/challenge/selection" in self.driver.current_url:
            random_sleep(0.5, 1)
            self.driver.find_element(By.XPATH, '//div[@data-challengetype="12"]').click()
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, '//input[@type="email"]'))
            )
            while True:
                try:
                    random_sleep(0.5, 1)
                    recovery_elem = self.driver.find_element(By.XPATH, '//input[@type="email"]')
                    recovery_elem.clear()
                    recovery_elem.send_keys(self.recovery)
                    recovery_elem.send_keys(Keys.ENTER)
                    break
                except TimeoutException as ex:
                    self.driver.refresh()

            if not self.wait_login_page_to_load():
                return False

            if 'https://accounts.google.com/signin/v2/disabled' in self.driver.current_url:
                error_message_elem = self.driver.find_element(By.XPATH, '//h1[@id="headingText"]/span')
                print(error_message_elem.text)
                api.set_status(self.email, api.STATUS_ERROR, "Account Disabled")
                # self.save_in('deactivated.txt')
                return False

            if 'https://gds.google.com/web/chip' in self.driver.current_url:
                self.driver.find_element(By.XPATH, '//span[@class="VfPpkd-vQzf8d "]').click()
                if not self.wait_login_page_to_load():
                    return False

            if len(self.driver.find_elements(By.XPATH, '//div[@jsname="B34EJ"]//*[name()="svg"]')) > 0:
                api.set_status(self.email, api.STATUS_ERROR, "Wrong recovery address")
                # self.save_in('wrong-recovery.txt')
                return False

            if 'https://accounts.google.com/speedbump/idvreenable' in self.driver.current_url:
                api.set_status(self.email, api.STATUS_ERROR, "Need phone validation")
                # self.save_in('phone.txt')
                return False

        if "https://myaccount.google.com/signinoptions/recovery-options-collection" in self.driver.current_url:
            random_sleep(0.5, 1)
            api.set_status(self.email, api.STATUS_ERROR, "Need to add a recovery email")
            # self.save_in('add-recovery.txt')
            self.driver.find_element(By.XPATH, '(//div[@role="button"])[2]').click()
            random_sleep(0.5, 1)

        api.set_status(self.email, api.STATUS_ACTIVE)
        # self.save_in('valid.txt')
        return True
        # self.wait_until_load_new_messages()
        # except:
        #     return False

    def logout(self):
        time.sleep(120)
        wait_until_internet_connectivity_is_good()
        self.driver.find_element(By.XPATH, '//a[contains(@href,"https://accounts.google.com/SignOutOptions")]').click()
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//a[contains(@href,"https://accounts.google.com/Logout")]')))
        time.sleep(0.5)
        self.driver.find_element(By.XPATH, '//a[contains(@href,"https://accounts.google.com/Logout")]').click()

    def save_in(self, verification_file):
        print(f'Saving {self.email} in {verification_file}')
        vf = open(f'errors/{verification_file}', 'a+')
        vf.write(f'{self.email};{self.password};{self.recovery}\n')
        vf.close()

    def click_more(self):
        try:
            self.driver.find_element(By.XPATH, f'//span[@role="button" and not(contains(@class, "air"))]/span['
                                               f'@class="CJ"]').click()
        except:
            pass

    def click_less(self):
        try:
            self.driver.find_element(By.XPATH, f'//span[@role="button" and contains(@class, "air")]/span['
                                               f'@class="CJ"]').click()
        except:
            pass

    def go_to_next_page(self):
        try:
            self.driver.find_element(By.XPATH,
                                     f'//div[contains(@class,"T-I J-J5-Ji amD T-I-awG T-I-ax7 T-I-Js-Gs L3")]').click()
            return True
        except:
            return False

    def go_to_next_message(self):
        try:
            self.driver.find_element(By.XPATH,
                                     f'//div[contains(@class,"T-I J-J5-Ji adg T-I-awG T-I-ax7 T-I-Js-Gs L3")]').click()
            return True
        except:
            return False

    def open_folder(self, folder_name):
        wait_until_internet_connectivity_is_good()
        try:
            self.driver.find_element(By.XPATH, f'//a[contains(@href,"/#{folder_name}")]').click()
        except:
            self.click_more()
            time.sleep(0.5)
            self.driver.find_element(By.XPATH, f'//a[contains(@href,"/#{folder_name}")]').click()

        self.wait_until_load_new_messages()

    def open_inbox_folder(self):
        self.open_folder('inbox')

    def open_spam_folder(self):
        self.open_folder('spam')

    def filter_by_unread(self, folder_name='inbox'):
        wait_until_internet_connectivity_is_good()
        self.driver.get(f'https://mail.google.com/mail/u/0/#search/in%3A{folder_name}+is%3Aunread')

    def filter_by_subject(self, folder_name='inbox', subject=''):
        wait_until_internet_connectivity_is_good()
        self.driver.get(
            f'https://mail.google.com/mail/u/0/#search/in%3A{folder_name}+is%3Aunread+subject%3A{urllib.parse.quote(subject)}')

    def get_total_visible_messages(self):
        try:
            return len(self.driver.find_elements(By.XPATH, f'//tr[@jsaction="Tnvr6c:RNc9jf;PG1zDd:eyrEaf;WGbBt:UL4Ddb'
                                                           f';nVvxM:UL4Ddb;"]'))
        except:
            return 0

    def get_message_number(self, number):
        return self.driver.find_element(
            By.XPATH, f'(//tr[@jsmodel="nXDxbd"])[{number}]')

    def inside_get_subject(self):
        WebDriverWait(self.driver, 8).until(
            EC.presence_of_element_located((By.XPATH, '//h2[@data-thread-perm-id]')))
        return self.driver.find_element(By.XPATH, '//h2[@data-thread-perm-id]').text

    def reply(self, creative):
        self.driver.find_element(By.XPATH, '//div[@class="T-I J-J5-Ji T-I-Js-IF aaq T-I-ax7 L3"]').click()
        WebDriverWait(self.driver, 8).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="ajR"]')))
        time.sleep(0.5)
        text_area = self.driver.find_element(By.XPATH, '//div[@class="Am aO9 Al editable LW-avf tS-tW"]')
        print(text_area.get_attribute('innerHTML'))
        text_area.send_keys(Keys.CONTROL, 'a')
        time.sleep(0.5)
        text_area.send_keys(Keys.BACK_SPACE)
        time.sleep(0.5)
        text_area.send_keys(Keys.BACK_SPACE)
        time.sleep(0.5)
        text_area.send_keys(Keys.BACK_SPACE)
        time.sleep(0.5)

        self.driver.execute_script(f"arguments[0].innerHTML = `{creative}`;", text_area)
        time.sleep(5)
        self.driver.find_element(By.XPATH, '//div[@class="T-I J-J5-Ji aoO v7 T-I-atl L3"]').click()

    def inside_delete_button(self):
        self.driver.find_element(By.XPATH, '//div[@jslog="20283; u014N:cOuCgd,Kr2w4b"]').click()

    def outside_mark_as_read(self):
        pass

    def outside_add_star(self):
        pass

    def outside_mark_as_important(self):
        pass

    def quit(self):
        self.driver.quit()
