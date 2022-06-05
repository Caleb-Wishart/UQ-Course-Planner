from bs4 import BeautifulSoup
from requests import get as rget
from sys import stderr
import re
import tkinter as tk

# TODO
# make everything run from an array that holds course codes and return a dictionary with the information in arrays under each key of a course code

# 5 wide grid of points that the lines can connect to in columns between course codes


#
#       -----------  : : : : :
#       | Course  |  : : : : : 
#       -----------  : : : : :
#                    : : : : :
#       -----------  : : : : :
#       | Course  |  : : : : :
#       -----------  : : : : :
#

### Variables ###
# Q.O.L variables
line_ending = '\n------------------------\n'

# email for bug reports / requests
email = 'PLACEHOLDER'

### Important Variables
#Input
# course_codes = ['CSSE1001','CSSE2010']
years = 1

# testing variable
m_course_codes = ['AAAA{}'.format('0'*(4-len(str(item)))+str(item)) for item in range(years*8)]
m_course_codes[0] = 'CSSE1001'
m_course_codes[5] = 'CSSE2010'

year = '2020'
m_results = {}
### CLASSES ###

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
                    work_final_options[num] += ', {}'.format(working_item)
                
                num+=1
                # remove the item from the process queue
                work_array.remove(working_item)

            # if there is no further breakdown item add it to the list (handles exception where the prereq is a not a couse-code unit)
            elif working_item.find('AND') == -1 and working_item.find('OR') == -1:
                if len(work_final_options[num]) == 0:
                    work_final_options[num] = working_item
                else:
                    work_final_options[num] += ', {}'.format(working_item)
                
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
                        work_final_options[num] += ', {}'.format(item)
                
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
                    self.final_options = [item + ', {}'.format(working_item) for item in self.final_options]
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
    def prerequisiteList(self,content):
        # sets the final result list to empty as a reset as __init__ only creates variable and doesn't reset
        self.final_options = ['']
        # starts the process
        self.standardSolver(self.breakdown(content))

        # debugging tools
        self.final_options = ['('+re.sub(r',',' and',inp)+')' for inp in self.final_options]
        if len(self.final_options) != 1:
            self.final_options = ' or '.join(self.final_options)
        else: 
            self.final_options = self.final_options[0]

        return self.final_options

class websiteScraper():

    def __init__(self):
        # Class definitions
        self.parser = logicParser()

    # Changes the case and manipulates the input to parse
    def inputModification(self,inp):
        re_malformed_and = re.compile(r'\w(AND|OR)')

        inp = inp.upper()
        inp = re.sub(r',',' AND',inp) # replacing the ',' with 'AND'
        inp = re.sub(r'\+','AND',inp) # replacing the '+' with 'AND'
        # add missign spaces for logical operators
        while re_malformed_and.search(inp):
            location = re_malformed_and.search(inp).start()
            inp = inp[:location+1] + ' ' + inp[location+1:]
        return inp

    def fetchHTML(self,course_code,year):
        # URL stoof
        headers = {'User-Agent': 'Mozilla/5.0'}

        # URL development -> base + code and year
        url = 'https://my.uq.edu.au/programs-courses/course.html?course_code={}&year={}'.format(course_code,year)

        # get and parse URL
        r = rget(url,headers=headers)
        if r.status_code != 200:
            # failsafe
            print('Sorry something went wrong getting the URL, below are variable values for debugging',end=line_ending,file=stderr)
            print('URL:  ',url,end=line_ending,file=stderr)
            print('Status Code:  ',r.status_code,end=line_ending,file=stderr)
            exit()
        soup = BeautifulSoup(r.text,'html.parser')
        return soup

    def scrapedData(self,course_code,year):
        html = self.fetchHTML(course_code,year)
        returnDict = {}
        
        # test case for debugging (uncomment to activate)
        # requried_content = inputModification('AAAA0000 aNd (BBBb1111 oR (CCcC3333, dDDD4444)) + (EEEE5555 or FffF6666)')

        # make sure course exists
        try:
            html.find(id='course-level').string
        except:
            returnDict.update({'Course Exists: ':False})
            returnDict.update({'Course Entered: ':course_code})
            return returnDict
            
        ### Getting all of the data ###

        # get the prerequisite courses by id 
        try:
            returnDict.update({'prerequisite':self.parser.prerequisiteList(self.inputModification(html.find(id='course-prerequisite').string))})
        except:
            returnDict.update({'prerequisite':None})

        # get recommended courses if they exist
        try:
            returnDict.update({'recommended':self.parser.prerequisiteList(self.inputModification(html.find(id='course-recommended-prerequisite').string))})
        except:
            returnDict.update({'recommended':None})

        # get companion courses if they exist
        try:
            returnDict.update({'companion':self.parser.prerequisiteList(self.inputModification(html.find(id='course-companion').string))})
        except:
            returnDict.update({'companion':None})

        # get companion courses if they exist
        try:
            returnDict.update({'incompatible':self.parser.prerequisiteList(self.inputModification(html.find(id='course-incompatible').string))})
        except:
            returnDict.update({'incompatible':None})

        return returnDict

class interface(tk.Frame):
    def __init__(self, master = None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.button_dictionary = {}

    def myButton(self,text):
        background = '#d9d9d9' #grey
        textColour = '#000000' #black
        highlight  = '#999999999' #dark grey
        border_type = 'groove'
        height = 2
        width = 12
        state = 'normal'
        return tk.Label(text=text,bg=background,fg=textColour,relief=border_type,height=height,width=width,state=state)

    def displayCourses(self,course_list):
        for item in range(len(course_list)):
            course_code = course_list[item]
            self.button_dictionary.update({course_code:self.myButton(course_code)})
            self.button_dictionary[course_code].place(x=( (item) // 4) * 140 + 25,y=( (item) % 4) * 75 + 25)

root = tk.Tk()
graphics = interface(master=root)

graphics.master.title('UQ Course Mapping')
graphics.master.geometry(str(years*280)+'x325')
graphics.master.resizable(0,0)

### Class definition
scrape = websiteScraper()

# output

# # website scraping
# for item in m_course_codes:
#     m_results.update({item:scrape.scrapedData(item,year)})

# # print debugging
# for key in results.keys():
#     print(line_ending[:-2])
#     print(key,end=line_ending)
#     for content in m_results[key].keys():
#         print('    ',content,':',m_results[key][content])
# print(m_results)
m_results = {'CSSE1001': {'prerequisite': None, 'recommended': None, 'companion': None, 'incompatible': '(COMP1502) or (CSSE7030)'}, 'CSSE2010': {'prerequisite': '(CSSE1001)', 'recommended': None, 'companion': None, 'incompatible': '(COMP1300) or (COMP2303) or (COMP2302) or (CSSE1000) or (CSSE7035) or (CSSE7201) or (ELEC2002)'}}
graphics.displayCourses(m_course_codes)

if __name__ == "__main__":
  # Start Program
  graphics.mainloop()