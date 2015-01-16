__author__ = 'Russell Williams'

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime


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
    movie_info = {}
    movie_info["title"] = parse_movie_title(soup)
    movie_info["rating"] = parse_rating(soup)
    movie_info["release date"] = parse_release_date(soup)
    movie_info["domestic gross"] = parse_dom_gross(soup)
    movie_info["worldwide gross"] = parse_world_gross(soup)
    movie_info["budget"] = parse_budget(soup)
    return movie_info


def parse_movie_title(page_soup):
    #Takes a BeautifulSoup object of a movie page, returns the movie's title
    #This counts on the title being the only thing on the page that's size=6
    #Could stand to have an error check for this.
    title_element = page_soup.find(size=6)
    title = title_element.string
    return title


def parse_dom_gross(page_soup):
    label = page_soup.find("td", text="Domestic:")
    dom_gross_element = label.find_next_sibling()
    dom_gross = dom_gross_element.find("b").string
    return format_money(dom_gross)


def parse_budget(page_soup):
    label = page_soup.find(text=re.compile("Production Budget"))
    data_cell = label.parent
    budget_string = data_cell.b.string
    if budget_string == "N/A":
        return None
    else:
        return words_to_num(budget_string)


def parse_world_gross(page_soup):
    label = page_soup.find(text=re.compile("Worldwide:"))
    label_cell = label.parent.parent
    data_row = label_cell.parent
    world_gross_string = find_money_pattern(data_row)
    return format_money(world_gross_string)


def parse_rating(page_soup):
    label = page_soup.find(text=re.compile("MPAA Rating:"))
    data_cell = label.parent
    rating = data_cell.b.string
    return rating


def parse_release_date(page_soup):
    #Finds the release date from a BOM movie page BeautifulSoup object
    #and returns as a datetime object
    label = page_soup.find(text=re.compile("Release Date:"))
    date = label.parent.a.string
    date_object = datetime.strptime(date, "%B %d, %Y")
    return date_object


def find_money_pattern(soup_result):
    #Takes a BeautifulSoup result object and returns the last string that matches
    #a regex to look for money amounts.
    money_pattern = re.compile("\$([0-9,])*")
    #A regex to find strings that look like money amounts
    success = False
    for string in soup_result.stripped_strings:
        if re.match(money_pattern, string):
            money_string = string
            success = True
    if success:
        return money_string
    else:
        return None


def format_money(money_string):
    #Takes a string representing an amount of money with dollar signs and commas
    #Returns an integer of the number of dollars
    money_string = money_string.replace("$", "")
    money_string = money_string.replace(",", "")
    return int(money_string)


def words_to_num(money_string):
    #Translates a string expressing an amount of money in the format
    #"$<number><word>" where <word> is "millions" to an integer
    #This is pretty fragile right now, especially if there are reported budgets less than 1m.
    #This is the format BMO uses for budget numbers
    base_match = re.search("([0-9]+)", money_string)
    base = int(base_match.group(0))
    multiplier = 1000000
    return base*multiplier
