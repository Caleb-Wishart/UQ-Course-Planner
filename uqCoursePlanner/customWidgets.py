import re
import tkinter as tk
import threading

from .appSettings import end_print
from .subjectClasses import Course

#########################################
#         MISC GLOBAL VARIABLES         #
#########################################

debug_lines = False

standardWidgetColour = "#DDDDDD"
standardRelief = tk.GROOVE
standardFont = ("Helvetica", 10)


#########################################
#               Controls                #
#########################################

class PageNavigation(tk.Frame):
    """A custom tkinter frame that contains the page navigation buttons

    Parameters:
        parentApp (cls): Parent application for reference.
        controller (tk.Tk()): tkinter Tk class
    """

    def __init__(self, master, head, *args, **kwargs):
        super(self.__class__, self).__init__(master=master,
                                             *args, **kwargs)
        self.master = master
        self.head = head
        self.widgets = {}

        for page in self.head.pages:
            button = tk.Button(master=self, text=self.head.frames[page].pageTitle, font=standardFont,
                               command=lambda destination=page: self.head.show_frame(destination), width=15, height=1, relief=standardRelief)
            button.pack(side=tk.LEFT)
            self.widgets[page] = button

        self.config(highlightbackground="black",
                    highlightthickness=1, bg="#d4d4d4")

    def update(self) -> None:
        for (key, value) in self.widgets.items():
            if key == self.head.currentPage:
                value.config(relief=tk.FLAT)
            else:
                value.config(relief=standardRelief)

    def __repr__(self):
        location = self.pack_info()()
        return f"<PageNavigation>"


class Controls(tk.Frame):
    bg = "#b8b8b8"

    def __init__(self, master, head, *args, **kwargs):
        super(self.__class__, self).__init__(master=master,
                                             *args, **kwargs)
        self.master = master
        self.head = head
        self.widgets = {}

        self.course = None

        self.config(bg=self.bg, highlightbackground="black",
                    highlightthickness=1)

        self.widgets[tk.Label] = tk.Label(
            self, bg=self.bg, text="Course Search")
        self.widgets[tk.Label].pack()

        self.widgets[CourseSearch] = CourseSearch(self, head)
        self.widgets[CourseSearch].pack()

        self.widgets[tk.Button] = tk.Button(
            self, text="Search", relief=standardRelief, bg="White", activebackground=self.bg, width=10, command=lambda: threading.Thread(target=self.search_course).start())
        self.widgets[tk.Button].pack(pady=(10, 10))

        self.widgets["Debug"] = tk.Button(
            self, text="Debug", relief=standardRelief, bg="White", activebackground=self.bg, width=10, command=lambda: self.debug())
        self.widgets["Debug"].pack(pady=(10, 10))

    def __repr__(self):
        location = self.pack_info()()
        return f"<Controls>"

    def debug(self):
        with self.head.coursesLock:
            print(self.head.courses)

    def search_course(self):
        courseSearch = self.widgets[CourseSearch]
        code = courseSearch.get()
        if courseSearch.valid:
            with self.head.coursesLock:
                try:
                    self.course = self.head.courses[code]
                except KeyError as e:
                    self.head.courses[code] = Course(code)
                    self.course = self.head.courses[code]
                self.head.page_refresh()


class CourseSearch(tk.Entry):
    width = 80  # max number of pixels wide
    height = 40  # max number of pixels high

    backgroundColour = '#d9d9d9'  # grey
    errorBackgroundColour = '#FFAAAA'  # light red
    highlightedBackgroundColour = '#a0a0a0'  # light grey
    textColour = '#000000'  # black
    justify = tk.CENTER
    CourseCodeReXp = re.compile(r'[A-z]{4}\d{4}(?!.)')

    def __init__(self, master, head, *args, **kwargs):
        super(self.__class__, self).__init__(
            master=master, *args, **kwargs)
        self.master = master
        self.head = head

        self.text = tk.StringVar()
        self.text.set("Course Code")
        self.valid = False

        self.config(textvariable=self.text, relief=standardRelief,
                    justify=self.justify, font=standardFont)
        # bind commands to interactions
        self.bind('<KeyRelease>', lambda event: self.key_handler(event))
        # debug
        self.bind('<Return>', lambda event: self.print_handler(event))

    def __repr__(self) -> str:
        return f"Course Search Entry"

    def key_handler(self, event) -> None:
        """Triggers on mouse exit widget, change background colour"""
        if self.CourseCodeReXp.match(self.get()):
            self.config(bg=self.backgroundColour)
            self.valid = True
        else:
            self.config(bg=self.errorBackgroundColour)
            self.valid = False

    def print_handler(self, event) -> None:
        """Triggers on enter being pressed in widget, prints debug information"""
        end_print(self.get(), len(self.get()))

#########################################
#                Frames                 #
#########################################


class DefaultFrame(tk.Frame):
    """The Default frame to use for application pages
    """

    def __init__(self, master, head, title: str, *args, **kwargs):
        super(DefaultFrame, self).__init__(master=master, *args, **kwargs)
        self.master = master
        self.head = head
        self.pageTitle = title
        self.widgets = {}

    def __repr__(self):
        location = self.pack_info()
        return f"<DefautFrame>"

    def draw_default_widgets(self, colour):
        tk.Frame(master=self, background=colour).pack(
            expand=True, fill=tk.BOTH)

    def refresh(self):
        for (key, widget) in self.widgets.items():
            try:
                widget.refresh()
            except:
                pass


class CourseCanvas(tk.Canvas):
    """A custom tkinter canvas"""

    def __init__(self, master, head, *args, **kwargs):
        super(CourseCanvas, self).__init__(master=master, *args, **kwargs)
        self.master = master
        self.head = head

    def create_label(self, x: int, y: int, text: str, tags=()):
        fill = "light blue"
        height = 30
        width = height*5/2
        tags = tuple(
            [tag+"_label" for tag in tags])
        self.create_rectangle(x, y, x+width, y+height,
                              fill=fill, tags=tags)
        self.create_text(x+width/2, y+height/2, text=text,
                         font=standardFont, tags=tags)

    def refresh(self):
        pass


#########################################
#                Labels                 #
#########################################

#########################################
#          Mapping Components           #
#########################################
