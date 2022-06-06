import tkinter as tk
import threading


from uqCoursePlanner.widgets.customWidgets import CourseCanvas, DefaultFrame, Controls, PageNavigation
from uqCoursePlanner.appSettings import Appversion

"""
Change web scrape Thread to something similar to 2310 system with semaphore and locks
Add more pages
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
    colour = "green"

    def __init__(self, master, head):
        # Frame Initialisation
        super(self.__class__, self).__init__(
            master, head, "Course Prerequisites")

        self.widgets[CourseCanvas] = CourseCanvas(
            self, head, bg=self.colour, bd=0, highlightthickness=0, relief=tk.FLAT, confine=True)
        self.widgets[CourseCanvas].pack(
            fill=tk.BOTH, expand=True, side=tk.LEFT)

    def __repr__(self) -> str:
        return f"<MapPage>"


class Settings(DefaultFrame):

    """The Course Info Page
        A tkinter Frame that contains information on a course the user selects

    Parameters:
        parentApp (cls): Parent application for reference.
        controller (tk.Tk()): tkinter Tk class
    """
    colour = "purple"

    def __init__(self, master, head):
        # Frame Initialisation
        super(self.__class__, self).__init__(
            master, head, "Settings")

    def __repr__(self) -> str:
        return f"<Page2>"
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
        self.title(f"UQ Course Planner Assistant: {Appversion}")
        self.geometry(f"{self.width}x{self.height}")
        # self.resizable(0,0)

        # the master container for the program
        container = tk.Frame(self)
        container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.frames = {}
        self.pages = [MapPage, Settings]
        # must be None of type, not instance
        self.currentPage = None

        # create the frames
        for page in self.pages:
            frame = page(container, self)
            self.frames[page] = frame
            frame.grid(row=1, column=1, sticky=tk.NSEW)

        # draw default widgets after all frames have been initialised
        # required as navigation references self.frames items
        self.nav = PageNavigation(container, self)
        self.nav.grid(row=0, column=1, sticky=tk.NSEW)

        self.controls = Controls(container, self)
        self.controls.grid(row=1, column=0, sticky=tk.NSEW)
        for page in self.pages:
            self.frames[page].draw_default_widgets(page.colour)

        # grid configure
        container.grid_rowconfigure(0, weight=0)
        container.grid_rowconfigure(1, weight=1)

        container.grid_columnconfigure(0, weight=0, minsize=200)
        container.grid_columnconfigure(1, weight=1)

        self.update()
        # call the first screen
        self.show_frame(self.pages[0])
        # set the program to refresh the page (and move the components when window size changes)
        # FIXME Change this to a more CPU friendly way so that the refresh is
        # not called event pixel change but until the window is done resizing
        self.bind("<Configure>", lambda event: self.page_refresh())

    def show_frame(self, page) -> None:
        """brings the specified frame to the front"""
        frame = self.frames[page]
        frame.tkraise()
        frame.refresh()
        self.currentPage = page
        # must be last
        self.nav.update()
        self.controls.update()

    def page_refresh(self) -> None:
        self.frames[self.currentPage].refresh()
        self.nav.update()
        self.controls.update()

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

# ʕ •ᴥ•ʔ