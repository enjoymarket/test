import random
from datetime import datetime, timedelta
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
            WebDriverWait(self.driver, 15).until(
                AnyEc(
                    EC.presence_of_element_located((By.XPATH, f'//div[@data-challengetype="12"]')),
                    EC.url_contains('https://mail.google.com/mail/'),
                    EC.url_contains('https://myaccount.google.com/signinoptions/recovery-options-collection'),
                    EC.url_contains('https://accounts.google.com/signin/v2/deniedsigninrejected'),
                    EC.url_contains('https://accounts.google.com/speedbump/idvreenable'),
                    EC.url_contains('https://accounts.google.com/signin/v2/disabled'),
                    EC.url_contains('https://gds.google.com/web/chip'),
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

        while True:
            try:
                WebDriverWait(self.driver, 15).until(
                    AnyEc(
                        EC.presence_of_element_located((By.XPATH, '//img[@id="captchaimg" and @src]')),
                        EC.presence_of_element_located((By.XPATH, '//div[@jsname="B34EJ"]//*[name()="svg"]')),
                        EC.url_contains('https://accounts.google.com/signin/v2/deniedsigninrejected'),
                        EC.url_contains('https://accounts.google.com/ServiceLogin/webreauth'),
                        EC.presence_of_element_located((By.XPATH, '//input[@type="password"]'))
                    )
                )
                break
            except:
                self.driver.refresh()

        if len(self.driver.find_elements(By.XPATH, '//div[@jsname="B34EJ"]//*[name()="svg"]')) > 0:
            api.set_status(self.email, api.STATUS_ERROR, "Email not found")
            # self.save_in('email-not-found.txt')
            return False

        if 'https://accounts.google.com/signin/v2/deniedsigninrejected' in self.driver.current_url:
            try:
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ENTER)
                WebDriverWait(self.driver, 8).until(
                    AnyEc(
                        EC.presence_of_element_located((By.NAME, 'password'))
                    )
                )
            except:
                error_message_elem = self.driver.find_element(By.XPATH, '//h1[@id="headingText"]/span')
                api.set_status(self.email, api.STATUS_ERROR, error_message_elem.text)
                return False

        if len(self.driver.find_elements(By.XPATH, '//img[@id="captchaimg" and @src]')) > 0:
            print('Captcha found, retry...')
            return "Captcha"

        if 'https://accounts.google.com/ServiceLogin/webreauth' in self.driver.current_url:
            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ENTER)
            WebDriverWait(self.driver, 8).until(
                AnyEc(
                    EC.presence_of_element_located((By.XPATH, '//input[@type="password"]'))
                )
            )

        while True:
            try:
                random_sleep(2, 4)
                password_elem = self.driver.find_element(By.XPATH, '//input[@type="password"]')
                password_elem.send_keys(self.password)

                wait_until_internet_connectivity_is_good()
                password_elem.send_keys(Keys.ENTER)
                break
            except TimeoutException as ex:
                self.driver.refresh()

        if not self.wait_login_page_to_load():
            return False

        if len(self.driver.find_elements(By.XPATH, '//img[@id="captchaimg" and @src]')) > 0:
            return "Captcha"

        if len(self.driver.find_elements(By.XPATH, '//div[@jsname="h9d3hd"]//*[name()="svg"]')) > 0:
            api.set_status(self.email, api.STATUS_WRONG_PASSWORD, "Wrong password")
            # self.save_in('wrong-password.txt')
            return False

        if 'https://accounts.google.com/signin/v2/deniedsigninrejected' in self.driver.current_url:
            error_message_elem = self.driver.find_element(By.XPATH, '//h1[@id="headingText"]/span')
            api.set_status(self.email, api.STATUS_ERROR, error_message_elem.text)
            # self.save_in('verify-its-you.txt')
            return False

        if 'https://gds.google.com/web/chip' in self.driver.current_url:
            random_sleep(1, 2)
            try:
                self.driver.find_element(By.XPATH, '//span[@class="VfPpkd-vQzf8d"]').click()
            except:
                self.driver.find_element(By.XPATH, '//span[@class="VfPpkd-vQzf8d "]').click()
            if not self.wait_login_page_to_load():
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
                api.set_status(self.email, api.STATUS_ERROR, "Account Disabled")
                # self.save_in('deactivated.txt')
                return False

            if 'https://gds.google.com/web/chip' in self.driver.current_url:
                random_sleep(1, 2)
                try:
                    self.driver.find_element(By.XPATH, '//span[@class="VfPpkd-vQzf8d"]').click()
                except:
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

    def add_contacts(self, file):
        wait_until_internet_connectivity_is_good()
        # self.driver.execute_script("window.open('');")
        # self.driver.switch_to.window(self.driver.window_handles[1])
        random_sleep(0.2, 0.9)
        self.driver.get('https://contacts.google.com')
        actions = ActionChains(self.driver)
        WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located((By.XPATH, '//a[@jsaction="BlwSWe"]'))
        )
        import_elem = self.driver.find_element(By.XPATH, '//a[@jsaction="BlwSWe"]')
        actions.move_to_element(import_elem).perform()
        time.sleep(0.5)
        import_elem.click()
        WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located((By.XPATH, '//input[@type="file"]'))
        )
        random_sleep(2, 3)
        self.driver.find_element(By.XPATH, '//input[@type="file"]').send_keys(rf'{file}')
        WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located((By.XPATH, '//span[contains(text(),".csv")]'))
        )
        random_sleep(0.5, 1)
        self.driver.find_element(By.CSS_SELECTOR, 'div[jsaction*="JIbuQc:DJ6zke;"] button:nth-child(2)').click()
        WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located((By.XPATH, '//div[@jsaction="JIbuQc:.CLIENT"]//div[@role="button"]'))
        )
        # self.driver.close()
        # self.driver.switch_to.window(self.driver.window_handles[0])

    def delete_all(self):
        # Clear Inbox
        if "https://mail.google.com/mail/u/0/#inbox" != self.driver.current_url:
            self.driver.get('https://mail.google.com/mail/u/0/#inbox')
        for i in range(1, 4):
            if i > 1:
                self.driver.find_element(By.XPATH, f'(//td[@class="aRz J-KU"])[{i}]').click()
                time.sleep(3)
            while len(self.driver.find_elements(By.XPATH, '//table[@class="F cf zt"]//tbody/tr')) > 5:
                try:
                    self.driver.find_element(By.XPATH, '//div[@class="bBe"]').click()
                except:
                    pass
                self.driver.find_element(By.XPATH, '//span[contains(@class,"T-Jo J-J5-Ji")]').click()
                time.sleep(0.5)
                try:
                    self.driver.find_element(By.XPATH, '(//div[@class="ya yb"]//span)[2]').click()
                    time.sleep(0.5)
                except:
                    pass
                self.driver.find_element(By.XPATH, '//div[@class="ar9 T-I-J3 J-J5-Ji"]/parent::div/parent::div').click()
                time.sleep(0.5)
                try:
                    self.driver.find_element(By.XPATH, '//button[contains(@class,"J-at1-auR")]').click()
                    time.sleep(0.5)
                except:
                    pass
                while len(self.driver.find_elements(By.XPATH, '//div[@class="bBe"]')) == 0:
                    print("sleep 3 sec")
                    time.sleep(3)
        # clear trash
        # print('Go to trash and clear it')
        # wait_until_internet_connectivity_is_good()
        # self.driver.get('https://mail.google.com/mail/u/0/#trash')
        # try:
        #     WebDriverWait(self.driver, 60).until(
        #         EC.presence_of_element_located((By.XPATH, '//div[@class="ya"]//span')))
        #     self.driver.find_element(By.XPATH, '//div[@class="ya"]//span').click()
        #     time.sleep(0.5)
        #     self.driver.find_element(By.XPATH, '(//button[contains(@class,"J-at1-auR")])[2]').click()
        #     while len(self.driver.find_elements(By.XPATH, '//div[@class="bBe"]')) == 0:
        #         print("sleep 3 sec")
        #         time.sleep(3)
        # except:
        #     pass

    def add_to_postmaster(self, domain):
        self.driver.get('https://postmaster.google.com/u/1/managedomains?pli=1')
        self.driver.find_element(By.XPATH, '//div[@id="l-joyFDb-ah"]').click()
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//input[@type="text"]'))
        )
        time.sleep(0.5)
        domain_elem = self.driver.find_element(By.XPATH, '//input[@type="text"]')
        domain_elem.send_keys(domain)
        domain_elem.send_keys(Keys.ENTER)
        WebDriverWait(self.driver, 30).until(
            AnyEc(
                EC.element_to_be_clickable((By.XPATH, '//div[@class="J-p"]')),
                EC.element_to_be_clickable((By.XPATH, '//button[@name="done"]'))
            )
        )
        if len(self.driver.find_elements(By.XPATH, '//button[@name="done"]')) > 0:
            self.driver.find_element(By.XPATH, '//button[@name="done"]').click()
            return True
        txt_record = self.driver.find_element(By.XPATH, '//div[@class="J-p"]').text

        record = {
            'Name': '@',
            'Type': 'TXT',
            "Address": txt_record,
            "TTL": "60"
        }
        recovered_record = {}
        try:
            username = "enjoymarket"
            wl_ip = "84.17.42.46"
            api_key = "55df0746701f4254a31728cdec699c87"
            api = Api(username, api_key, username, wl_ip, sandbox=False, attempts_count=3, attempts_delay=0.1)

            api.domains_dns_addHost(domain, record)
        except:
            try:
                hosts = api.domains_dns_getHosts(domain)
                last_record = hosts[-1]
                recovered_record = {
                    'Name': last_record['Name'],
                    'Type': last_record['Type'],
                    "Address": last_record['Address'],
                    "TTL": "60"
                }
                api.domains_dns_delHost(domain, recovered_record)
                api.domains_dns_addHost(domain, record)
            except:
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                return False

        time.sleep(3)
        attemps = 1
        while attemps < 7:
            self.driver.find_element(By.XPATH, '//button[@name="verify"]').click()
            WebDriverWait(self.driver, 30).until(
                AnyEc(
                    EC.presence_of_element_located((By.XPATH, '//div[@class="b-c-a3-Z" and text()!=""]')),
                    EC.presence_of_element_located((By.XPATH, '//button[@name="done"]'))
                )
            )
            if len(self.driver.find_elements(By.XPATH, '//div[@class="b-c-a3-Z" and text()!=""]')) > 0:
                print(f'Retry after 10 sec : {attemps}/6')
                attemps = attemps + 1
                time.sleep(10)
            if len(self.driver.find_elements(By.XPATH, '//button[@name="done"]')) > 0:
                self.driver.find_element(By.XPATH, '//button[@name="done"]').click()
                if len(recovered_record) > 0:
                    print('Recover DNS')
                    record = {
                        'Name': record['HostName'],
                        'Type': record['RecordType'],
                        "Address": record['Address'],
                        "TTL": "60"
                    }
                    print(record)
                    print(recovered_record)
                    try:
                        api.domains_dns_delHost(domain, record)
                        api.domains_dns_addHost(domain, recovered_record)
                    except Exception as ex:
                        print(ex)
                return True

        if len(recovered_record) > 0:
            print('Recover DNS-')
            record = {
                'Name': record['HostName'],
                'Type': record['RecordType'],
                "Address": record['Address'],
                "TTL": "60"
            }
            api.domains_dns_delHost(domain, record)
            api.domains_dns_addHost(domain, recovered_record)
        return False

    def change_password(self, new_password):
        # time.sleep(300)
        try:
            self.driver.get('https://myaccount.google.com/security')
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located(
                        (By.XPATH,
                         '(//a[contains(@href,"https://accounts.google.com/ServiceLogin?service=accountsettings")])[1]')))
                self.driver.find_element(
                    By.XPATH,
                    '(//a[contains(@href,"https://accounts.google.com/ServiceLogin?service=accountsettings")])[1]').click()
            except:
                pass
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, '//a[contains(@href,"signinoptions/rescuephone?")]')))

            time.sleep(2)
            self.driver.find_element(By.XPATH, '//a[contains(@href,"signinoptions/rescuephone?")]').click()
        except TimeoutException as ex:
            self.change_password(new_password)

        while True:
            try:
                # Old Password
                WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.NAME, 'password')))

                random_sleep(2, 4)
                password_elem = self.driver.find_element(By.NAME, 'password')
                password_elem.send_keys(self.password)

                wait_until_internet_connectivity_is_good()
                password_elem.send_keys(Keys.ENTER)

                try:
                    WebDriverWait(self.driver, 8).until(
                        AnyEc(
                            EC.presence_of_element_located((By.XPATH, '//input[@name="password" and @aria-invalid="true"]')),
                            EC.url_contains('https://accounts.google.com/signin/v2/challenge/selection')
                        )
                    )
                    if len(self.driver.find_element(By.XPATH, '//input[@name="password" and @aria-invalid="true"]')) > 0:
                        return False

                    if "https://accounts.google.com/signin/v2/challenge/selection" in self.driver.current_url:
                        random_sleep(0.5, 1)
                        self.driver.find_element(By.XPATH, '//div[@data-challengetype="12"]').click()
                        random_sleep(0.5, 1)
                        recovery_elem = self.driver.find_element(By.XPATH, '//input[@type="email"]')
                        recovery_elem.clear()
                        recovery_elem.send_keys(self.recovery)
                        recovery_elem.send_keys(Keys.ENTER)
                        break
                except:
                    break
            except TimeoutException as ex:
                self.driver.refresh()

        while True:
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.url_contains('https://myaccount.google.com/signinoptions/rescuephone'))

                current_url = self.driver.current_url
                new_url = current_url.replace('rescuephone', 'password')
                break
            except TimeoutException as ex:
                self.driver.refresh()

        while True:
            try:
                # New Password
                self.driver.get(new_url)

                WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.NAME, 'confirmation_password')))

                random_sleep(2, 4)
                new_password_elem = self.driver.find_element(By.NAME, 'password')
                time.sleep(0.2)
                new_password_elem.send_keys(new_password)
                random_sleep(2, 4)
                confirmation_password_elem = self.driver.find_element(By.NAME, 'confirmation_password')
                time.sleep(0.2)
                confirmation_password_elem.send_keys(new_password)
                time.sleep(0.1)
                confirmation_password_elem.send_keys(Keys.ENTER)
                break
            except TimeoutException as ex:
                if "https://myaccount.google.com/security" in self.driver.current_url:
                    return True
                self.driver.refresh()
            # except Exception as e:
            #     print(e)

        WebDriverWait(self.driver, 15).until(
            AnyEc(
                EC.presence_of_element_located((By.XPATH, '//p[@role="alert"]')),
                EC.url_contains('https://myaccount.google.com/security')
            )
        )

        if len(self.driver.find_elements(By.XPATH, '//p[@role="alert"]')) > 0:
            return False

        time.sleep(2)
        return True

    def change_language(self, language, country):
        try:
            self.driver.get('https://myaccount.google.com/language')
        except:
            self.change_language(language, country)
        WebDriverWait(self.driver, 8).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@class="VfPpkd-Bz112c-LgbsSe yHy1rc eT1oJ mN1ivc"]'))
        )
        self.driver.find_element(By.XPATH, '//button[@class="VfPpkd-Bz112c-LgbsSe yHy1rc eT1oJ mN1ivc"]').click()
        WebDriverWait(self.driver, 8).until(
            EC.presence_of_element_located((By.XPATH, '//input[@class="VfPpkd-fmcmS-wGMbrd WRh7Kd"]'))
        )
        random_sleep(1, 2)
        self.driver.find_element(By.XPATH, '//input[@class="VfPpkd-fmcmS-wGMbrd WRh7Kd"]').send_keys(language)
        random_sleep(0.5, 1)
        self.driver.find_element(By.XPATH, '//li[contains(@class,"MCs1Pd HiC7Nc OXawpe") and @aria-disabled="false"]').click()
        random_sleep(0.3, 0.8)
        print(f'//li[contains(@class,"MCs1Pd HiC7Nc OXawpe")]//span[text()="{country}"]//ancestor::li')
        country_elem = self.driver.find_element(By.XPATH, f'//li[contains(@class,"MCs1Pd HiC7Nc OXawpe")]//span[text()="{country}"]//ancestor::li')
        actions = ActionChains(self.driver)
        actions.move_to_element(country_elem).perform()
        random_sleep(0.5, 0.8)
        country_elem.click()
        time.sleep(0.3)
        actions.send_keys(Keys.TAB * 2)
        actions.perform()
        actions.send_keys(Keys.ENTER)
        actions.perform()
        time.sleep(5)


    def click_more(self):
        try:
            self.driver.find_element(By.XPATH, f'//span[@role="button" and not(contains(@class, "air"))]/span[@class="CJ"]').click()
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
        # print(f'https://mail.google.com/mail/u/0/#search/in%3A{folder_name}+subject%3A{urllib.parse.quote(subject)}')
        try:
            self.driver.get(
                f'https://mail.google.com/mail/u/0/#search/in%3A{folder_name}+subject%3A{urllib.parse.quote(subject)}')
        except TimeoutException as ex:
            self.filter_by_subject(folder_name, subject)

    def create_filter_for_reply(self):
        self.driver.find_element(By.XPATH, '//button[@gh="sda"]').click()
        random_sleep(1, 3)
        self.driver.find_element(By.XPATH, '//div[@class="aQh"]/input').send_keys('1')
        random_sleep(1, 3)
        self.driver.find_element(By.XPATH, '(//div[@class="aQj"]/div)[1]').click()
        random_sleep(0.3, 0.8)
        self.driver.find_element(By.XPATH, '((//div[@class="aQj"]/div)[2]/div)[3]').click()
        random_sleep(1, 2)
        self.driver.find_element(By.XPATH, '//div[@class="acM"]').click()

        WebDriverWait(self.driver, 8).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="nH lZ"]/label')))

        random_sleep(1, 1.5)
        self.driver.find_element(By.XPATH, '(//div[@class="nH lZ"]/label)[6]').click()

        random_sleep(1, 3)
        self.driver.find_element(By.XPATH, '//div[@class="btl bti"]/div[@role="button"]').click()
        random_sleep(3, 5)
        return True

    def delete_other_froms(self):
        try:
            WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//td[@class="rc CY"]/span')))
            try:
                self.driver.find_element(
                    By.XPATH,
                    f'(//table[@class="cf qv aYf"]//div[@class="rc" and contains(text(),"<{self.email}>")]/parent::td/following-sibling::td[@class="qy CY"])[1]/span[@role="link"]').click()
            except:
                pass

            # (//table[@class="cf qv aYf"]//tr/td[@class="qw CY"])/span[@role="link"] # select all other senders
            delete_elems = self.driver.find_elements(By.XPATH, '(//table[@class="cf qv aYf"]//tr/td['
                                                               '@class="CY"])/div[@class="rc" and contains(text(), '
                                                               '"gmail.com")]//parent::td/following-sibling::td['
                                                               '@class="qw CY"]/span[@role="link"]')
            for delete_elem in delete_elems:
                delete_elem.click()
                WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, '(//div[@role="alertdialog"]//button)[1]')))
                random_sleep(0.3, 0.5)
                self.driver.find_element(By.XPATH, '(//div[@role="alertdialog"]//button)[1]').click()
                random_sleep(0.5, 1)
        except:
            self.delete_other_froms()

    def set_new_from(self, from_name, from_email=None):
        try:
            self.driver.get('https://mail.google.com/mail/u/0/#settings/accounts')
            WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.XPATH, '//td[@class="rc CY"]/span')))
        except:
            self.set_new_from_name(from_name)
        random_sleep(2, 4)
        self.delete_other_froms()
        try:
            self.driver.find_element(
                By.XPATH,
                f'(//table[@class="cf qv aYf"]//div[@class="rc" and contains(text(),"{from_name} <{from_email}>")]/parent::td/following-sibling::td[@class="qy CY"])[1]/span[@role="link"]').click()
            random_sleep(2, 3)
        except:
            self.driver.find_element(By.XPATH, '//td[@class="rc CY"]/span').click()

            self.driver.switch_to.window(self.driver.window_handles[1])

            random_sleep(2, 4)
            from_name_elem = self.driver.find_element(By.XPATH, '//input[@name="cfn"]')
            from_name_elem.clear()
            from_name_elem.send_keys(from_name)

            random_sleep(2, 4)
            email = from_email if from_name is not None else self.email
            from_email_elem = self.driver.find_element(By.XPATH, '//input[@name="cfa"]')
            from_email_elem.send_keys(email)
            from_email_elem.send_keys(Keys.ENTER)

            random_sleep(2, 3)

            self.driver.switch_to.window(self.driver.window_handles[0])

            try:
                self.driver.find_element(
                    By.XPATH,
                    f'(//table[@class="cf qv aYf"]//div[@class="rc" and contains(text(),"{from_name} <{from_email}>")]/parent::td/following-sibling::td[@class="qy CY"])[1]/span[@role="link"]').click()
                random_sleep(2, 3)
            except:
                pass

    def get_total_visible_messages(self):
        try:
            return len(self.driver.find_elements(By.XPATH, f'//tr[@jsaction="Tnvr6c:RNc9jf;PG1zDd:eyrEaf;WGbBt:UL4Ddb'
                                                           f';nVvxM:UL4Ddb;"]'))
        except:
            return 0

    def get_message_number(self, number):
        try:
            WebDriverWait(self.driver, 8).until(
                EC.element_to_be_clickable((By.XPATH, f'(//tr[@jsmodel="nXDxbd"])[{number}]')))
            return self.driver.find_element(
                By.XPATH, f'(//tr[@jsmodel="nXDxbd"])[{number}]')
        except TimeoutException as ex:
            return False

    def inside_get_subject(self):
        WebDriverWait(self.driver, 8).until(
            EC.presence_of_element_located((By.XPATH, '//h2[@data-thread-perm-id]')))
        return self.driver.find_element(By.XPATH, '//h2[@data-thread-perm-id]').text

    def reply(self, creative, with_attachment):
        WebDriverWait(self.driver, 8).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@class="T-I J-J5-Ji T-I-Js-IF aaq T-I-ax7 L3"]')))
        random_sleep(1, 3)
        self.driver.find_element(By.XPATH, '//div[@class="T-I J-J5-Ji T-I-Js-IF aaq T-I-ax7 L3"]').click()
        WebDriverWait(self.driver, 8).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="ajR"]')))
        random_sleep(0.8, 1.5)
        text_area = self.driver.find_element(By.XPATH, '//div[@class="Am aO9 Al editable LW-avf tS-tW"]')
        if not with_attachment:
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

    def detect_bounce(self):
        try:
            self.driver.get('https://mail.google.com/mail/u/0/#advanced-search/from=mailer-daemon@googlemail.com&has=550+5.1.1')
            self.driver.refresh()
        except:
            self.detect_bounce()

        WebDriverWait(self.driver, 8).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@class="T-I J-J5-Ji nf T-I-ax7 L3"]')))
        random_sleep(1, 3)
        more_elem = self.driver.find_element(By.XPATH, '//div[@class="T-I J-J5-Ji nf T-I-ax7 L3"]')
        more_elem.click()
        random_sleep(0.5, 1.5)
        more_elem.click()
        random_sleep(0.5, 1.5)

        bounces = []
        first_message = self.get_message_number(1)
        if first_message is not False:
            first_message.click()
            while True:
                try:
                    WebDriverWait(self.driver, 8).until(
                        EC.element_to_be_clickable((By.XPATH, '//a[@style="color:#212121;text-decoration:none"]/b')))
                    bounce_elem = self.driver.find_element(By.XPATH, '//a[@style="color:#212121;text-decoration:none"]/b')
                    bounces.append(bounce_elem.text)
                    print(bounces)
                    random_sleep(0.5, 1)
                    if not self.go_to_next_message():
                        break
                except:
                    break
        return bounces

    def detect_sender_blocked(self):
        try:
            self.driver.get(
                'https://mail.google.com/mail/u/0/#advanced-search/from=mailer-daemon@googlemail.com&has=550+5.1.0')
            self.driver.refresh()
        except:
            self.detect_bounce()

        WebDriverWait(self.driver, 8).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@class="T-I J-J5-Ji nf T-I-ax7 L3"]')))
        random_sleep(1, 3)
        actions = ActionChains(self.driver)
        actions.send_keys(Keys.ESCAPE)
        actions.perform()
        random_sleep(1, 1.5)
        actions.send_keys(Keys.ESCAPE)
        actions.perform()
        random_sleep(1, 1.5)

        blocked = []
        first_message = self.get_message_number(1)
        if first_message is not False:
            first_message.click()
            while True:
                try:
                    WebDriverWait(self.driver, 8).until(
                        EC.element_to_be_clickable((By.XPATH, '//a[@style="color:#212121;text-decoration:none"]/b')))
                    bounce_elem = self.driver.find_element(By.XPATH,
                                                           '//a[@style="color:#212121;text-decoration:none"]/b')
                    block = '.'.join(bounce_elem.text.split('@')[1].split('.')[-2:])
                    email_elem = self.driver.find_element(By.XPATH, '//p[@style="font-family:monospace"]//a[contains('
                                                                    '@href, "mailto")]')
                    email = email_elem.text
                    e = {
                        'email': email,
                        'sender': block
                    }
                    if e not in blocked:
                        blocked.append(e)
                        print(blocked)
                    random_sleep(0.5, 1)
                    if not self.go_to_next_message():
                        break
                except:
                    break
        for block in blocked:
            api.add_blocked_sender(block.get('email'), block.get('sender'))
        return blocked

    def detect_limit(self):
        try:
            self.driver.get(
                f'https://mail.google.com/mail/u/0/#advanced-search/query=from%3A('
                f'mailer-daemon%40googlemail.com)+limit&isrefinement=true&datestart='
                f'{datetime.strftime(datetime.now() - timedelta(1), "%Y-%m-%d")}&dateend='
                f'{datetime.strftime(datetime.now(), "%Y-%m-%d")}&daterangetype=custom_range')
            self.driver.refresh()
        except:
            self.detect_bounce()

        WebDriverWait(self.driver, 8).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@class="T-I J-J5-Ji nf T-I-ax7 L3"]')))

        first_message = self.get_message_number(1)
        if first_message is not False:
            return True
        return False

    def inside_delete_button(self):
        self.driver.find_element(By.XPATH, '//div[@jslog="20283; u014N:cOuCgd,Kr2w4b"]').click()

    def quit(self):
        self.driver.quit()

    ####################################################################################################################
    def select_first_message(self, selector):
        list = {
            "all": "",
            "readed": "zA yO",
            "unreaded": "zA zE",
        }
        try:
            WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH,
                                                                             '//div[contains(@class,"BltHke nH oy8Mbf") and not(contains(@style,"display: none;"))]//tr[contains(@class,"{list[selector]}")][1]/td[contains(@class,"oZ-x3 xY")]')))
            self.driver.find_element(By.XPATH,
                                     '//div[contains(@class,"BltHke nH oy8Mbf") and not(contains(@style,"display: none;"))]//tr[contains(@class,"{list[selector]}")][1]/td[contains(@class,"oZ-x3 xY")]').click()
            return True
        except:
            return False

    def open_first_message(self, selector):
        list = {
            "all": "",
            "readed": "zA yO",
            "unreaded": "zA zE",
        }
        try:
            WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH,
                                                                             '//div[contains(@class,"BltHke nH oy8Mbf") and not(contains(@style,"display: none;"))]//tr[contains(@class,"{list[selector]}")][1]/td[contains(@class,"yX xY ")]')))
            self.driver.find_element(By.XPATH,
                                     '//div[contains(@class,"BltHke nH oy8Mbf") and not(contains(@style,"display: none;"))]//tr[contains(@class,"{list[selector]}")][1]/td[contains(@class,"yX xY ")]').click()
            return True
        except:
            return False

    # selector ("all","none","reda","unread","starred","unstarred")
    def select(self, selector):
        try:
            WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH,
                                                                             '//div[(contains(@class,"D E G-atb") or contains(@class,"G-atb D E")) and not(contains(@style,"display: none;"))]//div[contains(@class,"J-J5-Ji J-JN-M-I-Jm")]/div[contains(@class,"G-asx T-I-J3 J-J5-Ji")]')))
            self.driver.find_element(By.XPATH,
                                     '//div[(contains(@class,"D E G-atb") or contains(@class,"G-atb D E")) and not(contains(@style,"display: none;"))]//div[contains(@class,"J-J5-Ji J-JN-M-I-Jm")]/div[contains(@class,"G-asx T-I-J3 J-J5-Ji")]').click()
            self.driver.find_element(By.XPATH,
                                     f'//div[(contains(@class,"D E G-atb") or contains(@class,"G-atb D E")) and not(contains(@style,"display: none;"))]//div[contains(@class,"J-M jQjAxd")]//div[contains(@class,"J-N") and (@selector="{selector}")]').click()
            return True
        except:
            if selector == "all":
                self.driver.find_element(By.XPATH,
                                         '//div[(contains(@class,"D E G-atb") or contains(@class,"G-atb D E")) and not(contains(@style,"display: none;"))]//div[contains(@class,"J-J5-Ji J-JN-M-I-Jm")]/span[contains(@class,"T-Jo J-J5-Ji")]').click()
                return True
            else:
                return False

    def archive(self):
        try:
            WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH,
                                                                             '//div[(contains(@class,"D E G-atb") or contains(@class,"G-atb D E")) and not(contains(@style,"display: none;"))]//div[contains(@class,"T-I J-J5-Ji lR T-I-ax7")]/div[(@class="asa")]')))
            self.driver.find_element(By.XPATH,
                                     '//div[(contains(@class,"D E G-atb") or contains(@class,"G-atb D E")) and not(contains(@style,"display: none;"))]//div[contains(@class,"T-I J-J5-Ji lR T-I-ax7")]/div[(@class="asa")]').click()
            return True
        except:
            return False

    def report_spam(self):
        try:
            WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH,
                                                                             '//div[(contains(@class,"D E G-atb") or contains(@class,"G-atb D E")) and not(contains(@style,"display: none;"))]//div[contains(@class,"T-I J-J5-Ji nN T-I-ax7 T-I-Js-Gs T-I-Js-IF")]/div[(@class="asa")]')))
            self.driver.find_element(By.XPATH,
                                     '//div[(contains(@class,"D E G-atb") or contains(@class,"G-atb D E")) and not(contains(@style,"display: none;"))]//div[contains(@class,"T-I J-J5-Ji nN T-I-ax7 T-I-Js-Gs T-I-Js-IF")]/div[(@class="asa")]').click()
            return True
        except:
            return False

    def not_spam(self):
        try:
            WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH,
                                                                             '//div[(contains(@class,"D E G-atb") or contains(@class,"G-atb D E")) and not(contains(@style,"display: none;"))]//div[contains(@class, "T-I J-J5-Ji aFk T-I-ax7")]/div[(@class="Bn")]')))
            self.driver.find_element(By.XPATH,
                                     '//div[(contains(@class,"D E G-atb") or contains(@class,"G-atb D E")) and not(contains(@style,"display: none;"))]//div[contains(@class, "T-I J-J5-Ji aFk T-I-ax7")]/div[(@class="Bn")]').click()
            return True
        except:
            return False

    def delete(self):
        try:
            WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH,
                                                                             '//div[(contains(@class,"D E G-atb") or contains(@class,"G-atb D E")) and not(contains(@style,"display: none;"))]//div[contains(@class,"T-I J-J5-Ji aFi T-I-ax7") or contains(@class,"T-I J-J5-Ji nX T-I-ax7 T-I-Js-Gs")]')))
            self.driver.find_element(By.XPATH,
                                     '//div[(contains(@class,"D E G-atb") or contains(@class,"G-atb D E")) and not(contains(@style,"display: none;"))]//div[contains(@class,"T-I J-J5-Ji aFi T-I-ax7") or contains(@class,"T-I J-J5-Ji nX T-I-ax7 T-I-Js-Gs")]').click()
            return True
        except:
            return False

    def header_more(self, action):
        list = {
            "mark_all_as_read": 1,
            "mark_as_read": 2,
            "mark_as_unread": 3,
            "mark_as_important": 4,
            "mark_as_not_important": 5,
            "add_to_tasks": 6,
            "add_star": 7,
            "remove_star": 8,
            "archive": 9,
            "mark_as_not_spam": 10,
            "delete_forever": 11,
            "forward_as_attachment": 18,
        }
        try:
            WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH,
                                                                             '//div[(contains(@class,"D E G-atb") or contains(@class,"G-atb D E")) and not(contains(@style,"display: none;"))]//div[contains(@class,"T-I J-J5-Ji mA nf T-I-ax7 L3")]/span[contains(@class,"asa")]')))
            self.driver.find_element(By.XPATH,
                                     '//div[(contains(@class,"D E G-atb") or contains(@class,"G-atb D E")) and not(contains(@style,"display: none;"))]//div[contains(@class,"T-I J-J5-Ji mA nf T-I-ax7 L3")]/span[contains(@class,"asa")]').click()
            element = self.driver.find_element(By.XPATH,
                                               f'//div[contains(@class,"J-M aX0 aYO jQjAxd")]/div/div[contains(@class,"J-N")][{list[action]}]')
            aria_hidden = element.get_attribute("aria-hidden")
            aria_disabled = element.get_attribute("aria-disabled")
            if aria_hidden == "false" and aria_disabled == "false":
                print(action.replace("_", " "))
                element.click()
                return True
            else:
                print(f'already {action.replace("_", " ")}')
                self.driver.find_element(By.XPATH,
                                         '//div[(contains(@class,"D E G-atb") or contains(@class,"G-atb D E")) and not(contains(@style,"display: none;"))]//div[contains(@class,"T-I J-J5-Ji mA nf T-I-ax7 L3")]/span[contains(@class,"asa")]').click()
                return False
        except:
            return False

    def older(self):
        try:
            WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH,
                                                                             '//div[(contains(@class,"D E G-atb") or contains(@class,"G-atb D E")) and not(contains(@style,"display: none;"))]//div[contains(@class,"T-I J-J5-Ji") and contains(@class,"T-I-awG") and contains(@class,"T-I-ax7 T-I-Js-Gs")]')))
            self.driver.find_element(By.XPATH,
                                     '//div[(contains(@class,"D E G-atb") or contains(@class,"G-atb D E")) and not(contains(@style,"display: none;"))]//div[contains(@class,"T-I J-J5-Ji") and contains(@class,"T-I-awG") and contains(@class,"T-I-ax7 T-I-Js-Gs")]').click()
            return True
        except:
            return False

    def newer(self):
        try:
            WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH,
                                                                             '//div[(contains(@class,"D E G-atb") or contains(@class,"G-atb D E")) and not(contains(@style,"display: none;"))]//div[contains(@class,"T-I J-J5-Ji") and contains(@class,"T-I-awG") and contains(@class,"T-I-ax7 T-I-Js-IF")]')))
            self.driver.find_element(By.XPATH,
                                     '//div[(contains(@class,"D E G-atb") or contains(@class,"G-atb D E")) and not(contains(@style,"display: none;"))]//div[contains(@class,"T-I J-J5-Ji") and contains(@class,"T-I-awG") and contains(@class,"T-I-ax7 T-I-Js-IF")]').click()
            return True
        except:
            return False

    def body_more(self, action):
        list = {
            "reply": "r",
            "reply_to_all": "r2",
            "forward": "r3",
            "filter_message_like_this": "cf",
            "delete_this_message": "tm",
            "block_sender": "bs",
            "unblock_sender": "ubs",
            "report_spam": "rs",
            "report_phishing": "rp",
            "report_not_phishing": "rn",
            "show_original": "so",
            "download_message": "dm",
            "show_html_message": "shm",
            "mark_as_unread": "mu",
        }
        try:
            WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable(
                (By.XPATH, '//div[contains(@class,"T-I J-J5-Ji T-I-Js-Gs aap T-I-awG T-I-ax7 L3")]')))
            self.driver.find_element(By.XPATH,
                                     '//div[contains(@class,"T-I J-J5-Ji T-I-Js-Gs aap T-I-awG T-I-ax7 L3")]').click()
            element = self.driver.find_element(By.XPATH,
                                               f'//div[contains(@class,"b7 J-M")]/div[contains(@class,"J-N") and (@id="{list[action]}")]')
            aria_hidden = element.get_attribute("aria-hidden")
            style = element.get_attribute("style")
            if "display: none;" not in style:
                print(action.replace("_", " "))
                element.click()
                return True
            else:
                print(f'already {action.replace("_", " ")}')
                self.driver.find_element(By.XPATH,
                                         '//div[contains(@class,"T-I J-J5-Ji T-I-Js-Gs aap T-I-awG T-I-ax7 L3")]').click()
                return False
        except:
            return False

    def link_sender(self, sender_email, sender_password, sender_recovery):
        try:
            self.driver.get("https://mail.google.com/mail/u/0/#settings/accounts")
            main_window = self.driver.current_window_handle
            WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//span[@class="sA rc"]')))
            self.driver.find_element(By.XPATH, '//span[@class="sA rc"]').click()
            for handle in self.driver.window_handles:
                if handle != main_window:
                    popup = handle
                    self.driver.switch_to.window(popup)
            try:
                self.driver.find_element(By.NAME, 'ma_email').send_keys(sender_email)
                self.driver.find_element(By.XPATH, '//input[@type="submit"]').click()

                WebDriverWait(self.driver, 15).until(
                    AnyEc(
                        EC.presence_of_element_located((By.XPATH, '//td[@class="rb sf"]')),
                        EC.presence_of_element_located((By.XPATH, '//input[@type="radio"]'))
                    )
                )

                if len(self.driver.find_elements(By.XPATH, '//td[@class="rb sf"]')) > 0:
                    self.driver.close()
                    self.driver.switch_to.window(main_window)
                    print(f'{sender_email} already linked with another account.')
                    return False
                self.driver.find_element(By.XPATH, '//input[@type="submit"]').click()
            except:
                pass

            try:
                time.sleep(1)
                WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.ID, 'i0118')))
                self.driver.find_element(By.ID, 'i0118').send_keys(sender_password, Keys.ENTER)
            except:
                pass

            try:
                self.driver.find_element(By.ID, 'EmailAddress').send_keys(sender_recovery, Keys.ENTER)
            except:
                pass

            try:
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'idBtn_Back')))
                self.driver.find_element(By.ID, 'idBtn_Back').click()
            except:
                pass

            try:
                self.driver.find_element(By.ID, 'idSIButton9').send_keys(Keys.ENTER)
            except:
                pass

            try:
                self.driver.find_element(By.NAME, 'ucaccept').click()
            except:
                pass

            try:
                WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.ID, 'bttn_close')))
                time.sleep(1)
                self.driver.find_element(By.ID, 'bttn_close').click()
            except:
                pass

            self.driver.switch_to.window(main_window)
            time.sleep(1)
            self.driver.find_element(
                By.XPATH,
                f'(//div[text()[contains(.,"{sender_email}")]]/parent::td/following-sibling::td)[1]/span').click()
            time.sleep(3)
            return True
        except:
            return False

    def vacation_responder(self, creative):
        try:
            self.driver.get("https://mail.google.com/mail/u/0/#settings/general")
            WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable(
                (By.XPATH, '//table[@class="cf a8d"]//tr[@class="wbjtpc"]//td[@class="sG Db"]/input[@class="Da"]')))
            self.driver.find_element(By.XPATH,
                                     '//table[@class="cf a8d"]//tr[@class="wbjtpc"]//td[@class="sG Db"]/input[@class="Da"]').send_keys(
                " ")

            textarea = self.driver.find_element(By.XPATH,
                                                '//table[@class="cf An"]//td[@class="Ap"]//div[contains(@class,"Am Al editable")]')
            self.driver.execute_script(f"arguments[0].innerHTML = `{creative}`;", textarea)
            textarea.send_keys(' ')
            self.driver.find_element(By.XPATH, '//button[@guidedhelpid="save_changes_button"]').click()
            WebDriverWait(self.driver, 15).until(EC.url_contains('https://mail.google.com/mail/u/0/#inbox'))
            time.sleep(3)
            return True
        except:
            return False
