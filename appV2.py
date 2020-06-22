from bs4 import BeautifulSoup
from requests import get as rget
from sys import stderr
import re
import tkinter as tk

# TODO TODO TODO TODO
# Mapping component
# completely refactor code and split into multipel files doing the following at the same time
#  -> refactor custom widgets to pass *args and **kwargs
#  -> Frames for collections of elements
#  -> Object to hold all course instances
#  -> class to hold page transistion buttons (courseSelect, courseMap, Settings)
# settings area, default classes per semester, add second check when deleting semesters
# TODO TODO TODO TODO

#########################################
#         MISC GLOBAL VARIABLES         #
#########################################

# Q.O.L variables
line_ending = '\n------------------------\n'

# email for bug reports / requests
email = 'cw.online.acc@outlook.com'

year = '2020'

debug_lines = False

#########################################
#         Custom function groups        #
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

    def __init__(self):
        # nothing here
        pass

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

#########################################
#    Classes for real world concepts    #
#########################################

# a semester class to group course objects
class semester():
    # the semester number
    # DEFAULT = 1 to prevent NULL semesters
    def __init__(self,num=1):
        self.semester_number = num
        # the list holds the course objects
        self.courses = []
    
    # add the specified course object to the list
    def addCourse(self,course):
        self.courses.append(course)

    # remove the last course from the list
    def popCourse(self):
        self.courses.pop()

    # the position in the array that a new course would be if added
    def newCourseLocation(self):
        return len(self.courses)

    def removeCourse(self,code):
        for course in self.courses:
            if course.code == code:
                del self.courses[self.courses.index(course)]
                break


# a course class (one for each item)
class course():
    # the course code for the object and parent_semester object for association
    # DEFAULT: code (user prompt), parent_semester (prevents no association)
    def __init__(self,parent,code="Enter Course Code",parent_semester=semester()):
        self.parent = parent

        # course Code
        self.code = code
        self.old_code = code
        self.firstTest = True
        # attributes
        self.webGet = websiteScraper()
        self.parser = logicParser()

        # parent semester for association and what number it is
        self.parent_semester = parent_semester
        self.semester_number = self.parent_semester.semester_number
        
        # the location in the array that this course sits
        self.location = self.parent_semester.newCourseLocation()
        
        # default code 
        # !!! Not related to actual website codes !!!
        self.status_code = 200
        # lists of attributes to search
        self.prerequisite = []
        self.recommended = []
        self.companion = []
        self.incompatible = []
        self.description = "Course Description Placeholder Text\nLine 2\nLine 3\nLine 4\nLine 5\nLine 6\nLine 7"

        # associated prerequisite data
        self.num_prereq_has = 0
        self.num_prereq_of = 0
           
    def update(self):
        if self.old_code != self.code or self.firstTest:        
            soup_object = self.webGet.fetchHTML(self.code,year)

            # check if course exists by searching for course-notfound tag
            try: 
                soup_object.find(id='course-notfound').string
                self.status_code = 404
            except:
                self.status_code = 200
            if self.status_code == 200:
                # following the syntax of parse(the modified result of (the contents of the tag in the BS4 object))
                # if the tag doesnt exist, an error throws and we just return an empty list indicating no items
                try:
                    self.prerequisite = self.parser.combinationsList(self.webGet.inputModification(soup_object.find(id='course-prerequisite').string,self.code))
                except:
                    self.prerequisite = []
                # try:
                #     self.recommended = self.parser.combinationsList(self.webGet.inputModification(soup_object.find(id='course-recommended-prerequisite').string,self.code))
                # except:
                #     self.recommended = []
                # try:
                #     self.companion = self.parser.combinationsList(self.webGet.inputModification(soup_object.find(id='course-companion').string,self.code))
                # except:
                #     self.companion = []
                # try:
                #     self.incompatible = self.parser.combinationsList(self.webGet.inputModification(soup_object.find(id='course-incompatible').string,self.code))
                # except:
                #     self.incompatible = []
                try:
                    self.description = soup_object.find(id='course-summary').string
                except:
                    self.description = 'No description given'

            self.old_code = self.code
            self.firstTest = False
            # remove remove item from null_semester
            if self.code in [c.code for c in self.parent.null_semester.courses]:
                self.parent.null_semester.removeCourse(self.code)

            status = 0
            for code in set(','.join(self.prerequisite).split(',')):
                if len(code) == 8: # check its a code and not null
                    print(code,end=line_ending)
                    self.num_prereq_has += 1
                    for sem in self.parent.semesters:
                        for item in sem.courses:
                            if item.code == code:
                                item.addPreFor()
                                status = 1
                                if status:
                                    break
                        if status:
                                break
                    # which means item doesn't exist
                    if not status:
                        self.parent.null_semester.addCourse(course(self.parent,code=code,parent_semester=self.parent.null_semester))
                    status = 0

    
    def addPreFor(self):
        self.num_prereq_of += 1

#########################################
#       Tkinter Frames and pages        #
#########################################

# the main application wrapper for the program
class coursePlannerAssistantApp(tk.Tk):
    # standard openning
    def __init__(self, *args,**kwargs):
        # Tk initiatilsation
        tk.Tk.__init__(self, *args,**kwargs)
        
        # Window Managment
        self.title('UQ Course Planner Assistant: Alpha')
        self.geometry('960x540')
        # self.resizable(0,0)
        
        # the master container for the program
        container = tk.Frame(self)
        container.pack(side=tk.TOP,fill=tk.BOTH,expand=True)

        # setting defaults
        container.grid_rowconfigure(0,weight=1)
        container.grid_columnconfigure(0,weight=1)

        self.frames = {}
        # create the frames
        for F in (coursePage,mapCanvas,courseInfoPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0,column=0,sticky=tk.NSEW)
        # call the first screen
        self.show_frame(courseInfoPage)

    # bring the specified frame to the front
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        if cont == courseInfoPage:
            self.frames[cont].optionSelect.update()

# the course selection criteria
class coursePage(tk.Frame):
    # the parent container and tkinter Controller
    def __init__(self,parent,controller):
        # Frame Initialisation
        tk.Frame.__init__(self,parent)
        self.controller = controller
        # tkinter widget array
        self.labels = []

        # courses that are not a part of the user description
        self.null_semester = semester(-1)

        # Default frame label
        label = tk.Label(self,text='Course Select')
        label.grid(row=0,column=1,pady=10,padx=10) # row 0, column 0 reserved for transistion buttons
        # default transistion button
        mapCanvasButton = tk.Button(self,text="Course Map",command=lambda: controller.show_frame(mapCanvas))
        mapCanvasButton.grid(row=0,column=0)
        # default transistion button
        courseInfoPageButton = tk.Button(self,text="Course Info",command=lambda: controller.show_frame(courseInfoPage))
        courseInfoPageButton.grid(row=1,column=0)
        # query the web on items
        queryWebButton = tk.Button(self,text="Send 2 Web",command=lambda: self.updateWidgetCourseObjects())
        queryWebButton.grid(row=0,column=2)

        # status on the web querry
        self.webQueryStatus = webQuerryStatusBar(self)
        self.webQueryStatus.grid(row=0,column=3)

        self.semesters = []
        # creating the first semester
        self.semesters.append(semester(1))
        self.semesters[0].addCourse(course(self,parent_semester=self.semesters[0]))
        
        # initial generation
        self.generateLabels()

    # generate the dynamic UI 
    def generateLabels(self):
        # start by destroying any existing widgets
        for widget in self.labels:
            if widget.ID == "courseLabel" or widget.ID == "semesterLabel":
                widget.destroy()
            elif widget.ID == "courseNumControls" or widget.ID == "semesterNumControls":
                widget.destroyElements()
            else:
                print("unexpected widget in label area") # unexpected item in the bagging area
        # reset list
        self.labels = []

        # redraw all widgets
        for sem in self.semesters:
            # semester label
            self.labels.append(semesterLabel(self,sem.semester_number))
            # course code entrys
            for course_object in sem.courses:
                self.labels.append(courseLabel(self,course_object,sem.semester_number,course_object.location))
            # courseNum controller
            self.labels.append(courseNumControls(self,sem))
        # add the semesterNum controller at the end
        self.labels.append(semesterNumControls(self,len(self.semesters)))
        self.controller.update()

    #  add a semester the the semester list
    def addSemester(self):
        self.semesters.append(semester(len(self.semesters) + 1))
        self.semesters[-1].addCourse(course(self,parent_semester=self.semesters[-1]))

    # remove the last semester from the list
    def popSemester(self):
        self.semesters.pop()

    def updateWidgetCourseObjects(self):
        for widget in self.labels:
            if widget.ID == "courseLabel":
                widget.queryWeb()
        self.webQueryStatus.update("Nothing")

# the main canvas for the course descriptions
class mapCanvas(tk.Frame):
    # the parent container and tkinter Controller
    def __init__(self,parent,controller):
        # Frame initialisation
        tk.Frame.__init__(self,parent)
        # default label
        label = tk.Label(self,text='Course Map')
        label.grid(row=0,column=1)
        # canvas item
        canvas = tk.Canvas(self)
        label.grid(row=1,column=1)
        # default transistion button
        coursePageButton = tk.Button(self,text="Back",command=lambda: controller.show_frame(coursePage))
        coursePageButton.grid(row=1,column=0)

# the main canvas for the course descriptions
class courseInfoPage(tk.Frame):
    # the parent container and tkinter Controller
    def __init__(self,parent,controller):
        # Frame initialisation
        tk.Frame.__init__(self,parent)
        self.controller = controller
        # Default frame label
        label = tk.Label(self,text='Course Information')
        label.grid(row=0,column=1,pady=10,padx=10) # row 0, column 0 reserved for transistion buttons
        # default transistion button
        coursePageButton = tk.Button(self,text="Home",command=lambda: controller.show_frame(coursePage))
        coursePageButton.grid(row=0,column=0)

        self.optionSelect = courseInfoSelect(self)
        self.optionSelect.grid(row=0,column=2)

        tk.Label(self,relief=tk.GROOVE,text="Code",background="#DDDDDD",padx=4,pady=4).grid(row=1,column=1,sticky=tk.N)
        self.title = tk.Label(self,relief=tk.GROOVE,text=self.optionSelect.text.get(),background="#DDDDDD",padx=4,pady=4)
        self.title.grid(row=1,column=1)

        self.description = scrollableRegion(self)
        self.description.grid(row=1,column=2)

        self.prereqMap = courseMap(self)

    def updatePage(self):
        title = self.optionSelect.text.get()
        self.title["text"] = title

        self.description.text['state'] = tk.NORMAL
        self.description.text.delete(1.0,tk.END)
        self.description.text.insert(tk.INSERT, *[co.description for co in self.optionSelect.options if co.code == title])
        self.description.text['state'] = tk.DISABLED
        
#########################################
#       Custom Tkinter Widgets          #
#########################################

# a custom canvas label with certain attributes and values
class semesterLabel(tk.Label):
    # parent widget for location to draw. semester_number for locality
    # DEFAULT=1 to prevent accidental NULL semester locations
    def __init__(self,parent,semester_number=1):
        # label initialisation
        tk.Label.__init__(self,parent)
        # widget ID
        self.ID = "semesterLabel"
        # re-attribution
        self.semester_number = semester_number
        # the semester title
        self.text = "Semester {}".format(self.semester_number)
        # grid location
        self.row = 1
        self.column = self.semester_number 
        # set tkinter widget attribute
        self.config(text=self.text)
        # place in grid
        self.grid(row=self.row,column=self.column,pady=10,padx=10)

# a custom canvas label with certain attributes and values
class courseLabel(tk.Entry):
    # parent widget for location to draw, course for association, semester for locality, row for position
    # DEFAULT: course (prevents no association), semester (prevents NULL semester), row (prevents grid location error)
    def __init__(self,parent, course='None',semester=1,row=2):
        # Entry initialisation
        tk.Entry.__init__(self,parent)
        self.parent = parent
        
        # widget ID
        self.ID = "courseLabel"
        
        # standard values
        self.width = 80  # max number of pixels wide
        self.height = 40  # max number of pixels high 
        # associated course
        self.course = course
        if self.course == 'None':
            self.course = course(self)
        # course code to display
        self.text = tk.StringVar()
        self.text.set(self.course.code)
        # grid location
        self.row = row + 2 # + 2 because row 0 is reserved for buttons and row 1 is reserved for the semester label
        self.column = semester 
        # widget attributes
        self.background_colour = '#d9d9d9' #grey
        self.error_background_colour = '#FFAAAA' # light red
        self.highlighted_background_colour =  '#a0a0a0' # light grey
        textColour = '#000000' #black
        border_type = tk.GROOVE
        justify = tk.CENTER

        # set tkinter attributes
        self.config(textvariable=self.text, relief=border_type, state=tk.DISABLED, justify=justify) # items
        if self.course.status_code == 200:
            self.config(fg=textColour, disabledforeground=textColour, bg=self.background_colour, disabledbackground=self.background_colour) # default colours
        else: 
            self.config(fg=textColour, disabledforeground=textColour, bg=self.error_background_colour, disabledbackground=self.error_background_colour) # error colour
        # bind commands to interactions
        self.bind('<Enter>',lambda event: self.__enter_handler())
        self.bind('<Leave>',lambda event: self.__exit_handler())
        # debug
        self.bind('<Return>',lambda event: self.__print_handler())
        
        # place in grid
        self.grid(row=self.row,column=self.column,pady=10,padx=10)

    # triggers once mouse enters widget  
    def __enter_handler(self):
        # enable the widget and change colour for identification
        self.config(bg=self.highlighted_background_colour,state=tk.NORMAL) #dark grey 
    
    # triggers once mouse leaves widget
    def __exit_handler(self):
        if len(self.get()) == 8:
            self.course.code = self.get().upper()
        else:
            self.course.code = self.get()

        if self.course.status_code == 200:
            self.config(disabledbackground=self.background_colour,state=tk.DISABLED)
        else: 
            self.config(disabledbackground=self.error_background_colour,state=tk.DISABLED) # error colour
    
    def queryWeb(self):
        self.parent.webQueryStatus.update(self.course.code)
        # update corresponding course object
        self.course.update()
        # disable widget and adjust colour accordingly
        if self.course.status_code == 200:
            self.config(disabledbackground=self.background_colour,state=tk.DISABLED)
        else: 
            self.config(disabledbackground=self.error_background_colour,state=tk.DISABLED) # error colour
            self.course.description = 'Invalid Course Code'

    def __print_handler(self):
        print(self.course.code)
        print(self.course.num_prereq_has)
        print(self.course.num_prereq_of)
        print(self.course.prerequisite,end=line_ending)
        for course in self.parent.null_semester.courses:
            print(course.code)
        print(len(self.parent.null_semester.courses),end=line_ending)

# custom widget for adding courses to a semester
class courseNumControls():
    # parent widget for location to draw, semester object for association
    def __init__(self, parent,semester):
        # widget ID
        self.ID = "courseNumControls"

        # re-attribution
        self.semester = semester
        self.parent = parent

        # enable or disable the option to remove a course
        self.downEnable = True
        # meaning there is only 1 element in the list and hence don't remove it
        if self.semester.newCourseLocation() == 1:
            self.downEnable = False

        # grid location
        row = self.semester.newCourseLocation() + 2 # + 2 because row 0 is reserved for buttons and row 1 is reserved for the semester label 
        column = self.semester.semester_number
        
        # widget initialisation
        self.up = tk.Button(parent,text='+',command = lambda: self.controllerAddCourse())
        self.up.grid(row=row,column=column,padx=10)

        if self.downEnable:
            self.down = tk.Button(parent,text='-',command = lambda: self.controllerPopCourse())
            self.down.grid(row=row+1,column=column,padx=10) 

    # command for the add course, calls a method of the associated semester object then updates display
    def controllerAddCourse(self):
        self.semester.addCourse(course(self.parent,parent_semester=self.semester))
        self.parent.generateLabels()

    # command for the remove course, calls a method of the associated semester object then updates display
    def controllerPopCourse(self):      
        self.semester.popCourse()
        self.parent.generateLabels()

    # called when the widget pair needs to be destroyed
    def destroyElements(self):
        self.up.destroy()
        if self.downEnable:
            self.down.destroy()

# custom widget for adding semesters to the coursePage UI
class semesterNumControls():
    # parent widget for location to draw, number of semesters for grid location
    def __init__(self, parent,numOfSemesters):
        # Widget ID
        self.ID = "semesterNumControls"
        # re-attribution
        self.parent = parent

        # enable or disable the option to remove a semester
        self.downEnable = True
        # meaning there is only 1 element in the list and hence don't remove it
        if numOfSemesters == 1:
            self.downEnable = False
        
        # grid location
        row = 2 # 2 because row 0 is reserved for buttons and row 1 is reserved for the semester label 
        column = numOfSemesters + 1

        # widget initialisation
        self.up = tk.Button(parent,text='Add Semester',command = lambda: self.controllerAddSemester())
        self.up.grid(row=row,column=column,padx=10)

        if self.downEnable:
            self.down = tk.Button(parent,text='Remove Semester',command = lambda: self.controllerPopSemester())
            self.down.grid(row=row+1,column=column,padx=10) 

    # command for the add semester, calls a method of the associated parent object then updates display
    def controllerAddSemester(self):
        self.parent.addSemester()
        self.parent.generateLabels()

    # command for the remove semester, calls a method of the associated parent object then updates display
    def controllerPopSemester(self):      
        self.parent.popSemester()
        self.parent.generateLabels()

    # called when the widget pair needs to be destroyed
    def destroyElements(self):
        self.up.destroy()
        if self.downEnable:
            self.down.destroy()

# a custom widget to show which course is being searched
class webQuerryStatusBar(tk.Label):
    
    def __init__(self, parent):
        tk.Label.__init__(self,parent)
        self.ID = 'webQuerryStatusBar'
        self.parent = parent

        self.text = 'Searching for: {}'.format("Nothing")
        self.config(text=self.text)
        

    def update(self,code):
        self.text = 'Searching for: {}'.format(code)
        self.config(text=self.text)
        self.parent.controller.update()

# a custom widget to select which course to show info on
class courseInfoSelect(tk.OptionMenu):
    def __init__(self, parent):
        self.parent = parent
        # by navigating class tree find all options
        self.options = [label.course for label in self.parent.controller.frames[coursePage].labels if label.ID == 'courseLabel']
        # set default value
        self.text = tk.StringVar()
        self.text.set(self.options[0].code)
        self.text.trace("w",lambda *args: self.parent.updatePage())
        # create widget
        tk.OptionMenu.__init__(self,self.parent,self.text,*[op.code for op in self.options])

    def update(self):
        # delete existing options
        self['menu'].delete(0, 'end')
        # find all options
        self.options = [label.course for label in self.parent.controller.frames[coursePage].labels if label.ID == 'courseLabel']
        # set default to first
        self.text.set(self.options[0].code)
        # add all options to menu
        for choice in self.options:
            self['menu'].add_command(label=choice.code, command=tk._setit(self.text, choice.code))

# a custom scrollable region with a title
class scrollableRegion(tk.Frame):
    def __init__(self,parent):
        self.parent = parent
        # frame size (char)
        width=75
        height=5
        tk.Frame.__init__(self,parent,width=width,height=height)
        # title
        self.title = tk.Label(self,relief=tk.GROOVE,text="Description",background="#DDDDDD",padx=4,pady=4)
        self.title.pack(side=tk.TOP)
        # canvas for text
        canvas = tk.Canvas(self,width=width,height=height)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas,width=width,height=height)
        self.scrollable_frame.bind("<Configure>",lambda e: canvas.configure(scrollregion=canvas.bbox("all")) )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.text = tk.Text(self,width=width,height=height,relief=tk.GROOVE,background="#DDDDDD",wrap=tk.WORD)
        self.text.pack()
        self.text.insert(tk.INSERT,"Course Description")
        self.text['state'] = tk.DISABLED

# a custom canvas that shows a map of courses
class courseMap(tk.Canvas):
    def __init__(self,parent):
        self.parent = parent
        pass
#########################################
#               MAIN CALL               #
#########################################

# create app if called directly
# prevent creation on import
if __name__ == "__main__":
    app = coursePlannerAssistantApp()
    # start the app
    app.mainloop()