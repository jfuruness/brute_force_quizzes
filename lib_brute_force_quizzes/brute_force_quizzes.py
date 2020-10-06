from datetime import datetime
import os
from pprint import pprint
import json
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

class Module:
    def __init__(self, init_num, quizzes: list):
        self.init_num = init_num
        self.quizzes = quizzes

class Brute_Force_Quizzes:
    q_dict_path = "/tmp/quizz.json"

    def __init__(self):
        self.right_browser = None
        self.left_browser = None

    def run(self):
        print("Running")
        print("NOTE: This assumes you've taken them all")
        modules_list = list(range(14, 18))
        quizzes_list = [list(range(4, 9)),
                        list(range(4, 14)),
                        list(range(4, 8))]
        firsttry = True
        modules = []
        for module_num, quizzes_list in zip(modules_list, quizzes_list):
            modules.append(Module(module_num, quizzes_list))
        for module in modules:
            for quiz_num in module.quizzes:
                for i in range(20):
                    print(f"Round {i}")
                    newtry = False
                    if os.path.exists(self.q_dict_path):
                        try:
                            with open(self.q_dict_path, "r") as f:
                                q_dict = json.load(f)
                        except json.decoder.JSONDecodeError:
                            q_dict = {}
                    else:
                        q_dict = {}
                    self.thirty_five_hundred(firsttry=firsttry)
                    firsttry = False
                    self.scroll_down()
                    self.click(module.init_num)
                    self.click(7)  # Quizzes
                    self.click(quiz_num)
                    self.click(5)  # Begin
                    try:
                        self.click(7)  # Start a new submission
                    except selenium.common.exceptions.UnexpectedAlertPresentException:
                        print("Already started new")
                    self.accept_pop_up()
                    clicked_nums = []
                    qs = []
                    clicked_answers = []
                    for q_el in self.left_browser.get_el(_class="takeQuestionDiv ", plural=True):
                        q = self.left_browser.get_el(tag="p", start_node=q_el)
                        parent = self.left_browser.get_el(xpath="..", start_node=q)
                        q = parent.get_attribute("innerText")
                        # Get table
                        table = self.left_browser.get_el(tag="table", start_node=q_el)
                        # Within table, get all els with name of furuness and get text (those are the numbers once you replace the _
                        a_button_nums = []
                        for button_el in self.left_browser.get_el(name="furuness",
                                                                  start_node=table,
                                                                  plural=True):
                            a_button_nums.append(int(button_el.text.replace("_", "")))
                        # Get all p's
                        answers = []
                        for p in self.left_browser.get_el(tag="p",
                                                          start_node=table,
                                                          plural=True):
                            answers.append(p.text)
                        if q_dict.get(q) is None:
                            q_dict[q] = {}
                        click_num = a_button_nums[0]
                        answer_to_click = answers[0]
                        for button_num, a in zip(a_button_nums, answers):
                            if q_dict[q].get(a) is None:
                                q_dict[q][a] = None
                                click_num = button_num
                                answer_to_click = a
                                newtry = True
                        clicked_nums.append(click_num)
                        qs.append(q)
                        clicked_answers.append(answer_to_click)
                    for num in clicked_nums:
                        self.click_radio(num)
                    pprint(q_dict)
                    self.click(6)  # Submit
                    time.sleep(1)
                    self.accept_pop_up()
                    self.click(5)  # View results
                    feedback = []
                    # For every div with a class of details, get the last paragraphs text
                    details = list(self.left_browser.get_el(_class="details", plural=True))
                    for detail, q, a in zip(details, qs, clicked_answers):
                        addme = False
                        finaladd=False
                        for p in self.left_browser.get_el(tag="p", start_node=detail, plural=True):
                            if addme==True:  # one more after selected answers means feedback
                                finaladd=True
                            if p.text in q_dict[q]:
                                # After this there should be feedback, it's the last answer
                                addme=True
                        if finaladd:
                            feedback.append(p.text)
                            q_dict[q][a] = p.text
                        else:
                            feedback.append("WRONG")
                            q_dict[q][a] = "WRONG"

                    # DUMP JSON
                    with open(self.q_dict_path, "w") as f:
                        f.write(json.dumps(q_dict))
                    pprint(q_dict)
#####################################################################

    def refocus(self):
        self.focused_browser.refocus()

    def new_tab(self, *args):
        self.focused_browser.open_new_tab()

    def thirty_five_hundred(self, firsttry=False):
        self._login_to_huskyct(show_links=False, first_time=firsttry)
        self.left_browser.get("https://lms.uconn.edu/ultra/courses/_80636_1/cl/outline")
        self.left_browser.switch_to_iframe()
        self.left_browser.wait_click(_id="menuPuller")
        for _ in range(2):
            self.scroll_down()
        self.show_links()

    def _login_to_huskyct(self, show_links, first_time=False):
        if self.left_browser is None:
            self.left_browser = Browser()
            # Open left browser and align left
            self.left_browser.open(side=Side.LEFT)
        else:
            self.focus_left()
        # left browser goes to huskyct
        self.left_browser.get("https://lms.uconn.edu/")
        if first_time:
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

        if isinstance(number, int):
            # Get all links within the page
            num_str = self.focused_browser._format_number(number)
        elif isinstance(number, string):
            pass
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
        self.accept_pop_up(printme=False)
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



    def click_radio(self, number):
        num_str = self.focused_browser._format_number(number)
        javascript_str = (f"""return document.evaluate("//*[@id='furuness_{num_str}']","""
                          """ document, null, XPathResult.FIRST_ORDERED_NODE_TYPE,"""
                          """ null).singleNodeValue.nextSibling;""")
        try:
            node = self.focused_browser.browser.execute_script(javascript_str)
            self.focused_browser.browser.execute_script("arguments[0].scrollIntoView();", node)
            self.focused_browser.wait(node.get_attribute("id"), By.ID)
            tried = False
            while True:
                try:
                    node.click()
                    if node.is_selected():
                        pass
                    else:
                        node.click()
                    break
                except selenium.common.exceptions.ElementClickInterceptedException:
                    if tried:
                        raise Exception("Fuck couldn't click")
                    else:
                        tried = True
                        self.scroll_up()
                        time.sleep(1)
        except selenium.common.exceptions.JavascriptException as e:
            # This is a button
            if "nextSibling" in str(e):
                javascript_str = (f"""document.evaluate("//*[@id='furuness_{num_str}']","""
                          """ document, null, XPathResult.FIRST_ORDERED_NODE_TYPE,"""
                          """ null).singleNodeValue.nextSibling;""")
            input(e)
            print(e)


    def accept_pop_up(self, *args, printme=True):
        for browser in [self.focused_browser]:#, self.right_browser]:
            try:
                browser.browser.switch_to.alert.accept()
                browser.switch_to_iframe()
            except Exception as e:
                if printme:
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
