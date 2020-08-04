import tkinter as tk

from customWidgets import *
from scraper import *
from subjectClasses import *

# 1500+ lines and counting (across files)

# TODO todo list
"""
intermediary node lines
refactor instance variables that should be class variables
refactor clusters of code in class methods and make more methods
verbose output decorator
error output decorator
settings area
    [
        default num classes per add Semester
    ]
add second check when deleting semesters
investigate asyncio and threads https://www.youtube.com/watch?v=9zinZmE3Ogk&t=2244s
"""
#########################################
#       Tkinter Frames and pages        #
#########################################


class CoursePage(DefaultFrame):
    """The Course Page

        A tkinter Frame that contains editable labels that the user can use to select courses

    Parameters:
        parentApp (cls): Parent application for reference.
        controller (tk.Tk()): tkinter Tk class
    """

    def __init__(self, parentApp, controller):
        # Frame Initialisation
        super().__init__(parentApp, controller, 'Course Search')

        # tkinter widget array
        self.labels = []

        # Courses that are not a part of the user description
        self.null_semester = Semester(-1)

        # status on the web querry
        self.web_query_status = WebQuerryStatusBar(self, self.controller)
        self.web_query_status.grid(row=0, column=2)

        self.semesters = []
        # creating the first Semester
        self.semesters.append(Semester(1))
        self.semesters[0].add_course(
            Course(self, self.controller, parent_semester=self.semesters[0])
        )

        # initial generation
        self.generate_labels()

    def __repr__(self):
        return f'<CoursePage: Labels: {self.labels}>'

    def generate_labels(self) -> None:
        """Deletes (if existing) and regenerates the custom tkinter labels and course and semester amount controls on the page"""
        # start by destroying any existing widgets
        for widget in self.labels:
            if widget.ID == "CourseLabel" or widget.ID == "SemesterLabel":
                widget.destroy()
            elif widget.ID == "CourseNumControls" or widget.ID == "SemesterNumControls":
                widget.destroy_elements()
            else:
                # unexpected item in the bagging area
                print("unexpected widget in label area")
        # reset list
        self.labels = []

        # redraw all widgets
        for sem in self.semesters:
            # Semester label
            self.labels.append(
                SemesterLabel(self, sem.semester_number)
            )
            # Course code entrys
            for course_object in sem.courses:
                self.labels.append(
                    CourseLabel(self, self.controller, course_object,
                                sem.semester_number, course_object.location)
                )
            # CourseNum controller
            self.labels.append(
                CourseNumControls(self, self.controller, sem)
            )
        # add the SemesterNum controller at the end
        self.labels.append(
            SemesterNumControls(self, len(self.semesters))
        )
        self.controller.update()

    def add_semester(self) -> None:
        """Addes a semester to the list of semesters and fills it with a default course"""
        self.semesters.append(
            Semester(len(self.semesters) + 1)
        )
        self.semesters[-1].add_course(
            Course(self, self.controller, parent_semester=self.semesters[-1])
        )

    def pop_Semester(self) -> None:
        """Removes the last semster from the list"""
        self.semesters.pop()

    def update_widget_course_objects(self) -> None:
        """For each CourseLabel request that the course item be updated"""
        for widget in self.labels:
            if widget.ID == "CourseLabel":
                widget.label_query_web_request()

    def update_master_course_list(self) -> None:
        """If an item is in a null_semester (meaning it isn't in their list) but not in the master list of courses, add it to the master list"""
        for course in self.null_semester.courses:
            if course not in self.controller.course_list:
                self.controller.course_list.append(course)


class CourseMappingPage(DefaultFrame):
    """The Course Mapping Page

        A tkinter Frame that contains a map veiw layout of all the users selected courses

    Parameters:
        parentApp (cls): Parent application for reference.
        controller (tk.Tk()): tkinter Tk class
    """
    # the parent container and tkinter Controller

    def __init__(self, parentApp, controller):
        # Frame Initialisation
        super().__init__(parentApp, controller, 'Course Map')
        # canvas item
        canvas = tk.Canvas(self)
        canvas.grid(row=1, column=1)

    def __repr__(self):
        return '<CourseMappingPage>'


class CourseInfoPage(DefaultFrame):
    """The Course Info Page

        A tkinter Frame that contains information on a course the user selects

    Parameters:
        parentApp (cls): Parent application for reference.
        controller (tk.Tk()): tkinter Tk class
    """

    def __init__(self, parentApp, controller):
        # Frame Initialisation
        super().__init__(parentApp, controller, 'Course Information')

        self.option_select = CourseInfoSelect(self, self.controller)
        self.option_select.grid(row=0, column=2)

        tk.Label(self, relief=tk.GROOVE, text="Code", font=standard_font,
                 background=standard_widget_colour, padx=4, pady=4).grid(row=1, column=1, sticky=tk.N)

        self.title = tk.Label(self, relief=tk.GROOVE, text=self.option_select.text.get(),
                              font=standard_font, background=standard_widget_colour, padx=4, pady=4)
        self.title.grid(row=1, column=1)

        self.description = ScrollableRegion(self)
        self.description.grid(row=1, column=2)

        self.prerequisite_map = CourseMap(self, self.controller)
        self.prerequisite_map.grid(row=2, column=1, columnspan=2, pady=10)

        # status on the web querry
        self.web_query_status = WebQuerryStatusBar(self, self.controller)
        self.web_query_status.grid(row=2, column=0)

    def __repr__(self):
        return f'<CourseInfoPage: Selected item:{self.title["text"]}>'

    def update_page(self) -> None:
        """Updates the contents of the prerequisite_map and description items"""
        code = self.option_select.text.get()
        self.title["text"] = code

        self.description.text['state'] = tk.NORMAL
        self.description.text.delete(1.0, tk.END)
        self.description.text.insert(
            tk.INSERT, *[co.description for co in self.option_select.options if co.code == code])
        self.description.text['state'] = tk.DISABLED

        self.prerequisite_map.updateCanvas(code)

#########################################
#               MAIN APP                #
#########################################


class CoursePlannerAssistantApp(tk.Tk):
    """Application Wrapper

        A class that inherits from tk.Tk() to house tkinter objects
    """
    # standard openning

    def __init__(self, *args, **kwargs):
        # Tk initiatilsation
        tk.Tk.__init__(self, *args, **kwargs)

        # Window Managment
        self.title(f'UQ Course Planner Assistant: {Appversion}')
        self.geometry('960x540')
        # self.resizable(0,0)

        # the master container for the program
        container = tk.Frame(self)
        container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # setting defaults
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.page_classes = (CoursePage, CourseMappingPage, CourseInfoPage)

        self.course_list = []

        # create the frames
        for F in self.page_classes:
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky=tk.NSEW)

        # call the first screen
        self.show_frame(CoursePage)

        # draw default widgets after all frames have been initialised
        # required as navigation references self.frames items
        for page in self.page_classes:
            self.frames[page].draw_default_widgets()

    def show_frame(self, cont) -> None:
        """brings the specified frame to the front"""
        frame = self.frames[cont]
        frame.tkraise()
        # update items
        if cont == CourseInfoPage:
            self.frames[cont].option_select.update_selection_options()

    def tally_prerequisites(self, searchCode: str) -> None:
        """for each course in the master list, if that item is a prerequisite of some other course, add it to its sublist"""
        # clear list
        self.course_list[self.course_list.index(searchCode)].prereq_for.clear()
        # add to list
        verbose_print(
            f'\t{line_segment}\n\tsearching for {searchCode.code} in Course prerequisites', end='\n')
        for course in self.course_list:
            if searchCode.code in set([code for item in course.prerequisite for code in item.split(',')]):
                self.course_list[self.course_list.index(
                    searchCode)].prereq_for.append(course)
                verbose_print(
                    f'\t\tadded {searchCode.code} to {course.code} prerequisite', end='\n')
        verbose_print(
            f'\tFinished searching for {searchCode.code} in Course prerequisites', end=f'\n\t{line_segment}\n')

##############################################  WORKSPACE   ##############################################

#########################################
#          Mapping Components           #
#########################################


class CourseMap(tk.Frame):
    """The CourseMap

        A tkinter frame that holds a tkinter canvas which labels with course names and
        arrows show the chain of prerequisites for courses

    Parameters:
        parentApp (cls): Parent application for reference.
        controller (tk.Tk()): tkinter Tk class
    """

    def __init__(self, parentPage, controller):
        tk.Frame.__init__(self, parentPage)
        self.parentPage = parentPage
        self.controller = controller

        self.canvas_labels = []
        self.canvas_lines = []

        self.tag_text_box = 'textBox'
        self.tag_text_item = 'textItem'
        self.tag_node = 'textNode'
        self.tag_arrow = 'arrow'
        self.tag_arrow_node = 'arrow_node'
        self.tag_column = 'column'
        self.tag_free = 'free'

        self.width = 750
        self.height = 500

        self.box_height = 30
        self.box_width = self.box_height*5/2

        # group title
        self.title = tk.Label(self, relief=standard_relief, text="Prerequisite Map",
                              font=standard_font, background=standard_widget_colour, padx=4, pady=4)
        self.title.pack(side=tk.TOP)
        # canvas
        self.canvas = tk.Canvas(self, bg=standard_widget_colour,
                                relief=standard_relief, width=self.width, height=self.height, highlightthickness=1, highlightbackground="black")
        self.canvas.pack()

    def __repr__(self):
        location = self.grid_info()
        return f'<CourseMapWidget: Located:{self.parentPage} at row: {location["row"]}, column: {location["column"]}>'

    def updateCanvas(self, code: str) -> None:
        """delete all tkinter items on the canvas and regenerate

        Parameters:
            code (str): the code of the course object to use as the basis
        """

        # check valid code
        self.canvas.delete(tk.ALL)
        course = [
            course for course in self.controller.course_list
            if course.code == code]
        # ensure there is one and only one item
        if len(course) == 1:
            course = course[0]

            # find out how many Courses this item is a prerequisite for
            course.map_preprequisite_tree(self.parentPage)
            maplist = course.course_prerequisite_tree
            numCol = len(maplist)
            # labels
            verbose_print('Starting label drawing process', end='\n')
            for colLevel, subgroup in enumerate(maplist, 1):
                for rowLevel, cor in enumerate(subgroup, 1):
                    numRows = len(subgroup)
                    self.draw_Label(cor.code, numCol, numRows,
                                    colLevel, rowLevel)
            verbose_print('Label drawing process finished')
            maplist.reverse()
            # arrows
            verbose_print('Starting arrow drawing process', end='\n')
            searched_items = []
            for colLevel, subgroup in enumerate(maplist, 1):
                for rowLevel, cor in enumerate(subgroup, 1):
                    if cor not in searched_items:
                        searched_items.append(cor)
                        # search for prerequisites
                        self.controller.tally_prerequisites(cor)
                        verbose_print(
                            f'\tcourse {cor.code} is prerequisite for {" and ".join([course.code for course in cor.prereq_for]) if not len(cor.prereq_for) else "nothing"}', end='\n')
                        for item in cor.prereq_for:
                            self.draw_Line(cor.code, item.code)
            del searched_items
            verbose_print('Arrow drawing process finished')
        else:
            error_print("more then one code")
            error_print(course)

    def draw_Label(self, text: str, numCol: int, numRow: int, col: int, row: int) -> None:
        """Draws a custom label on the tkinter canvas at the specified position

        Parameters:
            text (str): the code of the course object to use as the basis
            numCol (int): number of total columns to display
            numRow (int): number of total rows to displa
            col (int): column position
            row (int): row position
        """
        # force round up
        numCol += 0.1
        numRow += 0.1
        # scaling of a box_width
        scale = 0.4

        # remainder 1
        if numCol % 2:
            x = (self.width * 0.5) + -(self.box_width * scale) * \
                (1 + (round(numCol/2) - col) * 4)
        # remainder 0
        else:
            x = (self.width * 0.5) + -(self.box_width * scale) * \
                (3 + (round(numCol/2) - col) * 4)
        # remainder 1
        if numRow % 2:
            y = (self.height * 0.5) + -(self.box_height * scale) * \
                (1 + (round(numRow/2) - row) * 4)
        # remainder 0
        else:
            y = (self.height * 0.5) + -(self.box_height * scale) * \
                (3 + (round(numCol/2) - row) * 4)

        # try find the item with the tag code + textBox
        try:
            item1 = self.canvas.find_withtag(text+self.tag_text_box)[0]
            verbose_print(f'\t{text} already exists, creating node', end='\n')
            x += self.box_width/2
            y += self.box_height/2
            self.canvas.create_rectangle(
                x, y, x, y, fill='black', tags=(text+self.tag_node, self.tag_column+str(col), self.tag_free))
            # debug feature
            self.canvas.create_text(x, y,
                                    text=text, font=standard_font, tags=(text+self.tag_text_item, self.tag_column+str(col)))
        except:
            # else make box and text item

            self.canvas.create_rectangle(
                x, y, x+self.box_width, y+self.box_height, fill='light blue', tags=(text+self.tag_text_box, self.tag_column+str(col)))
            self.canvas.create_text(x+self.box_width/2, y+self.box_height/2,
                                    text=text, font=standard_font, tags=(text+self.tag_text_item, self.tag_column+str(col)))
            verbose_print(
                f'\tdrew {text} at of row {row}, column {col},x: {x},y:{y}, numCol: {numCol}, numRow: {numRow}', end='\n')

    def draw_Line(self, code1: str, code2: str) -> None:
        """Draws a custom arrow on the tkinter canvas at the specified position

        Parameters:
            code1 (str): a course code
            code2 (str): a course code
        """
        # code 1 is the left box

        # check for existing instance
        try:
            item1 = self.canvas.find_withtag(code1+self.tag_arrow+code2)[0]
            if item1 != None:  # i.e. exists
                verbose_print(
                    f'\tArrow from {code1} to {code2} already exists', end='\n')
                return None
        except:
            # item doesn't exist
            pass
        # find the item with the tag code + textBox
        try:
            item1 = self.canvas.find_withtag(code1+self.tag_text_box)[0]
            item2 = self.canvas.find_withtag(code2+self.tag_text_box)[0]
        except:
            # if item does not exist return
            verbose_print(
                f'\t{code1} or {code2} Item does not exist', end='\n')
            return None

        x1, y1, x2, y2 = self.canvas.coords(item1)
        a1, b1, a2, b2 = self.canvas.coords(item2)

        c1 = int([tag for tag in self.canvas.gettags(
            item1) if tag.startswith(self.tag_column)][0][-1])
        c2 = int([tag for tag in self.canvas.gettags(
            item2) if tag.startswith(self.tag_column)][0][-1])
        box_width = x2-x1
        box_height = y2-y1
        # if in neighbouring columns
        if c1 + 1 == c2:
            self.canvas.create_line((x2, y1+box_height/2), (a1, b1+box_height/2),
                                    fill="red", width=2, arrow=tk.LAST, tags=code1+self.tag_arrow+code2)
            verbose_print(f'\tLine drawn from {code1} to {code2}', end='\n')

        else:
            # find all relevent nodes
            nodes = [node for node in self.canvas.find_withtag(
                code1+self.tag_node) if self.tag_free in self.canvas.gettags(node)]
            # for each intermediate node
            for num in range(1, c2-c1):
                # find the column position
                pos = str(c1+num)
                # find all nodes in that column
                column_nodes = self.canvas.find_withtag(
                    self.tag_column+pos)
                # find the intersecting node (column + correct tag)
                intersection_node = [
                    itemID for itemID in nodes if itemID in column_nodes][0]
                # get coords of node (right item)
                n1, m1, n2, m2 = self.canvas.coords(intersection_node)
                self.canvas.dtag(intersection_node, self.tag_free)
                # draw line from left item to right item
                self.canvas.create_line(
                    # + (y2 - y1)/2 in case coming from text, if not its + 0
                    (x2, y1+(y2-y1)/2), (n1, m1+(m2-m1)/2), fill="red", width=2, tags=code1+self.tag_arrow_node+pos)
                # update left item position to current right item
                x1, y1, x2, y2 = n1, m1, n2, m2

            self.canvas.create_line((x2, y1+(y2-y1)/2), (a1, b1+box_height/2),
                                    fill="red", width=2, arrow=tk.LAST, tags=code1+self.tag_arrow+code2)
            verbose_print(
                f'\tLine drawn from {code1} to {code2} through {c2-c1-1} nodes', end='\n')


##############################################  WORKSPACE   ##############################################

#########################################
#               MAIN CALL               #
#########################################

# create app if called directly
# prevent creation on import
if __name__ == "__main__":
    app = CoursePlannerAssistantApp()
    # start the app
    app.mainloop()
