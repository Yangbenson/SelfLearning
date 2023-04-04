from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time


# Web Scraper---------------------------------------------------------------------
# g_URL = "https://open.spotify.com/genre/section0JQ5DAzQHECxDlYNI6xD1h"

def Spotify_Genre_scraper(g_URL):
    # 自動下載ChromeDriver
    service = ChromeService(executable_path=ChromeDriverManager().install())

    # 關閉通知提醒

    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("headless")
    prefs = {"profile.default_content_setting_values.notifications": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--allow-running-insecure-content')
    # user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
    # chrome_options.add_argument(f'user-agent={user_agent}')

    # 開啟瀏覽器
    driver = webdriver.Chrome(service=service, chrome_options=chrome_options)
    driver.set_window_position(-1500, 0)
    driver.maximize_window()

    driver.get(g_URL)

    time.sleep(1)

    login = driver.find_element(by=By.XPATH, value='//*[@id="main"]/div/div[2]/div[1]/header/div[5]/button[2]')
    login.click()
    time.sleep(3)

    # tell the driver to login with the credentials provided above
    email = driver.find_element(By.ID, 'login-username')
    email.send_keys("aoaoaona@gmail.com")
    password = driver.find_element(By.ID, 'login-password')
    password.send_keys("Benson0326")
    password.send_keys(Keys.RETURN)


    driver.get(g_URL)

    actions = ActionChains(driver)
    for i in range(200):
        if i  == 100:
            time.sleep(2)
        actions.send_keys(Keys.TAB).perform()

    theurl = []
    geturl = driver.find_elements(by=By.XPATH, value='//a[@class="Nqa6Cw3RkDMV8QnYreTr"]')
    for i in geturl:
        url_id = i.get_attribute('href').split("/")[4]
        theurl.append(url_id)
    print(theurl)
    print(len(theurl))
    return theurl
