# ==============================================================================
# File: esb_navigator_test.py
# Project: Tests
# File Created: Thursday, 15th October 2020 7:30:42 pm
# Author: Dillon Koch
# -----
# Last Modified: Friday, 23rd October 2020 8:23:35 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Test suite for esb_navigator.py
# ==============================================================================

import logging
import sys
from os.path import abspath, dirname

import bs4
import pytest
from bs4 import BeautifulSoup as soup
from selenium import webdriver

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


from ESB.esb_navigator import ESB_Navigator


@pytest.fixture  # Fixture
def true_leagues():
    return ['NFL', 'NBA', 'NCAAF', 'NCAAB']


@pytest.fixture(scope='session')  # Fixture
def navigator():
    return ESB_Navigator()


@pytest.fixture(scope='session')  # Fixture
def homepage_sp(navigator):
    homepage_sp = navigator.reset_window()
    navigator.driver.quit()
    return homepage_sp


def test_setup(navigator):
    assert navigator.start_link == 'https://www.elitesportsbook.com/sports/home.sbk'

    assert isinstance(navigator.fake_nested_dropdowns, list)
    for item in navigator.fake_nested_dropdowns:
        assert isinstance(item, str)

    assert isinstance(navigator.logger, logging.Logger)


def test_section_dict(navigator, true_leagues):  # Property
    assert isinstance(navigator.section_dict, dict)

    sections = list(navigator.section_dict.keys())
    for section in sections:
        assert isinstance(section, str)

    leagues = list(navigator.section_dict.values())
    for league in leagues:
        assert league in true_leagues


def test_get_soup_sp(homepage_sp):  # Global Helper
    assert isinstance(homepage_sp, soup)


@pytest.mark.selenium
def test_reset_window(homepage_sp):  # Top Level
    assert isinstance(homepage_sp, soup)
    # title matches homepage title (to be sure it's the right sp)
    esb_title = homepage_sp.find_all('title')[0].get_text()
    assert esb_title == 'Online Football Betting and Sports Wagering at Elite Sportsbook'


@pytest.mark.selenium
def test_get_section_pairs(navigator, homepage_sp, true_leagues):  # Top Level
    section_pairs = navigator.get_section_pairs(homepage_sp)

    assert isinstance(section_pairs, list)
    for pair in section_pairs:
        assert isinstance(pair, tuple)
        league, sp = pair
        assert league in true_leagues
        print(type(sp))
        assert isinstance(sp, bs4.element.Tag)


@pytest.mark.selenium
def test_get_section_title(navigator, homepage_sp):  # Top Level
    section_pairs = navigator.get_section_pairs(homepage_sp)

    for section_pair in section_pairs:
        _, sp = section_pair
        title = navigator.get_section_title(sp)
        assert isinstance(title, str)
        assert title in navigator.section_dict.keys()


@pytest.mark.selenium
def test_click_button(navigator):  # Top Level
    driver = webdriver.Firefox(executable_path=ROOT_PATH + "/geckodriver")
    driver.get(navigator.start_link)
    navigator.driver = driver
    start_sp = navigator._get_soup_sp()

    name = "Iowa"
    navigator.click_button(name, upper=True)
    end_sp = navigator._get_soup_sp()
    assert str(start_sp) != str(end_sp)

    navigator.driver.quit()


# @pytest.fixture(scope='session')  # Fixture
# def nested_dropdown_list(navigator, homepage_sp):
#     section_pairs = navigator.get_section_pairs(homepage_sp)

#     nested_dropdown_list = []
#     for section_pair in section_pairs:
#         league, sp = section_pair
#         title = navigator.get_section_title(sp)
#         nested_dropdowns = navigator.find_nested_dropdowns(sp, title)
#         nested_dropdown_list.append(nested_dropdowns)
#     return nested_dropdown_list

def get_nested_dropdowns(navigator, homepage_sp):
    section_pairs = navigator.get_section_pairs(homepage_sp)

    nested_dropdown_list = []
    for section_pair in section_pairs:
        league, sp = section_pair
        title = navigator.get_section_title(sp)
        nested_dropdowns = navigator.find_nested_dropdowns(sp, title)
        nested_dropdown_list.append(nested_dropdowns)
    return nested_dropdown_list


@pytest.mark.selenium
def test_find_nested_dropdowns(navigator, homepage_sp):  # Top Level
    nested_dropdown_list = get_nested_dropdowns(navigator, homepage_sp)
    for nested_dropdowns in nested_dropdown_list:
        assert isinstance(nested_dropdowns, list)
        for item in nested_dropdowns:
            assert isinstance(item, str)
            assert item.strip() == item


def test_click_nested_dropdowns(navigator):
    pass
    # navigator.reset_window()
    # section_pairs = navigator.get_section_pairs(homepage_sp)
    # for section_pair in section_pairs:
    #     nested_dropdowns
