import time
import requests
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException


class ig_bug:
    def __init__(self, account):
        self.folder_name = 'result/' + account
        self.account = account
        self.post_index = 0
        self.create_folder(account)
        # your account
        self.username = 'your username'
        self.password = 'your password'

    def start_bug(self, dl_number):
        path = "D:\python-bug\ig_post_parse\chromedriver-win64\chromedriver.exe"
        chrome_driver_path = Service(path)
        driver = webdriver.Chrome(service=chrome_driver_path)
        driver.maximize_window()
        url = 'https://www.instagram.com/'
        driver.get(url)

        time.sleep(1)
        self.login(self.username, self.password, driver)

        # first-photo
        first_ph = driver.find_element(By.CSS_SELECTOR, '._aagw')
        first_ph.click()

        page_window = driver.find_element(
            By.CSS_SELECTOR, '.x1cy8zhl.x9f619.x78zum5.xl56j7k.x2lwn1j.xeuugli.x47corl')

        for i in range(dl_number):
            print("This is number ", i+1, " posts")
            retry_count = 0
            img_url = ''
            post_text = ''
            while retry_count < 2:
                try:
                    post_text_window = driver.find_element(
                        By.CSS_SELECTOR, '._ap3a._aaco._aacu._aacx._aad7._aade')
                    post_text = post_text_window.text
                    print('post_text: ', post_text)

                    img_url = self.get_img_url(page_window)
                    print('img_url: ', img_url)
                    break
                except NoSuchElementException:
                    print('The post is a theme.\n')
                    self.post_index += 1
                    break
                except StaleElementReferenceException:
                    retry_count += 1
                    print('retry_count: ', retry_count)
                    time.sleep(3)
            if img_url != '':
                self.dl_img(img_url)
                self.dl_post_text(post_text)

            self.post_index += 1
            next_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '._aaqg._aaqh')))

            next_button.click()
            time.sleep(1)

    def dl_img(self, img_url):
        res = requests.get(img_url)
        if res.status_code == 200:
            file_name = self.folder_name + '/' + \
                self.account + '_' + str(self.post_index) + '.jpg'
            with open(file_name, 'wb') as f:
                f.write(res.content)
            print(f"Image saved as {file_name}")
        else:
            print(f"Failed to download image from {img_url}")

    def get_img_url(self, page_window):
        img_url = ''
        try:
            img = page_window.find_element(
                By.CSS_SELECTOR, '.x5yr21d.xu96u03.x10l6tqk.x13vifvy.x87ps6o.xh8yej3')
            img_url = img.get_attribute('src')
        except errors.ElementNotFoundError:
            print('Not found the element')
        return img_url

    def dl_post_text(self, post_text):
        file_name = self.folder_name + '/' + \
            self.account + '_' + str(self.post_index) + '.txt'
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(post_text)
        print(f"Post-text saved as {file_name}")

    def create_folder(self, folder_name):
        if not os.path.exists(self.folder_name):
            os.makedirs(self.folder_name)

    def login(self, username, password, driver):
        login = True

        wait = WebDriverWait(driver, 10)

        try:

            username_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, 'username')))
            password_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, 'password')))

            username_input.send_keys(username)
            time.sleep(1)
            password_input.send_keys(password)
            time.sleep(3)

            # click login
            login_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'button[type="submit"]')))

            login_button.click()

            time.sleep(5)

        except Exception:
            login = False

        if login:
            self.remove_notification(driver, wait)

    def remove_notification(self, driver, wait):
        try:
            store_button = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="button"]')))
            store_button.click()
            time.sleep(3)

            notification_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'button._a9--._ap36._a9_1')))

            notification_button.click()
            time.sleep(3)

            # parse-account
            parser_account = "https://www.instagram.com/" + self.account + "/"
            driver.get(parser_account)
            time.sleep(5)

        except NoSuchElementException:
            print("No Notification Pop up occur")


if __name__ == '__main__':
    account = 'the account you want to parse'
    dl_number = 5

    parser = ig_bug(account)
    parser.start_bug(dl_number)

    print("Already DownLoad.")
