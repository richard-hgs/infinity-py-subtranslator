from time import sleep

from selenium import webdriver
import chromedriver_binary  # Adds chromedriver binary to path
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class wait_for_browser(object):
    def __call__(self, driver):
        try:
            return True
        except ValueError:
            print("Couldn't Connect Driver / Driver Closed")
            return False

class wait_for_input_value(object):
    def __init__(self, elout, elin):
        self.elout = elout
        self.elin = elin
        self.prev_len = 0
        self.error_count = 0

    def __call__(self, driver):
        try:
            elout_value_len = len(self.elout.get_attribute("value"))
            elin_value_len = len(self.elin.get_attribute("value"))
            len_diff = 13
            if (elin_value_len > 30):
                len_diff = 20

            if (elin_value_len > 0 and elout_value_len == 0 or elin_value_len > 2 and elout_value_len < 2 or elout_value_len != self.prev_len or elout_value_len < elin_value_len - len_diff):
                self.prev_len = elout_value_len
                sleep(1.5)
                self.error_count = self.error_count + 1

                if (self.error_count > 3):
                    return True
                return False
            else:
                return True
        except ValueError:
            return True

class wait_for_the_attribute_value(object):
    def __init__(self, locator, attribute, value):
        self.locator = locator
        self.attribute = attribute
        self.value = value

    def __call__(self, driver):
        try:
            element_attribute = EC._find_element(driver, self.locator).get_attribute(self.attribute)
            return element_attribute == self.value
        except StaleElementReferenceException:
            return False

def wait_for_driver_close(driver):
    webDriverWait = WebDriverWait(driver, 20)
    webDriverWait.until_not(wait_for_browser())

def open_browser(hide = True):
    options = Options()
    # options.add_argument('--headless')
    options.add_argument('--disable-gpu')

    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
    # driver = webdriver.Chrome()
    driver.get("https://www.deepl.com/pt-BR/translator")
    sleep(5)
    return driver

def changeLanguages(driver, inputLang = "auto", outputLang = "pt-BR"):
    # Perform click on select origin language
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".lmt__language_select__active[dl-test=translator-source-lang-btn]")
        )
    ).click()
    # Wait until select is menu is visible
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, ".lmt__language_select__menu[dl-test=translator-source-lang-list]"))
    )
    # Retrieves all buttons of select menu
    parentOriginLangEl = driver.find_element_by_css_selector(
        ".lmt__language_select__menu[dl-test=translator-source-lang-list]")
    originLangBtnList = parentOriginLangEl.find_elements_by_tag_name("button")
    # Iterate trough select language menu list
    for i in range(0, len(originLangBtnList)):
        originLangBtnAt = originLangBtnList[i]
        originLangBtnAtDlLang = originLangBtnAt.get_attribute("dl-test")
        if (originLangBtnAtDlLang == ("translator-lang-option-" + inputLang.lower())):
            print("Origin language selected:", originLangBtnAtDlLang)
            originLangBtnAt.click()
            break

    # Perform click on select destination language
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".lmt__language_select__active[dl-test=translator-target-lang-btn]")
        )
    ).click()
    # Wait until select is menu is visible
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, ".lmt__language_select__menu[dl-test=translator-target-lang-list]"))
    )
    # Retrieves all buttons of select menu
    parentDestLangEl = driver.find_element_by_css_selector(
        ".lmt__language_select__menu[dl-test=translator-target-lang-list]")
    destLangBtnList = parentDestLangEl.find_elements_by_tag_name("button")
    # Iterate trough select language menu list
    for i in range(0, len(destLangBtnList)):
        destLangBtnAt = destLangBtnList[i]
        destLangBtnAtDlLang = destLangBtnAt.get_attribute("dl-test")
        # destLangBtnAtDlLangVariant = destLangBtnAt.get_attribute("dl-variant")
        # if (destLangBtnAtDlLang == outputLang and (destLangBtnAtDlLangVariant is None or destLangBtnAtDlLangVariant == outputLangVariant)):
        if (destLangBtnAtDlLang == ("translator-lang-option-" + outputLang)):
            print("Destination language selected:", destLangBtnAtDlLang)
            # print("Destination language variant selected:", destLangBtnAtDlLangVariant)
            destLangBtnAt.click()
            break



def translate(driver, text):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "textarea"))
    )
    input_els = driver.find_elements_by_tag_name("textarea")
    input_in = input_els[0]
    input_out = input_els[1]

    # Select Input for translation
    input_in.click()
    input_in.send_keys(text)

    # Wait for translation data
    WebDriverWait(driver, 150).until(
        wait_for_input_value(input_out, input_in)
    )

    # Retrieves translated value from input
    translated = input_out.get_attribute("value")

    # Clear text in value
    input_in.clear()

    return translated