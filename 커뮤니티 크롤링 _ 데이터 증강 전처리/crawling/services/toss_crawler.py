import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .driver import get_chrome_driver


def fetch_comments(company_name, limit=20, max_scroll=10):
    driver = get_chrome_driver()

    try:
        # 1. 토스증권 메인 접속
        driver.get("https://www.tossinvest.com/")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # 2. 검색창 열기
        body = driver.find_element(By.TAG_NAME, "body")
        body.send_keys("/")
        time.sleep(1)

        # 3. 회사명 검색
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@placeholder='검색어를 입력해주세요']")
            )
        )
        search_input.send_keys(company_name)
        search_input.send_keys(Keys.ENTER)

        # 4. 주문 페이지 이동 대기
        WebDriverWait(driver, 15).until(EC.url_contains("/order"))

        current_url = driver.current_url
        parts = current_url.split("/")

        stock_code = ""
        if "stocks" in parts:
            stock_code = parts[parts.index("stocks") + 1]

        # 실제 종목명은 일단 입력값으로 임시 처리
        matched_company_name = company_name

        # 5. 커뮤니티 페이지 이동
        community_url = f"https://www.tossinvest.com/stocks/{stock_code}/community"
        driver.get(community_url)

        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#stock-content"))
            )
        except Exception:
            pass

        time.sleep(2)

        # 6. 댓글 수집
        comments = []
        last_height = driver.execute_script("return document.body.scrollHeight")

        comment_selectors = [
            "div > div.tc3tm81 > div > div.tc3tm85 > span > span",
            "article.comment span",
            "#stock-content article span",
        ]

        for _ in range(max_scroll):
            spans = []

            for selector in comment_selectors:
                spans = driver.find_elements(By.CSS_SELECTOR, selector)
                if spans:
                    break

            for span in spans:
                text = span.text.strip()
                if text and text not in comments:
                    comments.append(text)

            if len(comments) >= limit:
                break

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break

            last_height = new_height

        return {
            "matched_company_name": matched_company_name,
            "stock_code": stock_code,
            "raw_comments": comments[:limit],
        }

    finally:
        driver.quit()