import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def test_multi_user():
    streamlit_input_xpath = "/html/body/div/div[1]/div/div/div/div/section/div/div[1]/div/div[2]/div/div[3]/div/div[1]/div/input"
    url = os.environ["multi_user_test_url"]

    driver.get(url)
    time.sleep(5)
    # TODO: This is not working @aniketmaurya
    element = driver.find_element(by=By.XPATH, value=streamlit_input_xpath)
    element.send_keys("AlexClay")


if __name__ == '__main__':
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    # Download chromedriver first https://chromedriver.chromium.org/downloads
    driver = webdriver.Chrome("chromedriver", options=chrome_options)

    test_multi_user()
    driver.quit()
