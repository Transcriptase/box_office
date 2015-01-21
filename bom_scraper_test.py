__author__ = 'rwill127'

from nose.tools import *
import bom_scraper as b
import re
from bs4 import BeautifulSoup


class TestPage(object):
    def __init__(self):
        self.test_id = "bringiton"
        #The BOM id for Bring It On, for testing
        #Two reasons: It is old and will not change, unlike my original test movie from last year,
        #and it is awesome
        self.page = b.get_movie_page(self.test_id)
        self.soup = BeautifulSoup(self.page.text)

    def test_getpage(self):
        t_page = b.get_movie_page(self.test_id)
        t_match = re.search("Bring It On", t_page.text)
        #Test that, at least, what comes back contains the words "Bring It On"
        #which is pretty unlikely unless it successfully pulled the page for hat
        #masterpiece.
        ok_(t_match)
        eq_(t_match.group(0), "Bring It On")

    def test_get_title(self):
        t = b.parse_movie_title(self.soup)
        eq_(t, "Bring It On")

    def test_get_multiline_title(self):
        ml_page_id = "catchingfire"
        #The id for The Hunger Games: Catching Fire. The line break made the simple
        #version of title recognition fail.
        ml_page = b.get_movie_page(ml_page_id)
        ml_soup = BeautifulSoup(ml_page.text)
        t = b.parse_movie_title(ml_soup)
        eq_(t, "The Hunger Games: Catching Fire")

    def test_get_dom_gross(self):
        g = b.parse_dom_gross(self.soup)
        eq_(g, 68379000)

    def test_get_budg(self):
        budg = b.parse_budget(self.soup)
        eq_(budg, 28000000)

    def test_get_budg_no_mill(self):
        fp_page_id = "fireproof"
        #ID of a movie with a budget of less than $1m
        fp_soup = BeautifulSoup(b.get_movie_page(fp_page_id).text)
        budg = b.parse_budget(fp_soup)
        eq_(budg, 500000)

    def test_find_money_string_succeed(self):
        label = self.soup.find("td", text="Domestic:")
        data_row = label.parent
        r = b.find_money_pattern(data_row)
        eq_(r, "$68,379,000")

    def test_find_money_string_fail(self):
        row = self.soup.find("tr")
        r = b.find_money_pattern(row)
        eq_(r, None)

    def test_world_gross(self):
        w = b.parse_world_gross(self.soup)
        eq_(w, 90449929)

    def test_rating(self):
        r = b.parse_rating(self.soup)
        eq_(r, "PG-13")

    def test_date_parse(self):
        d = b.parse_release_date(self.soup)
        eq_(d.strftime("%x"), "08/25/00")

    def test_date_nolink(self):
        #original version relied on the release date being inside a link,
        #which is not true of older movies
        sw_id = "starwars5"
        #id for Empire Strikes Back
        sw_soup = BeautifulSoup(b.get_movie_page(sw_id).text)
        d = b.parse_release_date(sw_soup)
        eq_(d.strftime("%x"), "05/21/80")

    def test_page_parse(self):
        m = b.parse_movie_page(self.page)
        eq_(m["title"], "Bring It On")
        eq_(m["rating"], "PG-13")
        eq_(m["release year"], "2000")
        eq_(m["domestic gross"], 68379000)
        eq_(m["worldwide gross"], 90449929)
        eq_(m["budget"], 28000000)

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