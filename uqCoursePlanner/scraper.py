
from typing import Any, Tuple
from bs4 import BeautifulSoup
from requests import get as rget
import re
import logging

#########################################
#            Scraper Class              #
#########################################

class Scraper():
    """The website scraper

        A cluster of functions used to get a HTML document and validate input
        that goes into a logic parser

    Parameters:
        None
    """

    # year to look for in URL
    year = "2021"

    def __repr__(self):
        return f'<Website Scraper>'

    @staticmethod
    def content_filter(inp: str, code: str) -> str:
        """validate the input to a logic parser, handles ambiguity with
            logical operators and typos

            Transformations:
            ',' -> AND
            '+' -> AND
            COURSEAND COURSE -> COURSE AND COURSE
            COURSE ANDCOURSE -> COURSE AND COURSE
            COURSEOR COURSE -> COURSE OR COURSE
            COURSE ORCOURSE -> COURSE OR COURSE

            COURSE AND NUM -> COURSE AND COURSE

            FOR COURSE:
                COURSES
            FOR COURSE:   --> COURSES
                COURSES

        Parameters:
            inp (str): input to fix\
            code (str): the course code
        """
        # uppercase
        inp = inp.upper()
        inp = re.sub(r',', ' AND', inp)  # replacing the ',' with 'AND'
        inp = re.sub(r'\+', 'AND', inp)  # replacing the '+' with 'AND'
        # add missing spaces for logical operators
        re_malformed_operator_left = re.compile(r'([A-Z]{4}\d{4})(AND|OR)')
        while re_malformed_operator_left.search(inp):
            location = re_malformed_operator_left.search(inp).start()
            inp = inp[:location + 1] + ' ' + inp[location + 1:]

        re_malformed_operator_right = re.compile(r'(AND|OR)([A-Z]{4}\d{4})')
        while re_malformed_operator_right.search(inp):
            location = re_malformed_operator_right.search(inp).start()
            # modify AND / OR
            if inp[location] == 'A':
                inp = inp[:location + 3] + ' ' + inp[location + 3:]
            else:
                inp = inp[:location + 2] + ' ' + inp[location + 2:]

        # See COMP2303 example
        re_missing_course_code = re.compile(
            r'([A-Z]{4}\d{4}) (AND|OR) (\d{4})')
        re_only_course_number = re.compile(r'( \d{4})')
        while re_missing_course_code.search(inp):
            location = re_only_course_number.search(inp).start()
            code_location = re_missing_course_code.search(inp).start()
            code = inp[code_location:code_location + 4]
            inp = inp[:location + 1] + code + inp[location + 1:]

        # See COMS3000 for example
        re_for_code = re.compile(r'((?<=(: ))(.*?)(?=;|$))', re.MULTILINE)
        re_course_code = re.compile(r'[A-Z]{4}\d{4}(?!.)')
        if 'FOR' in inp:
            srch = re_for_code.findall(inp)
            if re_course_code.search(inp).group(0) == code:
                inp = srch[0][0]
            else:
                inp = srch[1][0]

        return inp

    @staticmethod
    def fetch_HTML(course_code: str, search_year: str = year) -> Tuple[BeautifulSoup, int]:
        """ scrape the UQ course page sepcified with the course_code and
            search_year and return a BS4 object
        Parameters:
            course_code (str): search code
            year (str): search year

        Returns:
            BS4 Object
        """
        # URL stoof
        headers = {'User-Agent': 'Mozilla/5.0'}

        # URL development -> base + code and year
        url = f'https://my.uq.edu.au/programs-courses/course.html?course_code={course_code}&year={search_year}'

        # get and parse URL
        try:
            r = rget(url, headers=headers)
            soup = BeautifulSoup(r.text, 'html.parser')
            logging.info(f'Successfully scraped {url}: {r.status_code}')
            return soup, r.status_code
        except Exception as e:
            logging.error('Something went wrong while searching the web: ' + e)
            return None, 404

    @staticmethod
    def get_Field_Contents(soup: BeautifulSoup, field: str, code: str) -> str | None:
        """
        Get the modified contents of a specific HTML feild

        :param soup: The BS4 HTML soup object
        :param field: The HTML tag to search for
        :param code: The course code we are looking for
        :return: A corrected Logical statement for the courses prerequisities
        """
        try:
            return Scraper.content_filter(soup.find(id=field).string, code)
        except:
            return None

# ʕ •ᴥ•ʔ