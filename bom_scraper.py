__author__ = 'Russell Williams'

import requests
from bs4 import BeautifulSoup
import re

def get_movie_page(movie_id):
    #Returns a requests object of the BOM page for the movie whose BOM ID is movie_id
    #Could use some error catching here
    url_template = "http://www.boxofficemojo.com/movies/?id=%s.htm"
    url = url_template % movie_id
    movie_page_request = requests.get(url)
    return movie_page_request

def parse_movie_page(page_request):
    #Takes a requests objects of a movie page, and returns a dictionary containing the relevant data
    soup = BeautifulSoup(page_request.text)


def parse_movie_title(page_soup):
    #Takes a BeautifulSoup object of a movie page, returns the movie's title
    #This counts on the title being the only thing on the page that's size=6
    #Could stand to have an error check for this.
    title_element = page_soup.find(size=6)
    title = title_element.string
    return title


def parse_dom_gross(page_soup):
    label = page_soup.find("td", text = "Domestic:")
    dom_gross_element = label.find_next_sibling()
    dom_gross = dom_gross_element.find("b").string
    return format_money(dom_gross)


def format_money(money_string):
    #Takes a string representing an amount of money with dollar signs and commas
    #Returns an integer of the number of dollars
    money_string = money_string.replace("$", "")
    money_string = money_string.replace(",", "")
    return int(money_string)


def find_main_info_table(page_soup):
    #Takes a BeautifulSoup object of a movie page and returns the table containing most of the relevant info
    finished = False
    tables = page_soup.find_all("table")
    current = tables[0]
    while not finished:
        if re.match("Domestic Total as of", current) and re.match("MPAA Rating", current):
            main_table = current
            finished = True
        else:
            current = tables.next()
    return main_table
