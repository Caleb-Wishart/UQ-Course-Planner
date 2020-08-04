import tkinter as tk

from subjectClasses import *
from appSettings import *
#########################################
#         MISC GLOBAL VARIABLES         #
#########################################

debug_lines = False

standard_widget_colour = '#DDDDDD'
standard_relief = tk.GROOVE
standard_font = ('Helvetica', 10)

#########################################
#                Frames                 #
#########################################


class DefaultFrame(tk.Frame):
    """The Default frame to use for application pages

    Parameters:
        parentApp (cls): Parent application for reference.
        controller (tk.Tk()): tkinter Tk class
        title (str): page title for reference
    """

    def __init__(self, parentApp, controller, title: str):
        tk.Frame.__init__(self, parentApp)
        self.parentApp = parentApp
        self.controller = controller
        self.page_title = title

    def __repr__(self):
        location = self.grid_info()
        return f'<DefautFrame: Located:{self.parentPage} at row: {location["row"]}, column: {location["column"]}>'

    def draw_default_widgets(self) -> None:
        """Places the default widgets on the page"""
        # Default frame label
        label = tk.Label(self, text=self.page_title, font=standard_font)
        # row 0, column 0 reserved for transistion buttons
        label.grid(row=0, column=1, pady=10, padx=10)

        # nav buttons
        PageNavigation(self, self.controller).grid(row=0, column=0)

#########################################
#                Labels                 #
#########################################


class SemesterLabel(tk.Label):
    """A custom tkinter Label to show a semester label

    Parameters:
        parentApp (cls): Parent application for reference.
        controller (tk.Tk()): tkinter Tk class
        semester_number (int): the semester number to display
            DEFAULT VALUE: 1, prevents null semesters
    """

    def __init__(self, parentPage, semester_number: int = 1):
        # label initialisation
        tk.Label.__init__(self, parentPage)
        # widget ID
        self.ID = "SemesterLabel"
        # re-attribution
        self.semester_number = semester_number
        # the Semester title
        self.text = f"Semester {self.semester_number}"
        # grid location
        self.row = 1
        self.column = self.semester_number
        # set tkinter widget attribute
        self.config(text=self.text, font=standard_font)
        # place in grid
        self.grid(row=self.row, column=self.column, pady=10, padx=10)

    def __repr__(self):
        location = self.grid_info()
        return f'<SemesterLabel: Located:{self.parentPage} at row: {location["row"]}, column: {location["column"]}: {self.text}>'


class CourseLabel(tk.Entry):
    """A custom tkinter Label to show a course label
        :: Editable

    Parameters:
        parentApp (cls): Parent application for reference.
        controller (tk.Tk()): tkinter Tk class
        course (str): the course code
            DEFAULT VALUE: None, prevents a label without an associated course
        semester (int): the semester number for attribution on the tkinter page
            DEFAULT VALUE: 1, ensure it is drawn to a valid location
        row (int): the row in the semester to be drawn
            DEFAULT VALUE: 2, ensure that labels don't overlap on other elements (row 0 = page label, row 1 = semester label)
    """

    def __init__(self, parentPage, controller, course='None', Semester: int = 1, row: int = 2):
        # Entry initialisation
        tk.Entry.__init__(self, parentPage, font=standard_font)
        self.parentPage = parentPage
        self.controller = controller

        # widget ID
        self.ID = "CourseLabel"

        # standard values
        self.width = 80  # max number of pixels wide
        self.height = 40  # max number of pixels high

        # associated Course
        self.course = course
        if self.course == 'None':
            self.course = Course(self, self.controller)

        # Course code to display
        self.text = tk.StringVar()
        self.text.set(self.course.code)

        # grid location
        # + 2 because row 0 is reserved for buttons and row 1 is reserved for the Semester label
        self.row = row + 2
        self.column = Semester

        # widget attributes
        self.background_colour = '#d9d9d9'  # grey
        self.error_background_colour = '#FFAAAA'  # light red
        self.highlighted_background_colour = '#a0a0a0'  # light grey
        textColour = '#000000'  # black
        justify = tk.CENTER

        # set tkinter attributes
        self.config(textvariable=self.text, relief=standard_relief,
                    justify=justify)  # items
        self.label_colour()

        # bind commands to interactions
        self.bind('<Enter>', lambda event: self.__enter_handler())
        self.bind('<Leave>', lambda event: self.__exit_handler())

        # debug
        self.bind('<Return>', lambda event: self.__print_handler())

        # place in grid
        self.grid(row=self.row, column=self.column, pady=10, padx=10)

    def __repr__(self):
        location = self.grid_info()
        return f'<CourseLabel: Located:{self.parentPage} at row: {location["row"]}, column: {location["column"]}: Contains: {self.course}>'

    def __enter_handler(self) -> None:
        """Triggers on mouse enter widget, change background colour and allow edits"""
        # enable the widget and change colour for identification
        self.config(bg=self.highlighted_background_colour,
                    state=tk.NORMAL)  # dark grey

    def __exit_handler(self) -> None:
        """Triggers on mouse exit widget, change background colour and disable edits"""
        if len(self.get()) == 8:
            self.course.code = self.get().upper()
            self.text.set(self.course.code)
        else:
            self.course.code = self.get()
        self.label_colour()

    def __print_handler(self) -> None:
        """Triggers on enter being pressed in widget, prints debug information"""
        # for course in self.parentPage.null_semester.courses:
        #     print(course)
        # print(len(self.parentPage.null_semester.courses),end=line_ending)

        for course in self.controller.course_list:
            end_print(course)
            end_print(course.course_prerequisite_tree)

    def label_query_web_request(self) -> None:
        """Request that the label course object has the information updated"""
        # check if item exists or not
        if self.course.code not in [course.code for course in self.controller.course_list]:
            # update corresponding Course object
            self.course.update_course_info(self.parentPage)
            verbose_print(
                f"Requested an update for course code {self.course.code}")
        else:
            self.course = [
                course for course in self.controller.course_list if course.code == self.course.code][0]
            verbose_print(
                f"Updated {self.course.code} to an existing item")

        # disable widget and adjust colour accordingly
        self.label_colour()

        if self.course.status_code != 200:
            self.course.description = 'Invalid Course Code'

    def label_colour(self) -> None:
        """Set the label colour based on the course status_code"""
        if self.course.status_code == 200:
            self.config(disabledbackground=self.background_colour,
                        state=tk.DISABLED)
        else:
            self.config(disabledbackground=self.error_background_colour,
                        state=tk.DISABLED)  # error colour


class ScrollableRegion(tk.Frame):
    """A custom tkinter textbox that allows scrolling

    Parameters:
        parentApp (cls): Parent application for reference.
    """

    def __init__(self, parentPage):
        self.parentPage = parentPage
        # frame size (char)
        width = 75
        height = 5
        tk.Frame.__init__(self, parentPage, width=width, height=height)
        # title
        self.title = tk.Label(self, relief=standard_relief, text="Description",
                              font=standard_font, background=standard_widget_colour, padx=4, pady=4)
        self.title.pack(side=tk.TOP)
        # canvas for text
        canvas = tk.Canvas(self, width=width, height=height)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, width=width, height=height)
        self.scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.text = tk.Text(self, width=width, height=height, relief=standard_relief,
                            background=standard_widget_colour, wrap=tk.WORD, font=standard_font)
        self.text.pack()
        self.text.insert(tk.INSERT, "Course Description")
        self.text['state'] = tk.DISABLED

    def __repr__(self):
        location = self.grid_info()
        return f'<ScrollableRegion: Located:{self.parentPage} at row: {location["row"]}, column: {location["column"]}>'


class CourseInfoSelect(tk.OptionMenu):
    """A custom tkinter option menu that allws the user to select which course they want to see information on
        :: Editable

    Parameters:
        parentApp (cls): Parent application for reference.
        controller (tk.Tk()): tkinter Tk class
    """

    def __init__(self, parentPage, controller):
        self.parentPage = parentPage
        self.controller = controller

        self.frames = self.controller.frames
        self.keys = self.controller.page_classes

        # by navigating class tree find all options
        self.options = [label.course for label in self.frames[self.keys[0]
                                                              ].labels if label.ID == 'CourseLabel']

        # set default value
        self.text = tk.StringVar()
        self.text.set(self.options[0].code)
        self.text.trace("w", lambda *args: self.parentPage.update_page())

        # create widget
        tk.OptionMenu.__init__(self, self.parentPage,
                               self.text, *[op.code for op in self.options])

    def __repr__(self):
        location = self.grid_info()
        return f'<CourseInfoSelection: Located:{self.parentPage} at row: {location["row"]}, column: {location["column"]}: Current Selection: {self.text.get()}>'

    def update_selection_options(self) -> None:
        """Changes the selectable options in the optionMenu based on courses that are in labels"""
        # delete existing options
        self['menu'].delete(0, 'end')
        # find all options
        self.options = [label.course for label in self.frames[self.keys[0]
                                                              ].labels if label.ID == 'CourseLabel']
        # set default to first
        self.text.set(self.options[0].code)
        # add all options to menu
        for choice in self.options:
            self['menu'].add_command(
                label=choice.code, command=tk._setit(self.text, choice.code))

#########################################
#               Controls                #
#########################################


class PageNavigation(tk.Frame):
    """A custom tkinter frame that contains the page navigation buttons

    Parameters:
        parentApp (cls): Parent application for reference.
        controller (tk.Tk()): tkinter Tk class
    """

    def __init__(self, parentPage, controller):
        tk.Frame.__init__(self, parentPage)
        self.parentPage = parentPage
        self.controller = controller
        self.ID = "PageNavigation"

        for page in self.controller.page_classes:
            button = tk.Button(self, text=controller.frames[page].page_title, font=standard_font,
                               command=lambda destination=page: controller.show_frame(destination), width=15, height=1).pack()

    def __repr__(self):
        location = self.grid_info()
        return f'<PageNavigation: Located:{self.parentPage} at row: {location["row"]}, column: {location["column"]}>'


class CourseNumControls():
    """A custom tkinter wdiget group that allows the user to add or remove courses from a semester display

    Parameters:
        parentApp (cls): Parent application for reference.
        controller (tk.Tk()): tkinter Tk class
        semester (Semester()): the semester to draw the contents of
    """

    def __init__(self, parentPage, controller, semester):
        # widget ID
        self.ID = "CourseNumControls"

        # re-attribution
        self.parentPage = parentPage
        self.controller = controller
        self.semester = semester

        # enable or disable the option to remove a Course
        self.remove_course_label_check = True
        # meaning there is only 1 element in the list and hence don't remove it
        if self.semester.new_course_location == 1:
            self.remove_course_label_check = False

        # grid location
        # + 2 because row 0 is reserved for buttons and row 1 is reserved for the Semester label
        row = self.semester.new_course_location + 2
        column = self.semester.semester_number

        # widget initialisation
        self.up = tk.Button(parentPage, text='+', font=standard_font,
                            command=lambda: self.add_course_controller(), width=1)
        self.up.grid(row=row, column=column, padx=10)

        if self.remove_course_label_check:
            self.down = tk.Button(parentPage, text='-', font=standard_font,
                                  command=lambda: self.pop_course_controller(), width=1)
            self.down.grid(row=row+1, column=column, padx=10)

    def __repr__(self):
        location = self.grid_info()
        return f'<CourseNumControls: Located:{self.parentPage} at row: {location["row"]}, column: {location["column"]}>'

    def add_course_controller(self) -> None:
        """Adds a course to the associated semester"""
        self.semester.add_course(
            Course(self.parentPage, self.controller, parent_semester=self.semester))
        self.parentPage.generate_labels()

    def pop_course_controller(self) -> None:
        """Removes a course from the associated semester"""
        self.semester.pop_course()
        self.parentPage.generate_labels()

    def destroy_elements(self) -> None:
        """Destroys all tkinter elements associated with the group"""
        self.up.destroy()
        if self.remove_course_label_check:
            self.down.destroy()


class SemesterNumControls():
    """A custom tkinter wdiget group that allows the user to add or remove semesters from the course selection page

    Parameters:
        parentApp (cls): Parent application for reference.
        controller (tk.Tk()): tkinter Tk class
        number_of_semesters (int): the number of semesters currently shown
    """

    def __init__(self, parentPage, number_of_semesters):
        # Widget ID
        self.ID = "SemesterNumControls"
        # re-attribution
        self.parentPage = parentPage

        # enable or disable the option to remove a Semester
        self.remove_course_label_check = True
        # meaning there is only 1 element in the list and hence don't remove it
        if number_of_semesters == 1:
            self.remove_course_label_check = False

        # grid location
        row = 2  # 2 because row 0 is reserved for buttons and row 1 is reserved for the Semester label
        column = number_of_semesters + 1

        # widget initialisation
        self.new_semester = tk.Button(parentPage, text='Add Semester', font=standard_font,
                                      command=lambda: self.add_semester_controller(), width=15)
        self.new_semester.grid(row=row, column=column, padx=10)

        if self.remove_course_label_check:
            self.remove_semester = tk.Button(parentPage, text='Remove Semester', font=standard_font,
                                             command=lambda: self.pop_semester_controller(), width=15)
            self.remove_semester.grid(row=row+1, column=column, padx=10)

    def __repr__(self):
        location = self.grid_info()
        return f'<SemesterNumControls: Located:{self.parentPage} at row: {location["row"]}, column: {location["column"]}>'

    def add_semester_controller(self) -> None:
        """Adds a semester to the associated page"""
        self.parentPage.add_semester()
        self.parentPage.generate_labels()

    def pop_semester_controller(self) -> None:
        """Adds a semester to the associated page"""
        self.parentPage.pop_Semester()
        self.parentPage.generate_labels()

    def destroy_elements(self) -> None:
        """Destroys all tkinter elements associated with the group"""
        self.new_semester.destroy()
        if self.remove_course_label_check:
            self.remove_semester.destroy()


class WebQuerryStatusBar(tk.Frame):
    """A custom tkinter wdiget group that shows the user the status of a web query process and allows them to request an update

    Parameters:
        parentApp (cls): Parent application for reference.
        controller (tk.Tk()): tkinter Tk class
    """

    def __init__(self, parentPage, controller):
        tk.Frame.__init__(self, parentPage)

        self.ID = 'WebQuerryStatusBar'
        self.parentPage = parentPage
        self.controller = controller

        # query the web on items
        web_query_request_button = tk.Button(self, text="Send 2 Web", font=standard_font,
                                             command=lambda: self.parentPage.update_widget_course_objects())
        web_query_request_button.pack()

        self.staus_text = tk.Label(self)
        self.staus_text.pack()

        self.text = 'Awaiting Request'
        self.staus_text.config(text=self.text, font=standard_font)

    def __repr__(self):
        location = self.grid_info()
        return f'<WebQueryStatusBar: Located:{self.parentPage} at row: {location["row"]}, column: {location["column"]}>'

    def update_scraping_message(self, code: str) -> None:
        """Updates the WebQuerryStatusBar widget message"""
        self.text = f'Searching for: {code}'
        self.staus_text.config(text=self.text, font=standard_font)
        self.controller.update()

    def update_parsing_message(self, code: str) -> None:
        """Updates the WebQuerryStatusBar widget message"""
        self.text = f'Parsing data for: {code}'
        self.staus_text.config(text=self.text, font=standard_font)
        self.controller.update()

    def update_waiting_message(self):
        """Updates the WebQuerryStatusBar widget message"""
        self.text = 'Awaiting Request'
        self.staus_text.config(text=self.text, font=standard_font)
        self.controller.update()
