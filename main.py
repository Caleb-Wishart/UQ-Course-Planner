import tkinter as tk

from customWidgets import *
from scraper import *
from subjectClasses import *

# 1000+ lines and counting (across files)

# TODO TODO TODO TODO
# intermediary node lines
# VS Code syntax highlighitng 
# verbose output
# error output
# settings area, default num classes per add semester, add second check when deleting semesters
# refactor clusters of code in class methods and make more methods
# TODO TODO TODO TODO

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

    def updateMasterCourseList(self):
        for course in self.null_semester.courses:
            if course not in self.controller.courseList:
                self.controller.courseList.append(course)

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

        # status on the web querry
        self.webQueryStatus = webQuerryStatusBar(self,self.controller)
        self.webQueryStatus.grid(row=2,column=0)

    def updatePage(self):
        code = self.optionSelect.text.get()
        self.title["text"] = code

        self.description.text['state'] = tk.NORMAL
        self.description.text.delete(1.0,tk.END)
        self.description.text.insert(tk.INSERT, *[co.description for co in self.optionSelect.options if co.code == code])
        self.description.text['state'] = tk.DISABLED

        self.prereqMap.updateCanvas(code)

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
        self.show_frame(coursePage)

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
            self.frames[cont].optionSelect.updateCourseInfoSelection()

    def tallyPrerequisites(self,searchCode):
        # clear list
        self.courseList[self.courseList.index(searchCode)].prereq_for.clear()
        # add to list
        print(f'searching for {searchCode.code} in course prerequisites')
        for course in self.courseList:
            if searchCode.code in set([code for item in course.prerequisite for code in item.split(',')]):
                self.courseList[self.courseList.index(searchCode)].prereq_for.append(course)
                print(f'added {searchCode.code} to {course.code} prerequisite')
        
##############################################  WORKSPACE   ##############################################

#########################################
#          Mapping Components           #
#########################################
# a custom canvas that shows a map of courses
class courseMap(tk.Frame):

    def __init__(self,parentPage,controller):
        tk.Frame.__init__(self,parentPage)
        self.parentPage = parentPage
        self.controller = controller

        self.canvasLabels = []
        self.canvasLines = []

        self.tagTextBox = 'textBox'
        self.tagTextItem = 'textItem'
        self.tagNode = 'textNode'
        self.tagArrow = 'arrow'

        self.width = 500
        self.height = 200

        self.boxHeight = 30
        self.boxWidth = self.boxHeight*5/2

        # group title
        self.title = tk.Label(self,relief=standardRelief,text="Prerequisite Map",font=standardFont,background=standardWidgetColour,padx=4,pady=4)
        self.title.pack(side=tk.TOP)
        # canvas
        self.canvas = tk.Canvas(self,bg=standardWidgetColour,relief=standardRelief,width=self.width,height=self.height)
        self.canvas.pack()

    def updateCanvas(self,code):
        # check valid code
        self.canvas.delete(tk.ALL)
        course = [course for course in self.controller.courseList if course.code == code]
        # ensure there is one and only one item
        if len(course) == 1:
            course = course[0]

            # find out how many courses this item is a prerequisite for
            course.prerequisiteMapping(self.parentPage)
            maplist = course.prerequisiteMap
            maplist.reverse()
            numCol = len(maplist)
            # labels
            for colLevel, subgroup in enumerate(maplist,1):
                for rowLevel, cor in enumerate(subgroup,1):
                    numRows = len(subgroup)
                    self.draw_Label(cor.code,numCol,numRows,colLevel,rowLevel)
            maplist.reverse()
            # arrows
            for colLevel, subgroup in enumerate(maplist,1):
                for rowLevel, cor in enumerate(subgroup,1):
                    # search for prerequisites
                    self.controller.tallyPrerequisites(cor)
                    endPrint(f'corse {cor.code} is prereq for {cor.prereq_for}')
                    for item in cor.prereq_for:
                        self.draw_Line(cor.code,item.code)

    # draw label with pos being top left of box
    def draw_Label(self,text,numCol,numRow,col,row):
        if numCol == 1:
            x = (self.width) * 0.5 - self.boxWidth/2 
        else:
            x = (self.width) * 0.5 + self.boxWidth * 1.5 * (-numCol +1 +col)  - self.boxWidth/2
        if numRow == 1:
            y = (self.height) * 0.5 - self.boxHeight/2
        else:
            y = (self.height) * 0.5 + self.boxHeight * 1.5 * (-numRow +1 +row) - self.boxHeight/2
        # tryu find the item with the tag code + textBox
        try:
            item1 = self.canvas.find_withtag(text+self.tagTextBox)[0]
            verbosePrint(f'{text} already exists, creating node')
            x += self.boxWidth/2
            y += self.boxHeight/2
            self.canvas.create_rectangle(x,y,x,y,fill='black',tags=text+self.tagNode)
        except:
            # else make box and text item

                self.canvas.create_rectangle(x,y,x+self.boxWidth,y+self.boxHeight,fill='light blue',tags=text+self.tagTextBox) 
                self.canvas.create_text(x+self.boxWidth/2,y+self.boxHeight/2,text=text,font=standardFont,tags=text+self.tagTextItem)
                verbosePrint(f'drew {text} at of row {row}, column {col},x: {x},y:{y}, numCol: {numCol}, numRow: {numRow}')
    
    # draw a line from point a to b
    # code 1 is the left box
    def draw_Line(self,code1,code2):
        # check for existing instance
        try:
            item1 = self.canvas.find_withtag(code1+self.tagArrow+code2)[0]
            if item1 != None: # i.e. exists
                verbosePrint(f'Arrow from {code1} to {code2} already exists')
                return None
        except: 
            # item doesn't exist
            pass
        # find the item with the tag code + textBox
        try:
            item1 = self.canvas.find_withtag(code1+self.tagTextBox)[0]
            item2 = self.canvas.find_withtag(code2+self.tagTextBox)[0]
        except:
        # if item does not exist return
            verbosePrint(f'{code1} or {code2} Item does not exist')
            return None

        x1,y1,x2,y2 = self.canvas.coords(item1)
        a1,b1,a2,b2 = self.canvas.coords(item2)

        boxwidth = x2-x1
        boxheight = y2-y1

        self.canvas.create_line((x2,y1+boxheight/2),(a1,b1+boxheight/2),fill="red",width=2, arrow=tk.LAST,tags=code1+self.tagArrow+code2)
        verbosePrint(f'Line drawn from {code1} to {code2}')
           
        
##############################################  WORKSPACE   ##############################################

#########################################
#               MAIN CALL               #
#########################################

# create app if called directly
# prevent creation on import
if __name__ == "__main__":
    app = coursePlannerAssistantApp()
    # start the app
    app.mainloop()
