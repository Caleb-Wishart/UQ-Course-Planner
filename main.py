from sys import stderr
import tkinter as tk

from scraper import *
from subjectClasses import *
from customWidgets import *

# TODO TODO TODO TODO
# Mapping component
# settings area, default num classes per add semester, add second check when deleting semesters
# TODO TODO TODO TODO

#########################################
#         MISC GLOBAL VARIABLES         #
#########################################

# Q.O.L variables
line_ending = '\n------------------------\n'

#########################################
#       Tkinter Frames and pages        #
#########################################

# the course selection criteria
class coursePage(defaultFrame):
    # the parent container and tkinter Controller
    def __init__(self,parentApp,controller):
        # Frame Initialisation
        super().__init__(parentApp,controller,'Course Search')
        
        # tkinter widget array
        self.labels = []

        # courses that are not a part of the user description
        self.null_semester = semester(-1)

        # status on the web querry
        self.webQueryStatus = webQuerryStatusBar(self,self.controller)
        self.webQueryStatus.grid(row=0,column=2)

        self.semesters = []
        # creating the first semester
        self.semesters.append(semester(1))
        self.semesters[0].addCourse(course(self,self.controller,parent_semester=self.semesters[0]))
        
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
                self.labels.append(courseLabel(self,self.controller,course_object,sem.semester_number,course_object.location))
            # courseNum controller
            self.labels.append(courseNumControls(self,self.controller,sem))
        # add the semesterNum controller at the end
        self.labels.append(semesterNumControls(self,len(self.semesters)))
        self.controller.update()

    #  add a semester the the semester list
    def addSemester(self):
        self.semesters.append(semester(len(self.semesters) + 1))
        self.semesters[-1].addCourse(course(self,self.controller,parent_semester=self.semesters[-1]))

    # remove the last semester from the list
    def popSemester(self):
        self.semesters.pop()

    def updateWidgetCourseObjects(self):
        for widget in self.labels:
            if widget.ID == "courseLabel":
                widget.queryWeb()
        self.webQueryStatus.update("Nothing")

# the main canvas for the course mapping
class courseMappingPage(defaultFrame):
    # the parent container and tkinter Controller
    def __init__(self,parentApp,controller):
        # Frame Initialisation
        super().__init__(parentApp,controller,'Course Map')
        # canvas item
        canvas = tk.Canvas(self)
        canvas.grid(row=1,column=1)

# the main frame for the course descriptions
class courseInfoPage(defaultFrame):
    # the parent container and tkinter Controller
    def __init__(self,parentApp,controller):
        # Frame Initialisation
        super().__init__(parentApp,controller,'Course Information')
        
        self.optionSelect = courseInfoSelect(self,self.controller)
        self.optionSelect.grid(row=0,column=2)

        tk.Label(self,relief=tk.GROOVE,text="Code",font=standardFont,background=standardWidgetColour,padx=4,pady=4).grid(row=1,column=1,sticky=tk.N)
        
        self.title = tk.Label(self,relief=tk.GROOVE,text=self.optionSelect.text.get(),font=standardFont,background=standardWidgetColour,padx=4,pady=4)
        self.title.grid(row=1,column=1)

        self.description = scrollableRegion(self)
        self.description.grid(row=1,column=2)

        self.prereqMap = courseMap(self,self.controller)
        self.prereqMap.grid(row=2,column=2,pady=10)

    def updatePage(self):
        title = self.optionSelect.text.get()
        self.title["text"] = title

        self.description.text['state'] = tk.NORMAL
        self.description.text.delete(1.0,tk.END)
        self.description.text.insert(tk.INSERT, *[co.description for co in self.optionSelect.options if co.code == title])
        self.description.text['state'] = tk.DISABLED

#########################################
#               MAIN APP                #
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
        self.pageFuncs = (coursePage,courseMappingPage,courseInfoPage)

        self.courseList = []

        # create the frames
        for F in self.pageFuncs:
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0,column=0,sticky=tk.NSEW)
        
        # call the first screen
        self.show_frame(courseInfoPage)

        # draw default widgets after all frames have been initialised
        # required as navigation references self.frames items
        for page in self.pageFuncs:
            self.frames[page].draw_default_widgets()

    # bring the specified frame to the front
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        # update items
        if cont == courseInfoPage:
            self.frames[cont].optionSelect.update()


#########################################
#               MAIN CALL               #
#########################################

# create app if called directly
# prevent creation on import
if __name__ == "__main__":
    app = coursePlannerAssistantApp()
    # start the app
    app.mainloop()