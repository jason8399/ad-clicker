import time
import traceback

from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoSuchWindowException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from cookies import Cookies

def click_hidden_elem_handle(driver, elem):
    driver.execute_script("arguments[0].click()", elem)

def nested_iframe_handle(driver):
    try:
        elems = driver.find_elements_by_css_selector('a[href*="adclick"],a[href*="javascript"]')
        for elem in elems:
            click_hidden_elem_handle(driver, elem)
    except NoSuchElementException:
        pass
    try:
        next_iframe = driver.find_element_by_css_selector('iframe')
    except NoSuchElementException as err:
        return
    driver.switch_to.frame(next_iframe)
    nested_iframe_handle(driver)
    driver.switch_to.parent_frame()

def click_ads(driver):
    iframes = driver.find_elements_by_css_selector('iframe[id*="ads"]')
    for iframe in iframes:
        try:
            driver.switch_to.frame(iframe)
            elem = driver.find_element_by_css_selector('a[href*="adclick"],a[href*="javascript"]')
            #click_hidden_elem_handle(driver, elem) # This is too fast
            elem.click()
        except ElementClickInterceptedException as err:
            click_hidden_elem_handle(driver, elem)
        except NoSuchElementException as err:
            nested_iframe_handle(driver)
        except Exception as err:
            traceback.print_exc()
        finally:
            driver.switch_to.default_content()
    # Close tabs
    tabs = driver.window_handles
    first_tab = tabs.pop(0)
    for tab in tabs:
        try:
            driver.switch_to.window(tab)
            driver.close()
        except NoSuchWindowException:
            pass
    driver.switch_to.window(first_tab)

# Set User-Agent
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.16 Safari/537.36')

# Start
driver = webdriver.Chrome(options=chrome_options)

# Load cookies to bypass recaptcha V3
cookies = Cookies("cookies.txt")
driver.get("https://www.mobile01.com/")
for cookie in cookies.cookies:
    driver.add_cookie(cookie)

# Reload page and click homepage ads.
driver.refresh()
click_ads(driver)

# Load topic and click ads in topics
topics = driver.find_elements_by_css_selector('a[href*="topicdetail.php"]')
for topic_num in range(len(topics)):
    topic = topics[topic_num]
    try:
        topic.click()
    except ElementNotInteractableException as err:
        click_hidden_elem_handle(driver, topic)
    time.sleep(5)
    click_ads(driver)
    driver.back()
    time.sleep(5)
    topics = driver.find_elements_by_css_selector('a[href*="topicdetail.php"]')

print("done")
