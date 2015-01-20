__author__ = 'Russell Williams'

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import csv

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
    date = parse_release_date(soup)
    movie_info["release year"] = date.strftime("%Y")
    movie_info["release day"] = date.strftime("%j")
    movie_info["domestic gross"] = parse_dom_gross(soup)
    movie_info["worldwide gross"] = parse_world_gross(soup)
    movie_info["budget"] = parse_budget(soup)
    return movie_info


def parse_movie_title(page_soup):
    #Takes a BeautifulSoup object of a movie page, returns the movie's title
    #This counts on the title being the first thing on the page that's size=5 or 6
    title_element = page_soup.find(size=6)
    if not title_element:
        title_element = page_soup.find(size=5)
    title = title_element.string
    #If there's no line break in the title, this works. If not,
    #the title has to be patched together from the string-only content
    #of the title element
    if not title:
        title = " ".join(title_element.strings)
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
    if label:
        label_cell = label.parent.parent
        data_row = label_cell.parent
        world_gross_string = find_money_pattern(data_row)
        return format_money(world_gross_string)
    else:
        return None


def parse_rating(page_soup):
    label = page_soup.find(text=re.compile("MPAA Rating:"))
    data_cell = label.parent
    rating = data_cell.b.string
    return rating


def parse_release_date(page_soup):
    #Finds the release date from a BOM movie page BeautifulSoup object
    #and returns as a datetime object
    label = page_soup.find(text=re.compile("Release Date:"))
    data_cell = label.parent
    for string in data_cell.strings:
        if not re.match("Release Date", string):
            date_string = string
    date_object = datetime.strptime(date_string, "%B %d, %Y")
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


def get_year_page(year):
    #Retrieves the list of the top 100 movies for a given year
    #Returns a Requests object
    url_template = "http://www.boxofficemojo.com/yearly/chart/?page=1&view=releasedate&view2=domestic&yr=%s&p=.htm"
    url = url_template % year
    year_page_request = requests.get(url)
    return year_page_request


def get_id_list(year_page):
    soup = BeautifulSoup(year_page.text)
    label = soup.find(text=re.compile("Rank"))
    top_row = label.parent.parent.parent.parent.parent
    id_list = []
    current = top_row
    for i in range(100):
        current = current.next_sibling
        id = get_id_from_row(current)
        id_list.append(id)
    return id_list

def get_id_from_row(row):
    #Takes a "tr" tree of the yearly movie table and returns the movie's internal id
    link = row.find("a", href=re.compile("movies"))
    id = re.search("id=(.*)\.htm", str(link)).group(1)
    return id


def get_year_data(year):
    ids = get_id_list(get_year_page(year))
    movie_data = []
    print "Retrieving top 100 films from %s" % year
    for id in ids:
        try:
            page = get_movie_page(id)
            movie_data.append(parse_movie_page(page))
        except:
            print "Error encountered for movie id: %s. Skipping." % id
            #This added after the fact that "Elizabeth (1998)" has an extra space at the end of its title
            #that parses differently in unicode vs HTML caused more trouble than it was
            #worth to fix.
    return movie_data


def get_year_range_data(start, stop):
    year_data = []
    for year in range(start, stop+1):
        year_data.append(get_year_data(year))
    return year_data

def output(year_data, filename):
    f = open(filename, "w")
    field_names = ["title",
                   "rating",
                   "release year",
                   "release day",
                   "domestic gross",
                   "worldwide gross",
                   "budget"]
    writer = csv.DictWriter(f, field_names)
    writer.writeheader()
    for year in year_data:
        for movie in year:
            writer.writerow(movie)


if __name__ == "__main__":
    fn = "box_office.csv"
    print "Retrieving data from Box Office Mojo:"
    x = get_year_range_data(1990, 2014)
    skipped_ids = ["elizabeth%A0", "simpleplan%A0"]
    skipped_data = []
    for id in skipped_ids:
        movie_data = parse_movie_page(get_movie_page(id))
        movie_data["title"] = movie_data["title"].encode("ascii", "ignore")
        skipped_data.append(movie_data)
    x.append(skipped_data)
    #Yes, this is kludgy. Deal with it, or figure out the unicode/str/html parsing thing yourself.
    output(x, fn)
    print "Done. Output to %s" % fn