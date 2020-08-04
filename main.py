import tkinter as tk

from customWidgets import *
from scraper import *
from subjectClasses import *

# 1500+ lines and counting (across files)

# TODO todo list
"""
refactor instance variables that should be class variables
refactor clusters of code in class methods and make more methods
large mapping area
settings area
    [
        default num classes per add Semester
    ]
select prerequisite layout for courses
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
                error_print("unexpected widget in label area")
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
