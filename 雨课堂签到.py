from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
import requests
import schedule
import time
import os
import sys

# 设置ChromeDriver路径
CHROMEDRIVER_PATH = r'/usr/bin/chromedriver'


# 向服务器发送通知的函数
def send_notification(title, content):
    url = "http://www.pushplus.plus/send"
    data = {
        "token": "340d3858fcaa4550a19c73ea6361db99",
        "title": title,
        "content": content,
        "topic": ""  # 群组
    }
    response = requests.post(url, json=data)
    print("通知已发送:", response.status_code)
    print("响应内容:", response.text)  # 打印响应内容


# 主函数
global driver


def execute_code():
    global driver
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument(f'--user-data-dir={os.path.expanduser("~/.config/google-chrome")}')
        chrome_options.add_argument('--log-level=3')

        service = Service(CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.get("https://sziit.yuketang.cn/pro/courselist")

        try:
            login_button = WebDriverWait(driver, 10).until(
                ec.presence_of_element_located(
                    (By.XPATH, '//button[@class="el-button login-btn el-button--primary"]'))
            )
            if login_button:
                messages = ["未登录", "请检查", "跑路了886"]
                for message in messages:
                    send_notification("重要错误", message)
                    time.sleep(5)
                    sys.exit(1)
        except TimeoutException:
            return

        try:
            trigger_element = WebDriverWait(driver, 10).until(
                ec.presence_of_element_located((By.XPATH, '//div[@class="spinner"]'))
            )
            trigger_element.click()
        except TimeoutException:
            print("超时警告: 触发元素未能及时出现。")
            return

        try:
            target_elements = WebDriverWait(driver, 10).until(
                ec.presence_of_all_elements_located((By.XPATH, '//i[@class="iconfont icon--yinpinbofang"]'))
            )
        except TimeoutException:
            print("超时警告: 目标元素未能及时出现。")
            return

        for target_element in target_elements:
            target_url = target_element.get_attribute("href")

            if target_url is None:
                continue
            target_element.click()
            time.sleep(10)
            send_notification("成功", f"打开目标网页成功: {target_url}")

    finally:
        try:
            driver.quit()
        except Exception as e:
            send_notification("错误", f"无法关闭浏览器，可能导致内存泄漏: {e}")


# 每隔30分钟执行一次代码
schedule.every(30).minutes.do(execute_code)

# 立即执行一次
execute_code()

# 循环执行
while True:
    schedule.run_pending()
    time.sleep(1)

# chrome和chromedriver下载镜像
# https://googlechromelabs.github.io/chrome-for-testing/#stable
