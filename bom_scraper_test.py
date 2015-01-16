__author__ = 'rwill127'

from nose.tools import *
import bom_scraper as b
import re
from bs4 import BeautifulSoup


class TestPage(object):
    def __init__(self):
        self.test_id = "marvel2014a"
        self.page = b.get_movie_page(self.test_id)
        self.soup = BeautifulSoup(self.page.text)

    def test_getpage(self):
        #The BOM id for Guardians of the Galaxy
        t_page = b.get_movie_page(self.test_id)
        t_match = re.search("Guardians of the Galaxy", t_page.text)
        #Test that, at least, what comes back contains the words "Guardians of the Galaxy"
        #which is pretty unlikely unless it successfully pulled the page for GotG
        ok_(t_match)
        eq_(t_match.group(0), "Guardians of the Galaxy")

    def test_get_title(self):
        t = b.parse_movie_title(self.soup)
        eq_(t, "Guardians of the Galaxy")

    def test_get_dom_gross(self):
        g = b.parse_dom_gross(self.soup)
        eq_(g, 333130696)

    def test_get_budg(self):
        budg = b.parse_budget(self.soup)
        eq_(budg, 170000000)

    def test_find_money_string_succeed(self):
        label = self.soup.find("td", text="Domestic:")
        data_row = label.parent
        r = b.find_money_pattern(data_row)
        eq_(r, "$333,130,696")

    def test_find_money_string_fail(self):
        row = self.soup.find("tr")
        r = b.find_money_pattern(row)
        eq_(r, None)

    def test_world_gross(self):
        w = b.parse_world_gross(self.soup)
        eq_(w, 772730696)

    def test_rating(self):
        r = b.parse_rating(self.soup)
        eq_(r, "PG-13")

    def test_date_parse(self):
        d = b.parse_release_date(self.soup)
        eq_(d.strftime("%x"), "08/01/14")

    def test_page_parse(self):
        m = b.parse_movie_page(self.page)
        eq_(m["title"], "Guardians of the Galaxy")
        eq_(m["rating"], "PG-13")
        eq_(m["release date"].strftime("%x"), "08/01/14")
        eq_(m["domestic gross"], 333130696)
        eq_(m["worldwide gross"], 772730696)
        eq_(m["budget"], 170000000)