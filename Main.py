from bs4 import BeautifulSoup
from requests import get as rget
from sys import stderr
import re
import tkinter as tk

# Q.O.L variables
line_ending = '\n------------------------\n'

# email for bug reports / requests
email = 'cw.online.acc@outlook.com'
year = '2020'
debug_lines = False

# parses the logic retrieved from the website
# Error with COMS3000

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

        return self.final_options

# gets the html and returns a BS4 object
class websiteScraper():

    def __init__(self):
        # nothing here
        pass

    # Changes the case and manipulates the input to parse
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
        if r.status_code != 200:
            # failsafe
            print('Sorry something went wrong getting the URL, below are variable values for debugging',end=line_ending,file=stderr)
            print('URL:  ',url,end=line_ending,file=stderr)
            print('Status Code:  ',r.status_code,end=line_ending,file=stderr)
            exit()
        soup = BeautifulSoup(r.text,'html.parser')
        return soup

# a course class (one for each item)
class course():
    def __init__(self,code=None,semester=1):
        # attributes
        webGet = websiteScraper()
        parser = logicParser()
        soup_object = webGet.fetchHTML(code,year)
        self.code = code
        self.semester = semester
        # the follow follow the syntax of parse(the modified result of (the contents of the tag in the BS4 object))
        # if the tag doesnt exist, an error throws and we just return an empty list
        try:
            self.prerequisite = parser.prerequisiteList(webGet.inputModification(soup_object.find(id='course-prerequisite').string,self.code))
        except:
            self.prerequisite = []
        try:
            self.recommended = parser.prerequisiteList(webGet.inputModification(soup_object.find(id='course-recommended-prerequisite').string,self.code))
        except:
            self.recommended = []
        try:
            self.companion = parser.prerequisiteList(webGet.inputModification(soup_object.find(id='course-companion').string,self.code))
        except:
            self.companion = []
        try:
            self.incompatible = parser.prerequisiteList(webGet.inputModification(soup_object.find(id='course-incompatible').string,self.code))
        except:
            self.incompatible = []

# a class for node lines or travel paths for the connections
class line_node():
    def __init__(self, xpos=0, ypos=0, sem=0, pos=0):
        # attributes
        self.used = False
        self.xpos = xpos
        self.ypos = ypos
        self.number = (sem,pos)

# a class for label nodes for the path connections
class label_node():
    def __init__(self, xpos = 0,ypos=0,parent_course='',number=0):
        # attributes
        self.used = False
        self.xpos = xpos
        self.ypos = ypos
        self.coords = (xpos,ypos)
        self.parent_course = parent_course
        self.number = number

# a custom canvas label with certain attributes and values
class canvas_label():
    
    def __init__(self, course_item=course(), xpos=0, ypos=0):
        super().__init__()

        self.width = 80  # max number of pixels wide
        self.height = 40  # max number of pixels high

        # standard values
        self.course = course_item
        self.xpos = xpos
        self.ypos = ypos
        self.text = self.course.code

        # path connection nodes
        num_nodes = 6
            # Outbound
        self.nodesOut = [label_node(xpos + self.width, ypos + (self.height -6) / num_nodes * num,self.text,num) for num in range(1,num_nodes+1)]
            # inbound
        self.nodesIn = [label_node(xpos, ypos + (self.height -6) / num_nodes * num,self.text,num) for num in range(1,num_nodes+1)]

        # central node for location
        self.nodeC = (xpos + self.width/2, ypos + self.width/2)

        # actual label
        self.tk_item = self.__custom_label()
        self.tk_item.place(x=self.xpos,y=self.ypos,height=self.height,width=self.width)

    # creates a custom tkinter label widget
    def __custom_label(self):
        background = '#d9d9d9' #grey
        textColour = '#000000' #black
        border_type = 'groove'

        return tk.Label(text=self.text,bg=background,fg=textColour,relief=border_type)
    
# object canvas for display purposes
class objectCanvas(tk.Canvas):
    def __init__(self, parent=None,course_list=[]):
        super().__init__(master=parent, bg='grey')

        # function calls
        self.generate_labels(course_list)
        self.generate_lines()

    # generates labels for each item
    def generate_labels(self,course_list):
        # standard values
        xbase = 50
        ybase = 50
        xmove = 140
        ymove = 100
        num_nodes = 2**4

        # creates the labels and adds them to an array
        self.labels = [canvas_label(    # custom widget class
                course, (xbase + xmove * (course.semester -1)), # sends a course class object, the x position [generated with a base and offset]
                # the y position generated with a base and offset where the offset is determined by getting the index in the list and finding its position in that semester by
                # subtracting the number of courses that come before it e.g if sem 2 pos 2, (assuming 3 course 1st sem) it would interpret as 
                # index = 5, num of courses in previous semster = 3 so multiply offset by 5-3 (2)
                (ybase + ymove * (index - len( [x for x in course_list if x.semester < course.semester] ) ) ) ) 
            for index, course in enumerate(course_list) ] # loop through each item

        # if there is a label generated make corresponding travel nodes
        if len(self.labels) > 0:
            label_width = self.labels[0].width
            label_height = self.labels[0].height

            # create an array holding custom node classes
            self.verticle_nodes = [line_node(
                # x value composed of base and width, then semester offset
                # and finally break the gap between the labels down into the requiired number of positions (based on number of nodes set above)
                xbase + label_width + xmove * (semester) + (xmove - label_width)/(num_nodes+1)*num, 
                0, semester+1, num) # y value, semester and node number for that semester
                for semester in range(len(course_list)) # loop through each item and... 
                for num in range(1,num_nodes + 1)] # add the required number of nodes
            
            # debugging tool to illustrate above nodes as lines [uses the same principles]
            if debug_lines:
                [(lambda x: self.create_line(x,20,x,400))(x.xpos) for x in self.verticle_nodes]

            # create an array holding custom node classes
            self.horizontal_nodes = [line_node(0, # class call and x value
                # y value composed of base and height, then course number offset
                # and finally break the gap between the labels down into the requiired number of positions (based on number of nodes set above)
                (ybase + label_height + ymove * (course_num) + (ymove - label_height)/(num_nodes+1)*num),
                course_num+1, num) # course_number and node number for that semester
                
                # loop through a certain number of times creating nodes based on the largest number of courses in a semester in the plan
                # largest number found by getting the maximum value from a list comprhension that holds the number of times each semester appears in a list
                # generated by another list comprehension that just holds all of the semester in the list of courses and searches for every semester
                for course_num in range(max(
                        [
                            [x.semester for x in course_list].count(search_term)
                                for search_term in range(
                                    max([x.semester for x in course_list])
                                    )
                        ]
                    ))
                for num in range(1,num_nodes+1)] # add the required number of nodes
            
            # debugging tool to illustrate above nodes as lines [uses the same principles as above]
            if debug_lines:
                [(lambda x: self.create_line(20,x,1200,x,fill='light cyan'))(x.ypos) for x in self.horizontal_nodes]

    # draw line from label code to course code if label = a prereq
    # the most nested loops you have ever seen
    def generate_lines(self):
        for major_label in self.labels: # get one label
            if len(major_label.course.prerequisite) > 0: # only proceed if one exists
                for minor_label in self.labels: # get second label
                    if minor_label.course.code in ''.join(major_label.course.prerequisite):  # check if second label is in prerequisites
                        # TODO above will not check for seperate lines
                        for major_node in major_label.nodesIn: # get first node
                            if not major_node.used: # ensure its not used
                                for minor_node in minor_label.nodesOut: # get second node
                                    if not minor_node.used: # check its not used
                                        if minor_label.course.semester + 1 == major_label.course.semester: # if in sequential semesters
                                            if major_node.ypos == minor_node.ypos:  # if they are on the same y-level
                                                self.create_line(minor_node.coords,major_node.coords,fill='red') # create line using direct coordinates 
                                                major_node.used, minor_node.used = True,True # mark as used

                                                # print('No itermediate for {} to {} || used minor {} and major {}'.format(minor_label.text,
                                                #     major_label.text,minor_node.number,major_node.number),end=line_ending,file=stderr)

                                                break # break out of minor_node search when line is created
                                            else: # if they aren't on the same level
                                              # check through verticle nodes backwards to preference closer nodes to lines that have to go to other  locations
                                                for v_node in self.verticle_nodes[::-1]:  
                                                    # check node isn't used and that the node is on the right semester
                                                    if not v_node.used and v_node.number[0] == minor_label.course.semester: 
                                                        self.create_line(minor_node.coords,(v_node.xpos,minor_node.ypos), # create line using coordinates of lines and v-line
                                                            (v_node.xpos,major_node.ypos),major_node.coords,fill='red')
                                                        major_node.used, minor_node.used, v_node.used = True,True,True # mark as used

                                                        # print('Itermediate used for {} to {} || used minor {} and major {} || used v_node {}'.format(minor_label.text,
                                                        #     major_label.text,minor_node.number,major_node.number,v_node.number),end=line_ending,file=stderr)

                                                        break # out of v_node search when line created
                                                break # break out of minor_node search when line is created
                                        else: # if they aren't on sequential semesters
                                            for v_node_minor in self.verticle_nodes[::-1]:
                                                    # check node isn't used and that the node is on the right semester
                                                    if not v_node_minor.used and v_node_minor.number[0] == minor_label.course.semester: 
                                                        for h_node in self.horizontal_nodes:
                                                            if not h_node.used and h_node.ypos > minor_node.ypos: 
                                                                # check through verticle nodes backwards to preference closer nodes to lines that have to go to other locations
                                                                for v_node_major in self.verticle_nodes[::-1]:  # check through verticle nodes
                                                                    # check node isn't used and that the node is on the right semester
                                                                    if not v_node_major.used and v_node_major.number[0] == major_label.course.semester-1: 
                                                                        # create line using coordinates of lines, v-line and h-line 
                                                                        # from label to v-line to h-line to h-line to v-line to label
                                                                        self.create_line(minor_node.coords,(v_node_minor.xpos,minor_node.ypos),
                                                                            (v_node_minor.xpos,h_node.ypos),(v_node_major.xpos,h_node.ypos), 
                                                                            (v_node_major.xpos,major_node.ypos),major_node.coords,fill='red')

                                                                        major_node.used, minor_node.used = True,True # mark as used
                                                                        v_node_minor.used, v_node_major.used, h_node.used = True,True,True # mark as used

                                                                        # print('Itermediate used for {} to {} || used minor {} and major {} || used minor v_node {} || used h_node {} || used major v_node {}'.format(minor_label.text, major_label.text,minor_node.number,major_node.number,v_node_minor.number,h_node.number, v_node_major.number),end=line_ending,file=stderr)  
                                                                        break # out of v_node search when line created 
                                                                break # out of h_node search when line created 
                                                        break # out of v_node search when line created 
                                            break # break out of minor_node search when line is created
                                break # break out of major_node search when line is created or when minor_nodes run out

# creates the application
class Application():

    def __init__(self, master=None):
        # Window Managment
        master.title('UQ Course Map Alpha')
        master.geometry('1200x400')
        master.resizable(0,0)
        
        # creating the canvas
        canvas = objectCanvas(master,course_items)
        canvas.pack(fill=tk.BOTH, expand=True)

# list of courses
course_items = [
    course('CSSE1001',1),

    course('MATH1061',2),

    course('MATH1051',3),
    course('INFS1200',3),
    course('CSSE2010',3),

    course('CSSE2002',4),
    course('INFS2200',4),
    course('CSSE2310',4),

    course('COMP2048',5),
    course('INFS3202',5),
    course('INFS3200',5),
    course('MATH2301',5),

    course('STAT2203',6),
    course('COMP3506',6),
    course('COMS3000',6)
    ]
[print(course_item.prerequisite) for course_item in course_items if course_item.code == 'COMS3000']
# call
if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master=root)
    root.mainloop()

# TODO
# add a loading bar
# TODO issues
# atm, the code will not draw lines for anything other than prerequisites, 
# atm, the code also can not distinguish between different prerequisite lines and so will draw everything
# there is also the chance that the code will run out of nodes to draw with