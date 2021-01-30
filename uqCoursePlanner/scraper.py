
from typing import Any, List, Tuple
from bs4 import BeautifulSoup
from requests import get as rget
import re

from .appSettings import *

#########################################
#       scraper & parsing functions     #
#########################################

# TODO rework this class


class LogicParser():
    """The logic parser

        A cluster of functions used to breakdown a string that contains logical operators
        i.e. AND, OR, commas, parentheses

    Parameters:
        None
    """
    # regex for matching Course codes
    re_course_code = re.compile(r'[A-Z]{4}\d{4}')
    # regex for matching logical operators
    re_non_course_code = re.compile(r'((and)|(or)|(\()|(\)))')

    def __init__(self):
        # the master list that holds the result
        self.final_options = ['']

    def __repr__(self):
        return f'<Logic Parser>'

    def parentheses_breakdown(self, inp: str) -> str:
        """split a string by parentheses

        Parameters:
            inp (str): a string to remove parentheses from
        """
        # find all of the top level parentheses
        re_parentheses = re.findall(r'\((?:[^()]*|\([^()]*\))*\)', inp)
        # replace all of the top level bracket sections with ID's
        for i in range(len(re_parentheses)):
            inp = inp.replace(re_parentheses[i], 'ID'+str(i))

        # split content in required Courses by AND
        component = re.split(' AND ', inp)

        # if the item is an ID replace it with the ID otherwise return the item
        component = [re_parentheses[int(item[-1])][1:-1] if item.find('ID')
                     != -1 else item for item in component]
        return component

    def logical_or_branch(self, work_array: list) -> None:
        """return the two sides of an OR operator and solve the logic, duplicate the existing items in the result as there is a branched path

        Parameters:
            work_array (list): the current work 'stack'
        """
        # tracker for which iteration we are on
        num = 0
        # duplicate final array enough times so each option appears in the right spot
        work_final_options = [
            item for item in self.final_options for _ in range(0, len(work_array))]
        # duplicate the work array items so that they appear on each instance of the final product
        work_array = work_array * len(self.final_options)
        # while there are still option
        while len(work_array) != 0:
            working_item = work_array[0]
            # if the item is just a Course code either set that option to the item or add it to the end if one exists already in that line
            if len(working_item) == 8 and self.re_course_code.search(working_item):
                if len(work_final_options[num]) == 0:
                    work_final_options[num] = working_item
                else:
                    work_final_options[num] += f',{working_item}'

                num += 1
                # remove the item from the process queue
                work_array.remove(working_item)

            # if there is no further parentheses_breakdown item add it to the list (handles exception where the prereq is a not a couse-code unit)
            elif working_item.find(' AND ') == -1 and working_item.find(' OR ') == -1:
                if len(work_final_options[num]) == 0:
                    work_final_options[num] = working_item
                else:
                    work_final_options[num] += f',{working_item}'

                num += 1
                # remove the item from the process queue
                work_array.remove(working_item)

            # if the working item contains a nested AND function but not an OR function try breaking it down,
            # if there are further nested entries throw an error as I am too lazy to try and get it to sort out the rest atm,
            # but if not add both to the end of the list
            elif working_item.find(' AND ') != -1:

                work_array_and = self.parentheses_breakdown(working_item[1:-1])
                for item in work_array_and:
                    if self.re_non_course_code.search(item):
                        print(
                            'Required Courses are too complicated to parse\n for support please contanct the author at: ', email)
                        exit()
                    else:
                        work_final_options[num] += f',{item}'

                num += 1
                # remove item from the process queue
                work_array.remove(working_item)

            else:
                # failsafe
                error_print('Sorry something went wrong in the logical_or_branch, below are variable values for debugging',
                            end=line_ending, file=stderr)
                error_print('Final Options:  ', self.final_options,
                            end=line_ending, file=stderr)
                error_print('OR Work array ended at  ', work_array,
                            end=line_ending, file=stderr)
                exit()
        # set the master list to be the different branches of the process completed above
        self.final_options = [item for item in work_final_options]

    def logical_seperator(self, work_array: list) -> None:
        """ seperate a string by logical operator or add the result to the final options if it is a course code \[A-Z]{4}\d{4}\\

        Parameters:
            work_array (list): the current work 'stack'
        """
        # while there are still options
        while len(work_array) != 0:
            working_item = work_array[0]
            # if the current item matches a Course code add it to the final options list(s)
            if len(working_item) == 8 and self.re_course_code.search(working_item):
                # if this is the first item to be computer make the array that item
                if self.final_options[0] == '':
                    self.final_options = [working_item]
                    # remove item from process queue
                    work_array.remove(working_item)
                else:
                    self.final_options = [
                        item + f',{working_item}' for item in self.final_options]
                    # remove item from process queue
                    work_array.remove(working_item)
            # if the current item contains an OR logical operator send it to the OR function to process
            elif working_item.find(' OR ') != -1:
                component = re.split(' OR ', working_item)
                self.logical_or_branch(component)
                # once processed remove item from queue
                work_array.remove(working_item)
            else:
                # failsafe
                print('Sorry something went wrong in the logical_seperator, below are variable values for debugging',
                      end=line_ending, file=stderr)
                print('Final Options:  ', self.final_options,
                      end=line_ending, file=stderr)
                print('Work array ended at  ', work_array,
                      end=line_ending, file=stderr)
                exit()

    # to call outside of the class
    def prerequisite_combinations_list(self, content: str) -> List[str]:
        """ find the prerequsite combinations available for a given course from website data

        Parameters:
            content (str): content to parse
        """
        # sets the final result list to empty as a reset as __init__ only creates variable and doesn't reset
        self.final_options = ['']
        if content is None:
            return self.final_options
        # starts the process
        self.logical_seperator(self.parentheses_breakdown(content))
        return self.final_options


class WebsiteScraper():
    """The website scraper

        A cluster of functions used to get a HTML document and validate input that goes into a logic parser

    Parameters:
        None
    """

    def __repr__(self):
        return f'<Website Scraper>'

    @staticmethod
    def content_validation(inp: str, code: str) -> str:
        """validate the input to a logic parser, handles ambiguity with logical operators and typos
        Parameters:
            inp (str): input to fix
        """
        # uppercase
        inp = inp.upper()
        inp = re.sub(r',', ' AND', inp)  # replacing the ',' with 'AND'
        inp = re.sub(r'\+', 'AND', inp)  # replacing the '+' with 'AND'
        # add missing spaces for logical operators
        re_malformed_operator_left = re.compile(r'([A-Z]{4}\d{4})(AND|OR)')
        while re_malformed_operator_left.search(inp):
            location = re_malformed_operator_left.search(inp).start()
            inp = inp[:location+1] + ' ' + inp[location+1:]

        re_malformed_operator_right = re.compile(r'(AND|OR)([A-Z]{4}\d{4})')
        while re_malformed_operator_right.search(inp):
            location = re_malformed_operator_right.search(inp).start()
            if inp[location] == 'A':
                inp = inp[:location+3] + ' ' + inp[location+3:]
            else:
                inp = inp[:location+2] + ' ' + inp[location+2:]
        # See COMP2303 example
        re_missing_course_code = re.compile(
            r'([A-Z]{4}\d{4}) (AND|OR) (\d{4})')
        re_only_course_number = re.compile(r'( \d{4})')
        while re_missing_course_code.search(inp):
            location = re_only_course_number.search(inp).start()
            code_location = re_missing_course_code.search(inp).start()
            code = inp[code_location:code_location+4]
            inp = inp[:location+1] + code + inp[location+1:]
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
    def fetch_HTML(course_code: str, search_year: str = year) -> Tuple[Any, int]:
        """ scrape the UQ course page sepcified with the course_code and search_year and return a BS4 object
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
            return soup, r.status_code
        except:
            error_print('Something went wrong while searching the web')
            return None, 404

    @staticmethod
    def get_Field_Contents(soup: Any, field: str, code: str):
        try:
            return WebsiteScraper.content_validation(soup.find(id=field).string, code)
        except:
            return None
