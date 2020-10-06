from datetime import datetime
import sys
import time

from pocketsphinx import LiveSpeech
from pynput.keyboard import Key, Controller
import selenium
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .browser import Browser, Side

class Brute_Force_Quizzes:
    def __init__(self):
        self.right_browser = None
        self.left_browser = None

    def run(self):
        print("Running")
        self.thirty_five_hundred()

    def refocus(self):
        self.focused_browser.refocus()

    def new_tab(self, *args):
        self.focused_browser.open_new_tab()

    def thirty_five_hundred(self):
        self._login_to_huskyct(show_links=False)
        self.left_browser.get("https://lms.uconn.edu/ultra/courses/_80636_1/cl/outline")
        self.left_browser.switch_to_iframe()
        self.left_browser.wait_click(_id="menuPuller")
        for _ in range(2):
            self.scroll_down()
        self.show_links()

    def _login_to_huskyct(self, show_links):
        if self.left_browser is None:
            self.left_browser = Browser()
            # Open left browser and align left
            self.left_browser.open(side=Side.LEFT)
        else:
            self.focus_left()
        # left browser goes to huskyct
        self.left_browser.get("https://lms.uconn.edu/")
        try:
            if "https://lms.uconn.edu/ultra/institution-page" in self.left_browser.url:
                print("logged in?")
                raise Exception("Already logged in")
            # Wait for privacy agreement to pop up and click
            self.left_browser.wait_click(_id="agree_button")
            # click login button
            self.left_browser.wait_click(_id="cas-login")
            # Send in username
            self.left_browser.wait_send_keys(_id="username",
                                             keys="chg16109")
            # Send in password
            with open("/tmp/password.txt", "r") as f:
                password = f.read().strip()
            self.left_browser.wait_send_keys(_id="password",
                                             keys=password)
            # Click login
            self.left_browser.get_el(name="submit").click()
        except Exception as e:
            print(e)
            print("Already logged in?")
        self.focused_browser = self.left_browser
        if show_links:
            self.left_browser.get("https://lms.uconn.edu/ultra/course")
            self.focused_browser = self.left_browser
            self.focused_browser.switch_to_iframe()
            self.focused_browser.wait('//*[@id="course-columns-current"]/div', By.XPATH)
            self.show_links()

    def show_links(self, side=None):
        # https://stackoverflow.com/a/21898701/8903959
        self.focused_browser.switch_to_iframe()

        # https://stackoverflow.com/a/24595952
        removal_javascript_str = ("""var ele = document.getElementsByName("furuness");"""
                                  """for(var i=ele.length-1;i>=0;i--)"""
                                  """{ele[i].parentNode.removeChild(ele[i]);}""")
        self.focused_browser.browser.execute_script(removal_javascript_str)


        javascript_strs = []
        elems = []
        # Get all links within the page
        for i, tag in enumerate(self.focused_browser.get_clickable()):
            # Add a number next to all of the links
            javascript_str, elem = self.focused_browser.add_number(i, tag)
            javascript_strs.append(javascript_str)
            elems.append(elem)
        self.focused_browser.browser.execute_script(" ".join(javascript_strs), *elems)

    def click(self, number):
        tag_to_click = None

        old_clickables = self.focused_browser.get_clickable()

        # Get all links within the page
        num_str = self.focused_browser._format_number(number)
        javascript_str = (f"""document.evaluate("//*[@id='furuness_{num_str}']","""
                          """ document, null, XPathResult.FIRST_ORDERED_NODE_TYPE,"""
                          """ null).singleNodeValue.nextSibling.click();""")
        try:
            self.focused_browser.browser.execute_script(javascript_str)
        except selenium.common.exceptions.JavascriptException as e:
            # This is a button
            if "nextSibling" in str(e):
                javascript_str = (f"""document.evaluate("//*[@id='furuness_{num_str}']","""
                          """ document, null, XPathResult.FIRST_ORDERED_NODE_TYPE,"""
                          """ null).singleNodeValue.nextSibling.click();""")
            print(e)

        # Sometimes it opens in a new tab, we must refocus
        self.focused_browser.switch_to_iframe()
        # Wait until clickables change
        for i in range(3):
            clickables = self.focused_browser.get_clickable()
            if clickables != old_clickables:
                break
            else:
                # NOTE: just check if it was a radio button pressed
                # OR store that radio buttons exist on the page when adding numbers
                # Just a simple bool. And if radios on page, wait a lot less if at all
                print("Waiting for change - remind me and I'll fix this later")
                time.sleep(.2)
        self.show_links()

    def accept_pop_up(self, *args):
        for browser in [self.focused_browser]:#, self.right_browser]:
            try:
                browser.browser.switch_to.alert.accept()
                browser.switch_to_iframe()
            except Exception as e:
                print(e)

    def scroll_up(self, *args, browser=None):
        if not browser:
            browser = self.focused_browser

        browser.scroll_up()

    def scroll_down(self, *args, browser=None):
        if not browser:
            browser = self.focused_browser

        browser.scroll_down()

    def page_up(self, *args, browser=None):
        if not browser:
            browser = self.focused_browser
        browser.page_up()

    def page_down(self, *args, browser=None):
        if not browser:
            browser = self.focused_browser
        browser.page_down()

    def focus_left(self, *args):
        self.focused_browser = self.left_browser
        self.focused_browser.refocus()

    def quit(self, *args):
        for attr in ["left_browser", "right_browser"]:
            try:
                getattr(self, attr).browser.quit()
                setattr(self, attr, None)
            except AttributeError as e:
                pass

    def turn_off(self, *args):
        try:
            self.quit()
        except Exception as e:
            print(e)
        sys.exit(0)
