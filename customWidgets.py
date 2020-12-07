import tkinter as tk
from tkinter.constants import NSEW

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
#               Controls                #
#########################################


class PageNavigation(tk.Frame):
    """A custom tkinter frame that contains the page navigation buttons

    Parameters:
        parentApp (cls): Parent application for reference.
        controller (tk.Tk()): tkinter Tk class
    """
    ID = "PageNavigation"

    def __init__(self, parent, head):
        super(self.__class__, self).__init__(master=parent,
                                             highlightbackground="black", highlightthickness=1, bg="#d4d4d4")
        self.parent = parent
        self.head = head
        self.widgets = {}

        for page in self.head.pages:
            button = tk.Button(master=self, text=self.head.frames[page].pageTitle, font=standardFont,
                               command=lambda destination=page: self.head.show_frame(destination), width=15, height=1, relief=standardRelief)
            button.pack(side=tk.LEFT)
            self.widgets[page] = button

    def update(self) -> None:
        for (key, value) in self.widgets.items():
            if key == self.head.currentPage:
                value.config(relief=tk.FLAT)
            else:
                value.config(relief=standardRelief)

    def __repr__(self):
        location = self.pack_info()()
        return f'<PageNavigation>'

#########################################
#                Frames                 #
#########################################


class DefaultFrame(tk.Frame):
    """The Default frame to use for application pages
    """

    def __init__(self, parent, head, title: str):
        super(DefaultFrame, self).__init__(master=parent)
        self.parent = parent
        self.head = head
        self.pageTitle = title
        self.widgets = {}

    def __repr__(self):
        location = self.pack_info()
        return f'<DefautFrame>'

    def draw_default_widgets(self, colour):

        tk.Frame(master=self, background=colour).pack(
            expand=True, fill=tk.BOTH)
        #########################################
        #                Labels                 #
        #########################################

        #########################################
        #          Mapping Components           #
        #########################################
