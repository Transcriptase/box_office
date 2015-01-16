__author__ = 'rwill127'

from nose.tools import *
import bom_scraper as b
import re
from bs4 import BeautifulSoup


class TestPage(object):
    def __init__(self):
        self.test_id = "marvel2014a"
        #The BOM id for Guardians of the Galaxy, for testing
        self.page = b.get_movie_page(self.test_id)
        self.soup = BeautifulSoup(self.page.text)
        #These comparisons work for the week of 1/16/15, might need to adjust them to whatever is current
        #Or I could switch this to an old movie that's not changing.
        #TODO: Switch to an old movie that won't change

    def test_getpage(self):
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
        eq_(g, 333145154)

    def test_get_budg(self):
        budg = b.parse_budget(self.soup)
        eq_(budg, 170000000)

    def test_find_money_string_succeed(self):
        label = self.soup.find("td", text="Domestic:")
        data_row = label.parent
        r = b.find_money_pattern(data_row)
        eq_(r, "$333,145,154")

    def test_find_money_string_fail(self):
        row = self.soup.find("tr")
        r = b.find_money_pattern(row)
        eq_(r, None)

    def test_world_gross(self):
        w = b.parse_world_gross(self.soup)
        eq_(w, 772745154)

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
        eq_(m["release year"], "2014")
        eq_(m["domestic gross"], 333145154)
        eq_(m["worldwide gross"], 772745154)
        eq_(m["budget"], 170000000)

class TestYear(object):
    def __init__(self):
        self.year = 2013
        self.page = b.get_year_page(self.year)
        self.list = b.get_id_list(self.page)

    def test_get_year_page(self):
        p = b.get_year_page(self.year)
        p_match = re.search("2013 DOMESTIC GROSSES", p.text)
        ok_(p_match)

    def test_make_id_list(self):
        list = b.get_id_list(self.page)
        eq_(len(list), 100)
        ok_(isinstance(list[99], str))

#This is very slow and a lot of pull requests, I suggest not running it routinely.
    # def test_get_year(self):
    #     x = b.get_year_data(self.year)
    #     eq_(len(x), 100)
    #     ok_(isinstance(x[14], dict))
    #     ok_(isinstance(x[14]["budget"], int))