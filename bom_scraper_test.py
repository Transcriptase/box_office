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