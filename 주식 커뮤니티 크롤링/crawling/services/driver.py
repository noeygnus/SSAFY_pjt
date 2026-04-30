import os
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service


BASE_DIR = Path(__file__).resolve().parent.parent.parent


def get_chrome_driver():
    chrome_driver_path = BASE_DIR / "chromedriver-win64" / "chromedriver.exe"

    chrome_options = webdriver.ChromeOptions()

    # 브라우저 최대화
    chrome_options.add_argument("--start-maximized")

    # 자동화 감지 완화
    chrome_options.add_argument("disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option(
        "excludeSwitches",
        ["enable-automation", "enable-logging"],
    )

    # 불필요한 로그 줄이기
    chrome_options.add_argument("--log-level=3")

    service = Service(
        executable_path=str(chrome_driver_path),
        log_output=os.devnull,
    )

    return webdriver.Chrome(service=service, options=chrome_options)