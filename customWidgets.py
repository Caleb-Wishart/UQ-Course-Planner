import tkinter as tk

from subjectClasses import *
from appSettings import *
#########################################
#         MISC GLOBAL VARIABLES         #
#########################################

debug_lines = False

standardWidgetColour = '#DDDDDD'
standardRelief = tk.GROOVE
standardFont = ('Helvetica', 10)

#########################################
#                Frames                 #
#########################################
# the default frame to be inherited for pages
class defaultFrame(tk.Frame):
    def __init__(self,parentApp,controller,title):
        tk.Frame.__init__(self,parentApp)
        self.parentApp = parentApp
        self.controller = controller
        self.pageTitle = title
    
    def draw_default_widgets(self):
        # Default frame label
        label = tk.Label(self,text=self.pageTitle,font=standardFont)
        label.grid(row=0,column=1,pady=10,padx=10) # row 0, column 0 reserved for transistion buttons

        # nav buttons
        pageNavigation(self,self.controller).grid(row=0,column=0)

#########################################
#                Labels                 #
#########################################

# a custom canvas label with certain attributes and values
class semesterLabel(tk.Label):
    # parentPage widget for location to draw. semester_number for locality
    # DEFAULT=1 to prevent accidental NULL semester locations
    def __init__(self,parentPage,semester_number=1):
        # label initialisation
        tk.Label.__init__(self,parentPage)
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
        self.config(text=self.text,font=standardFont)
        # place in grid
        self.grid(row=self.row,column=self.column,pady=10,padx=10)

# a custom canvas label with certain attributes and values
class courseLabel(tk.Entry):
    # parentPage widget for location to draw, course for association, semester for locality, row for position
    # DEFAULT: course (prevents no association), semester (prevents NULL semester), row (prevents grid location error)
    def __init__(self,parentPage,controller, course='None',semester=1,row=2):
        # Entry initialisation
        tk.Entry.__init__(self,parentPage,font=standardFont)
        self.parentPage = parentPage
        self.controller = controller
        
        # widget ID
        self.ID = "courseLabel"
        
        # standard values
        self.width = 80  # max number of pixels wide
        self.height = 40  # max number of pixels high 

        # associated course
        self.course = course
        if self.course == 'None':
            self.course = course(self,self.controller)

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
        justify = tk.CENTER

        # set tkinter attributes
        self.config(textvariable=self.text, relief=standardRelief, justify=justify) # items
        self.colourFromStatus()
        
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
        self.colourFromStatus()
    
    def queryWeb(self):
        # send query        
        # update corresponding course object
        self.course.updateCourseInfo(self.parentPage)
        
        # disable widget and adjust colour accordingly
        self.colourFromStatus()

        if self.course.status_code != 200:
            self.course.description = 'Invalid Course Code'

    def colourFromStatus(self):
        if self.course.status_code == 200:
            self.config(disabledbackground=self.background_colour,state=tk.DISABLED)
        else: 
            self.config(disabledbackground=self.error_background_colour,state=tk.DISABLED) # error colour

    def __print_handler(self):
        print(self.course.code)
        print(self.course.prerequisite,end=line_ending)

        # for course in self.parentPage.null_semester.courses:
        #     print(course.code)
        # print(len(self.parentPage.null_semester.courses),end=line_ending)

        for course in self.controller.courseList:
            endPrint(course.code, course.prerequisite)

# a custom scrollable region with a title
class scrollableRegion(tk.Frame):
    def __init__(self,parentPage):
        self.parentPage = parentPage
        # frame size (char)
        width=75
        height=5
        tk.Frame.__init__(self,parentPage,width=width,height=height)
        # title
        self.title = tk.Label(self,relief=standardRelief,text="Description",font=standardFont,background=standardWidgetColour,padx=4,pady=4)
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

        self.text = tk.Text(self,width=width,height=height,relief=standardRelief,background=standardWidgetColour,wrap=tk.WORD,font=standardFont)
        self.text.pack()
        self.text.insert(tk.INSERT,"Course Description")
        self.text['state'] = tk.DISABLED

# a custom widget to select which course to show info on
class courseInfoSelect(tk.OptionMenu):
    def __init__(self, parentPage,controller):
        self.parentPage = parentPage
        self.controller = controller

        self.frames = self.controller.frames
        self.keys = self.controller.pageFuncs

        # by navigating class tree find all options
        self.options = [label.course for label in self.frames[self.keys[0]].labels if label.ID == 'courseLabel']
        
        # set default value
        self.text = tk.StringVar()
        self.text.set(self.options[0].code)
        self.text.trace("w",lambda *args: self.parentPage.updatePage())
        
        # create widget
        tk.OptionMenu.__init__(self,self.parentPage,self.text,*[op.code for op in self.options])

    def updateCourseInfoSelection(self):
        # delete existing options
        self['menu'].delete(0, 'end')
        # find all options
        self.options = [label.course for label in self.frames[self.keys[0]].labels if label.ID == 'courseLabel']
        # set default to first
        self.text.set(self.options[0].code)
        # add all options to menu
        for choice in self.options:
            self['menu'].add_command(label=choice.code, command=tk._setit(self.text, choice.code))

#########################################
#               Controls                #
#########################################
# group of page navigation buttons
class pageNavigation(tk.Frame):
    def __init__(self, parentPage,controller):
        tk.Frame.__init__(self,parentPage)
        self.parentPage = parentPage
        self.controller = controller
        self.ID = "pageNavigation"

        for page in self.controller.pageFuncs:
            button = tk.Button(self,text=controller.frames[page].pageTitle,font=standardFont,command=lambda destination=page: controller.show_frame(destination),width=15,height=1).pack()

# custom widget for adding courses to a semester
class courseNumControls():
    # parentPage widget for location to draw, semester object for association
    def __init__(self, parentPage,controller,semester):
        # widget ID
        self.ID = "courseNumControls"

        # re-attribution
        self.parentPage = parentPage
        self.controller = controller
        self.semester = semester

        # enable or disable the option to remove a course
        self.downEnable = True
        # meaning there is only 1 element in the list and hence don't remove it
        if self.semester.newCourseLocation() == 1:
            self.downEnable = False

        # grid location
        row = self.semester.newCourseLocation() + 2 # + 2 because row 0 is reserved for buttons and row 1 is reserved for the semester label 
        column = self.semester.semester_number
        
        # widget initialisation
        self.up = tk.Button(parentPage,text='+',font=standardFont,command = lambda: self.controllerAddCourse(),width=1)
        self.up.grid(row=row,column=column,padx=10)

        if self.downEnable:
            self.down = tk.Button(parentPage,text='-',font=standardFont,command = lambda: self.controllerPopCourse(),width=1)
            self.down.grid(row=row+1,column=column,padx=10) 

    # command for the add course, calls a method of the associated semester object then updates display
    def controllerAddCourse(self):
        self.semester.addCourse(course(self.parentPage,self.controller,parent_semester=self.semester))
        self.parentPage.generateLabels()

    # command for the remove course, calls a method of the associated semester object then updates display
    def controllerPopCourse(self):      
        self.semester.popCourse()
        self.parentPage.generateLabels()

    # called when the widget pair needs to be destroyed
    def destroyElements(self):
        self.up.destroy()
        if self.downEnable:
            self.down.destroy()

# custom widget for adding semesters to the coursePage UI
class semesterNumControls():
    # parentPage widget for location to draw, number of semesters for grid location
    def __init__(self, parentPage,numOfSemesters):
        # Widget ID
        self.ID = "semesterNumControls"
        # re-attribution
        self.parentPage = parentPage

        # enable or disable the option to remove a semester
        self.downEnable = True
        # meaning there is only 1 element in the list and hence don't remove it
        if numOfSemesters == 1:
            self.downEnable = False
        
        # grid location
        row = 2 # 2 because row 0 is reserved for buttons and row 1 is reserved for the semester label 
        column = numOfSemesters + 1

        # widget initialisation
        self.up = tk.Button(parentPage,text='Add Semester',font=standardFont,command = lambda: self.controllerAddSemester(),width=15)
        self.up.grid(row=row,column=column,padx=10)

        if self.downEnable:
            self.down = tk.Button(parentPage,text='Remove Semester',font=standardFont,command = lambda: self.controllerPopSemester(),width=15)
            self.down.grid(row=row+1,column=column,padx=10) 

    # command for the add semester, calls a method of the associated parentPage object then updates display
    def controllerAddSemester(self):
        self.parentPage.addSemester()
        self.parentPage.generateLabels()

    # command for the remove semester, calls a method of the associated parentPage object then updates display
    def controllerPopSemester(self):      
        self.parentPage.popSemester()
        self.parentPage.generateLabels()

    # called when the widget pair needs to be destroyed
    def destroyElements(self):
        self.up.destroy()
        if self.downEnable:
            self.down.destroy()

# a custom widget to show which course is being searched
class webQuerryStatusBar(tk.Frame):
    
    def __init__(self, parentPage,controller):
        tk.Frame.__init__(self,parentPage)

        self.ID = 'webQuerryStatusBar'
        self.parentPage = parentPage
        self.controller = controller

        # query the web on items
        queryWebButton = tk.Button(self,text="Send 2 Web",font=standardFont,command=lambda: self.parentPage.updateWidgetCourseObjects())
        queryWebButton.pack()

        self.stausText = tk.Label(self)
        self.stausText.pack()

        self.text = 'Awaiting Request'
        self.stausText.config(text=self.text,font=standardFont)
        

    def updateScraping(self,code):
        self.text = 'Searching for: {}'.format(code)
        self.stausText.config(text=self.text,font=standardFont)
        self.controller.update()

    def updateParsing(self,code):
        self.text = 'Parsing data for: {}'.format(code)
        self.stausText.config(text=self.text,font=standardFont)
        self.controller.update()
    
    def updateNormal(self):
        self.text = 'Awaiting Request'
        self.stausText.config(text=self.text,font=standardFont)
        self.controller.update()
