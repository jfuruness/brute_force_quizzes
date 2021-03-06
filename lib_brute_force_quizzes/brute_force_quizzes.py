from datetime import datetime
import os
from pprint import pprint
import re
import json
from subprocess import check_call
import sys
import time
from unidecode import unidecode

from pocketsphinx import LiveSpeech
from pynput.keyboard import Key, Controller
import selenium
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .browser import Browser, Side

class El_w_link:
    def __init__(self, el, parent):
        self.text = el.text
        self.link = parent.get_attribute("href")


class Module(El_w_link):
    pass
class Quiz(El_w_link):
    pass

class Question:
    def __init__(self, el, q_el, links):
        self.el = el
        self.inner_text = q_el.get_attribute("innerHTML")
        self.links = links

    @property
    def text(self):
        link_text = " " + " ".join(str(x) for x in self.links)
        return self.inner_text + link_text

class Answer:
    def __init__(self, num, text, link):
        self.num = num
        self.inner_text = text
        self.link = link

    @property
    def text(self):
        return self.inner_text + " " + str(self.link)

class Brute_Force_Quizzes:
    q_dict_path = "/tmp/quiz.json"

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.right_browser = None
        self.left_browser = None
        self.q_dict = {}
        self.unanswered = []
        try:
            with open(self.q_dict_path, "r") as f:
                self.q_dict = json.loads(f.read())
        except FileNotFoundError:
            pass
        except json.decoder.JSONDecodeError:
            os.remove(self.q_dict_path)

    def run(self):
        self.e = None
        try:
            self._run()
        except Exception as e:
            print(e)
            self.e = e
        finally:
            for unanswered_quiz in self.unanswered:
                input("Unanswered, do by hand" + unanswered_quiz)
            if self.e is not None:
               raise self.e

    def _run(self):
        print("Running")
        self.thirty_five_hundred(True)
        self.modules = self.get_modules()
        self.get_module_quizzes()
        self.focused_browser.browser.maximize_window()
        for mi, module in enumerate(self.modules):
            # Skip unnesseccary mods
            if False:
                continue
            if len(module.quizzes) > 0:
                self.q_dict[module.text] = self.q_dict.get(module.text, {})
                for qi, quiz in enumerate(module.quizzes):
                    if False:
                        continue
                    self.q_dict[module.text][quiz.text] =\
                        self.q_dict[module.text].get(quiz.text, {})
                    self.cur_q = self.q_dict[module.text][quiz.text]
                    times_to_take = 25
                    for i in range(times_to_take):
                        self.take_quiz(quiz, i==(times_to_take - 1))
        self.format(reopen=False, give_feedback=False, only_correct=True)
        self.format(reopen=False, give_feedback=True, only_correct=False)
        self.format(reopen=False, give_feedback=True, only_correct=True)
        self.format(reopen=False, give_feedback=False, only_correct=False)
        input("Hey teacher. Leave those kids alone!")

    def get_module_quizzes(self):
        for module in self.modules:
            print(module.text)
            self.focused_browser.get(module.link)
            try:
                self.click_link_text("Lecture Quizzes")
                module.quizzes = self.get_quizzes()
            # No quizzes in this sectin
            except AttributeError as e:
                module.quizzes = []
        
    def get_modules(self):
        return [Module(el, parent) for el, parent
                in zip(*self.get_el_w_link("Module"))]

    def get_quizzes(self):
        return [Quiz(el, parent) for el, parent
                in zip(*self.get_el_w_link("Q"))
                if parent.get_attribute("href") is not None]

    def get_el_w_link(self, text):
        els = self.focused_browser.get_el(xpath=f"//span[contains(text(),'{text}')]",
                                           plural=True)
        parents = [self.focused_browser.get_el(xpath="..", start_node=el)
                   for el in els]
        return els, parents
            
    def click_link_text(self, text):
        """Gets span within href and gets url and shows links"""

        el = self.focused_browser.get_el(xpath=f"//span[contains(text(),'{text}')]")
        parent = self.focused_browser.get_el(xpath="..", start_node=el)
        self.focused_browser.get(parent.get_attribute("href"))
        self.show_links()
        return

    def take_quiz(self, quiz, last_time):
        self.focused_browser.get(quiz.link)
        self.start_quiz(quiz)
        questions = self.get_questions()
        for question in questions:
            self.get_answer_objects(question)
            self.select_unchosen_answer(question, last_time, quiz)
        self.submit_quiz()
        self.get_feedback(questions)
        if last_time:
            pass
            # input("verify that you chose correctly")
        self.save_feedback(questions)

    def start_quiz(self, quiz):
        try:
            self.focused_browser.get_el(name="bottom_Begin").click()
        except AttributeError:
            self.focused_browser.get_el(name="bottom_Continue").click()
        start_new = self.focused_browser.get_el(xpath="//a[contains(text(),'Start New')]")
        if start_new is not None:
            start_new.click()
        self.show_links()

    def get_questions(self):
        questions = []
        for q_el in self.left_browser.get_el(_class="takeQuestionDiv ",
                                             plural=True):
            q = self.left_browser.get_el(tag="legend", start_node=q_el)
            questions.append(Question(q_el, q, self.get_img_links(q)))
        return questions

    def get_answer_objects(self, question):
        # Get table
        # Must be plural because sometimes q is a table
        table = self.left_browser.get_el(tag="table",
                                         start_node=question.el,
                                         plural=True)[-1]
        # Within table, get all els with name of furuness 
        # get text (those are the numbers once you replace the _
        a_button_nums = self.get_button_nums(table)
        answer_texts, img_links = self.get_answers(table)
        answers = []
        for i, (a_button_num, answer_text) in enumerate(zip(a_button_nums,
                                                             answer_texts)):
            link = img_links[i] if i < len(img_links) else None
            answers.append(Answer(a_button_num, answer_text, link))
        question.answers = answers

    def get_button_nums(self, table):
        a_button_nums = []
        for button_el in self.left_browser.get_el(name="furuness",
                                                  start_node=table,
                                                  plural=True):
            a_button_nums.append(int(button_el.text.replace("_", "")))
        return a_button_nums

    def get_answers(self, table):
        # Get all p's
        answers = []
        img_links = []
        for i, p in enumerate(self.left_browser.get_el(tag="label",
                                                       start_node=table,
                                                       plural=True)):
            answers.append(p.get_attribute("innerHTML"))
            # UGHHHHHHH STOP IT
            a_img_links = self.get_img_links(p, double_parent=True)
            img_links.append(None if len(a_img_links) == 0 else a_img_links[0])
        return answers, img_links

    def select_unchosen_answer(self, question, last_time: bool, quiz):
        """Selects last answer every time except for the last time

        Done for speed, last answer requires less scrolling
        But the last time through, get it correctly
        """

        print(question.text)
        print(f"Answer texts {[x.text for x in question.answers]}")
        # Last one to reduce scrolling time
        selected_answer = question.answers[-1].text
        known = True
        for answer, feedback in self.cur_q.get(question.text, {}).items():
            if feedback is None:
                selected_answer = answer
                known = False
        if known is True and last_time is True:
            try:
                # wtf r u doing
                selected_answer = [k for k, v in self.cur_q[question.text].items()
                                   if "CORRECT" in v][0]
            except IndexError:
                self.unanswered.append(quiz.text)
                input(f"Unanswered quizzes: {self.unanswered}")
            except KeyError:
                print("key error issue")
                from pprint import pprint
                print("printing json")
                pprint(self.cur_q)
                print("printing qustion te")
                print(question.text)
                print("printing inner text")
                print(question.inner_text)
                for a in question.answers:
                    print("new answer")
                    print(a.inner_text)
                    print(a.link)
                    print(a.text)
                input("Key Error problems")
        # Shame on you
        try:
            question.selected_answer = [a for a in question.answers
                                        if a.text == selected_answer][0]
        except IndexError:
            print(selected_answer)
            input("index probs")
        self.click_radio(question.selected_answer.num)

    def submit_quiz(self):
        self.focused_browser.get_el(name="bottom_Save and Submit").click()
        self.accept_pop_up()
        self.focused_browser.get_el(xpath="//a[contains(text(),'OK')]").click()

    def get_feedback(self, questions):
        feedback_els = self.left_browser.get_el(_class="details", plural=True)
        # A little part of me just died
        counter = 1
        for feedback_el, question in zip(feedback_els, questions):
            gif = self.focused_browser.get_el(_id=f"gs_q{counter}")
            if "Correct" == gif.get_attribute("title"):
                question.feedback = "CORRECT: "
            else:
                question.feedback = "WRONG"
            # Honestly fuck you
            counter += 1
            last_row = self.focused_browser.get_el(tag="tr",
                                                   plural=True,
                                                   start_node=feedback_el)[-1]
            text = last_row.get_attribute("innerText")
            if "Answer Feedback" in text:
                question.feedback += text.replace("Answer Feedback",
                                                  "").replace("Correct",
                                                              "").strip()

    def save_feedback(self, questions):
        for question in questions:
            self.cur_q[question.text] = self.cur_q.get(question.text, {})
            cur = self.cur_q[question.text]
            for answer in question.answers:
                cur[answer.text] = cur.get(answer.text, None)
            cur[question.selected_answer.text] = question.feedback
        self.save_json()

    def save_json(self):
        # DUMP JSON
        with open(self.q_dict_path, "w") as f:
            f.write(json.dumps(self.q_dict))

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
                                                 keys=self.username)
                if self.password is None:
                    # Send in password
                    with open("/tmp/password.txt", "r") as f:
                        self.password = f.read().strip()
                self.left_browser.wait_send_keys(_id="password",
                                                 keys=self.password)
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
        node = self.focused_browser.browser.execute_script(javascript_str)
        self.focused_browser.browser.execute_script("arguments[0].scrollIntoView();", node)
        self.focused_browser.wait(node.get_attribute("id"), By.ID)

        tried = False
        for _ in range(2):
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

    def focus_left(self, *args):
        self.focused_browser = self.left_browser
        self.focused_browser.refocus()

    def format_markdown(self):
        with open(self.q_dict_path, "r") as f:
            q = json.loads(f.read())
        md_path = self.q_dict_path.replace("json", "md")
        with open(md_path, "w") as f:
            for module, quizzes in q.items():
                f.write("# " + self.strip(module) + "\n")
                for quiz_name, quiz_dict in quizzes.items():
                    f.write("## " + self.strip(quiz_name) + "\n")
                    for question, answers_dict in quiz_dict.items():
                        question_md = self.convert_link_text(question)
                        f.write("* " + self.strip(question_md) + "\n")
                        for answer, feedback in answers_dict.items():
                            if feedback is None:
                                f.write("    * No answer for this question???\n")
                            else:
                                answer_md = self.convert_link_text(answer)
                                f.write("    * " + self.strip(answer_md) + "\n")
                                f.write("        * " + self.strip(feedback) + "\n")
                    f.write("\n")
        # https://stackoverflow.com/a/55484165/8903959
        pdf_path = self.q_dict_path.replace("json", "pdf")
        check_call(f'pandoc {md_path} -o {pdf_path}', shell=True)
        short_pdf_path = pdf_path.replace(".pdf", "_short.pdf")
        margins = "geometry:margin=1cm"
        check_call(f'pandoc {md_path} -V {margins} -o {short_pdf_path}',
                   shell=True)

    def format(self, reopen=True, give_feedback=False, only_correct=True, from_main=False):
        with open(self.q_dict_path, "r") as f:
            q = json.loads(f.read())
        md_path = self.q_dict_path.replace("json", "html")
        with open(md_path, "w") as f:
            f.write("""<html>
                     <head>
                      <title>3500 quizzes</title>
                    </head>
                    <body>""")
            for module, quizzes in q.items():
                f.write("<h1>" + self.strip(module) + "</h1>\n")
                print(quizzes)
                for quiz_name, quiz_dict in quizzes.items():
                    f.write("<h3>" + self.strip(quiz_name) + "</h3>\n")
                    f.write("<ol>\n")
                    for question, answers_dict in quiz_dict.items():
                        question_md = self.convert_link_text(question)
                        f.write("<li>" + self.strip(question_md) + "\n")
                        f.write("<ul>\n")
                        for answer, feedback in answers_dict.items():
                            
                            if only_correct and (feedback is None or "WRONG" in feedback):
                                continue
                            if feedback is None:
                                f.write("<li>")
                                f.write("    * No answer for this question???\n")
                                f.write("</li>\n")
                            else:
                                f.write("<li>")
                                answer_md = self.convert_link_text(answer)
                                f.write(self.strip(answer_md))
                                if give_feedback:
                                    f.write("</li>\n<ul><li>")
                                    f.write(self.strip(feedback))
                                    f.write("</li></ul>\n")
                                else:
                                    f.write("</li>\n")
                        f.write("</ul>\n")
                    f.write("</ol>\n")
                    f.write("\n")
            f.write("""</body>
                    </html>""")
        if reopen:
            self.thirty_five_hundred(True)
        cookies = self.focused_browser.browser.get_cookies()
        self.focused_browser.browser.delete_all_cookies()
        for cookie in cookies:
            cookie["secure"] = True
            cookie['sameSite'] = "None"
        for cookie in cookies:
            self.focused_browser.browser.add_cookie(cookie)
        print(md_path)
        self.left_browser.open_new_tab(url=md_path)
        self.focused_browser.browser.get("file://" + md_path)
        # https://stackoverflow.com/a/55484165/8903959
        pdf_path = md_path.replace("html", "pdf")
        if from_main:
            self.format(reopen=False, give_feedback=True, only_correct=False)
            self.format(reopen=False, give_feedback=True, only_correct=True)
            self.format(reopen=False, give_feedback=False, only_correct=False)
            input("wait")
        #check_call(f'pandoc {md_path} -t latex -o {pdf_path}', shell=True)
        #short_pdf_path = pdf_path.replace(".pdf", "_short.pdf")
        #margins = "geometry:margin=1cm"
        #check_call(f'pandoc {md_path} -V {margins} -o {short_pdf_path}',
        #           shell=True)

 
    def convert_link_text(self, text):
        """I know there could be multiple links. I don't care"""

        if "bbcsweb" in text:
            link_reg = "http.*png"
        else:
            link_reg = "http.*"
        link = re.search(link_reg, text)
        if link is not None:
            link = link.group(0)
            link_md = self.get_link_md(link)
            text = text.replace(link, link_md)
        if text[-4:] == "None":
            text = text[:-4]
        if "http" in text:
            text = text[:text.index("http")]
        return text

    def get_link_md(self, link):
        return f'<img src="{link.replace(";","%3B")}">'
        return f'<a>![Foo]({link})</a>'


    def strip(self, string):
        try:
            return string
            for char in ["\t", "\n", "::"]:
                string = string.replace(char, "")
            return unidecode(string)
        except AttributeError:
            raise Exception(f"Couldn't format {string}")

    def get_img_links(self, el, double_parent=False):
        """Gets all image links"""

        links = []
        try:
            double_parent_str = ""
            if double_parent:
                double_parent_str = ".parentNode.parentNode"
            javascript_str = (f"var imgs = arguments[0]{double_parent_str}"
                              ".getElementsByTagName('img');"
                              "var mylinks = [];"
                              "for (var j = 0; j < imgs.length; j++) {"
                              "  mylinks.push(imgs[j].getAttribute('src'));"
                              "}"
                              "return mylinks")
            raw_links = self.focused_browser.browser.execute_script(javascript_str, el)
            for link in raw_links:
                if "http" not in link:
                    link = "https://lms.uconn.edu" + link
                    handle = self.focused_browser.browser.current_window_handle
                    self.focused_browser.open_new_tab()
                    self.focused_browser.browser.get(link)
                    link = self.focused_browser.browser.current_url
                    self.focused_browser.browser.close()
                    self.focused_browser.browser.switch_to.window(handle)
                    self.focused_browser.switch_to_iframe()
                links.append(link)
        except:
            input("img link issue, investigate")
        return links 
