from bs4 import BeautifulSoup
from requests import get as rget
import re

from appSettings import *

#########################################
#       scraper & parsing functions     #
#########################################

# parses the logic retrieved from the website
class logicParser():

    def __init__(self):
        # regex for matching course codes
        self.re_course_code = re.compile(r'[A-Z]{4}\d{4}')
        # regex for matching logical operators
        self.re_non_course_code = re.compile(r'((and)|(or)|(\()|(\)))')
        # the master list that holds the result
        self.final_options = ['']

    # breaks the input down by seperating by the AND function - handles brackets
    # accepts string input ONLY
    def breakdown(self,inp):
        # find all of the top level brackets
        brackets = re.findall(r'\((?:[^()]*|\([^()]*\))*\)',inp)
        # replace all of the top level bracket sections with ID's
        for i in range(len(brackets)):
            inp = inp.replace(brackets[i],'ID'+str(i))

        # split content in required courses by AND
        component = re.split(' AND ', inp)

        # if the item is an ID replace it with the ID otherwise return the item
        component = [brackets[int(item[-1])] [1:-1] if item.find('ID') != -1 else item for item in component]
        return component
        
    # accepts list input ONLY
    def orSolver(self,work_array):
        # tracker for which iteration we are on
        num = 0
        # duplicate final array enough times so each option appears in the right spot
        work_final_options = [item for item in self.final_options for __ in range(0,len(work_array))]
        # duplicate the work array items so that they appear on each instance of the final product
        work_array = work_array * len(self.final_options)
        # while there are still option
        while len(work_array) != 0:
            working_item = work_array[0]
            # if the item is just a course code either set that option to the item or add it to the end if one exists already in that line
            if len(working_item) == 8 and self.re_course_code.search(working_item):
                if len(work_final_options[num]) == 0:
                    work_final_options[num] = working_item
                else:
                    work_final_options[num] += ',{}'.format(working_item)
                
                num+=1
                # remove the item from the process queue
                work_array.remove(working_item)

            # if there is no further breakdown item add it to the list (handles exception where the prereq is a not a couse-code unit)
            elif working_item.find('AND') == -1 and working_item.find('OR') == -1:
                if len(work_final_options[num]) == 0:
                    work_final_options[num] = working_item
                else:
                    work_final_options[num] += ',{}'.format(working_item)
                
                num+=1
                # remove the item from the process queue
                work_array.remove(working_item)

            # if the working item contains a nested AND function but not an OR function try breaking it down, 
            # if there are further nested entries throw an error as I am too lazy to try and get it to sort out the rest atm,
            # but if not add both to the end of the list
            elif working_item.find('AND') != -1:

                work_array_and = self.breakdown(working_item[1:-1])
                for item in work_array_and:
                    if self.re_non_course_code.search(item):
                        print('Required courses are too complicated to parse\n for support please contanct the author at: ',email)
                        exit()
                    else:
                        work_final_options[num] += ',{}'.format(item)
                
                num+=1
                # remove item from the process queue
                work_array.remove(working_item)
            
            else:
                # failsafe
                print('Sorry something went wrong in the orSolver, below are variable values for debugging',end=line_ending,file=stderr)
                print('Final Options:  ',self.final_options,end=line_ending,file=stderr)
                print('OR Work array ended at  ',work_array,end=line_ending,file=stderr)
                exit()
        # set the master list to be the different branches of the process completed above
        self.final_options = [item for item in work_final_options]

    # accepts list input ONLY
    def standardSolver(self,work_array):
        # while there are still options
        while len(work_array) != 0:
            working_item = work_array[0]
            # if the current item matches a course code add it to the final options list(s)
            if len(working_item) == 8 and self.re_course_code.search(working_item):
                # if this is the first item to be computer make the array that item
                if self.final_options[0] == '':
                    self.final_options = [working_item]
                    # remove item from process queue
                    work_array.remove(working_item)
                else:
                    self.final_options = [item + ',{}'.format(working_item) for item in self.final_options]
                    # remove item from process queue
                    work_array.remove(working_item)
            # if the current item contains an OR logical operator send it to the OR function to process
            elif working_item.find('OR') != -1:
                component = re.split(' OR ', working_item)
                self.orSolver(component)
                # once processed remove item from queue
                work_array.remove(working_item)    
            else:
                # failsafe
                print('Sorry something went wrong in the standardSolver, below are variable values for debugging',end=line_ending,file=stderr)
                print('Final Options:  ',self.final_options,end=line_ending,file=stderr)
                print('Work array ended at  ',work_array,end=line_ending,file=stderr)
                exit()

    # to call outside of the class
    def combinationsList(self,content):
        # sets the final result list to empty as a reset as __init__ only creates variable and doesn't reset
        self.final_options = ['']
        # starts the process
        self.standardSolver(self.breakdown(content))
        return self.final_options

# gets the html and returns a BS4 object
class websiteScraper():

    # Changes the case and manipulates the data to parse
    def inputModification(self,inp,code):
        re_malformed_operator_left = re.compile(r'\w(AND|OR)')
        re_malformed_operator_right = re.compile(r'(AND|OR)\w')
        course_code = re.compile(r'[A-Z]{4}\d{4}')

        inp = inp.upper()
        inp = re.sub(r',',' AND',inp) # replacing the ',' with 'AND'
        inp = re.sub(r'\+','AND',inp) # replacing the '+' with 'AND'
        # add missing spaces for logical operators
        while re_malformed_operator_left.search(inp):
            location = re_malformed_operator_left.search(inp).start()
            inp = inp[:location+1] + ' ' + inp[location+1:]

        while re_malformed_operator_right.search(inp):
            location = re_malformed_operator_right.search(inp).start()
            if inp[location] == 'A':
                inp = inp[:location+3] + ' ' + inp[location+3:]
            else:
                inp = inp[:location+2] + ' ' + inp[location+2:]

        edge_case1 = re.compile(r'((?<=(: ))(.*?)(?=;|$))',re.MULTILINE) #See COMS3000 for example
        if 'F OR' in inp:
            srch = edge_case1.findall(inp)
            if course_code.search(inp).group(0) == code:
                inp = srch[0][0]
            else:
                inp = srch[1][0]

        return inp

    # returns a BS4 soup object
    def fetchHTML(self,course_code,search_year=year):
        # URL stoof
        headers = {'User-Agent': 'Mozilla/5.0'}

        # URL development -> base + code and year
        url = 'https://my.uq.edu.au/programs-courses/course.html?course_code={}&year={}'.format(course_code,search_year)

        # get and parse URL
        r = rget(url,headers=headers)
        soup = BeautifulSoup(r.text,'html.parser')
        return soup