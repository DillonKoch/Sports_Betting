# ==============================================================================
# File: parent_navigator.py
# Project: Scrapers
# File Created: Sunday, 16th May 2021 4:42:55 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 16th May 2021 4:42:57 pm
# Modified By: Dillon Koch
# -----
#
# -----
# parent class for all child web navigators
# includes the typical navigation actions used in selenium across different sites
# ==============================================================================


import os
import sys
import time
from os.path import abspath, dirname

from bs4 import BeautifulSoup as soup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


class Parent_Navigator:
    def __init__(self):
        pass

    def new_window(self, link, headless=False):  # Top Level
        """
        creates a new window in Firefox and goes to the input link
        """
        options = Options()
        options.headless = headless
        self.driver = webdriver.Firefox(executable_path=ROOT_PATH + "/geckodriver", options=options)
        time.sleep(1)
        self.driver.get(link)
        self.driver.maximize_window()

    def scroll_to_bottom(self):  # Global Helper
        """
        scrolls to the bottom of the page
        """
        self.driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.END)

    def scroll_to_top(self):  # Global Helper
        """
        scrolls to the top of the page
        """
        self.driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.HOME)

    def get_html(self):  # Global Helper
        """
        returns the BeautifulSoup (html) object of the current page
        """
        html = self.driver.page_source
        sp = soup(html, 'html.parser')
        return sp

    def click_button(self, name):  # Global Helper
        """
        """
        time.sleep(2)
        button = self.driver.find_element_by_link_text(name)
        button.click()
        time.sleep(2)
        return self.get_html()

    def _delete_geckodriver_log(self):  # Specific Helper exit_browser
        """
        deletes the annoying and useless geckodriver.log file automatically for me
        """
        paths = listdir_fullpath(ROOT_PATH + "/scrapers/")
        for path in paths:
            if 'geckodriver.log' in path:
                os.remove(path)

    def exit_browser(self):  # Top Level
        """
        exits the selenium browser after 5 seconds
        """
        time.sleep(5)
        self.driver.quit()
        self._delete_geckodriver_log()


if __name__ == '__main__':
    x = Parent_Navigator()
    self = x
    x.run()
