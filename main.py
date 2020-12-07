import tkinter as tk
from tkinter.constants import BOTH

from customWidgets import *
from scraper import *
from subjectClasses import *
from appSettings import *

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


class MapPage(DefaultFrame):

    """The Course Info Page
        A tkinter Frame that contains information on a course the user selects

    Parameters:
        parentApp (cls): Parent application for reference.
        controller (tk.Tk()): tkinter Tk class
    """
    colour = 'green'

    def __init__(self, parent, head):
        # Frame Initialisation
        super(self.__class__, self).__init__(
            parent, head, 'Course Information')

    def __repr__(self) -> str:
        return f'<MapPage>'


class Page2(DefaultFrame):

    """The Course Info Page
        A tkinter Frame that contains information on a course the user selects

    Parameters:
        parentApp (cls): Parent application for reference.
        controller (tk.Tk()): tkinter Tk class
    """
    colour = 'purple'

    def __init__(self, parent, head):
        # Frame Initialisation
        super(self.__class__, self).__init__(
            parent, head, 'Page 2')

    def __repr__(self) -> str:
        return f'<Page2>'
#########################################
#               MAIN APP                #
#########################################


class Application(tk.Tk):
    """Application Wrapper

        A class that inherits from tk.Tk() to house tkinter objects
    """
    # standard openning

    width = 900
    height = 600

    def __init__(self, *args, **kwargs):
        # Tk initiatilsation
        tk.Tk.__init__(self, *args, **kwargs)

        # Window Managment
        self.title(f'UQ Course Planner Assistant: {Appversion}')
        self.geometry(f'{self.width}x{self.height}')
        # self.resizable(0,0)

        # the master container for the program
        container = tk.Frame(self)
        container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # setting defaults
        # container.grid_rowconfigure(0, weight=1)
        # container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.pages = [MapPage, Page2]
        self.currentPage = None

        self.course_list = []

        # create the frames
        for page in self.pages:
            frame = page(container, self)
            self.frames[page] = frame
            frame.grid(row=1, column=1, sticky=tk.NSEW)

        # draw default widgets after all frames have been initialised
        # required as navigation references self.frames items
        self.nav = PageNavigation(container, self)
        self.nav.grid(row=0, column=1, sticky=tk.NSEW)

        self.controls = tk.Frame(
            master=container, bg="#b8b8b8", highlightbackground="black", highlightthickness=1)
        self.controls.grid(row=1, column=0, sticky=tk.NSEW)
        for page in self.pages:
            self.frames[page].draw_default_widgets(page.colour)

        # call the first screen
        self.show_frame(self.pages[0])

        # grid configure
        container.grid_rowconfigure(0, weight=0)
        container.grid_rowconfigure(1, weight=1)

        container.grid_columnconfigure(0, weight=0, minsize=200)
        container.grid_columnconfigure(1, weight=1)

    def show_frame(self, page) -> None:
        """brings the specified frame to the front"""
        frame = self.frames[page]
        frame.tkraise()
        self.currentPage = page
        self.nav.update()

##############################################  WORKSPACE   ##############################################

##############################################  WORKSPACE   ##############################################

#########################################
#               MAIN CALL               #
#########################################


def main():
    app = Application()
    # start the app
    app.mainloop()


# create app if called directly
# prevent creation on import
if __name__ == "__main__":
    main()
