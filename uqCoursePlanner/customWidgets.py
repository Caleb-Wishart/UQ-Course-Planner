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
            button = tk.Button(master=self,
                               text=self.head.frames[page].pageTitle,
                               font=standardFont,
                               width=15,
                               height=1,
                               relief=standardRelief,
                               command=lambda destination=page: self.head.show_frame(destination))
            button.pack(side=tk.LEFT)
            self.widgets[page] = button

        self.config(highlightbackground="black",
                    highlightthickness=1,
                    bg="#d4d4d4")

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

        self.config(bg=self.bg,
                    highlightbackground="black",
                    highlightthickness=1)
        debugButton = tk.Button(self,
                                text="Debug",
                                relief=standardRelief,
                                bg="White",
                                activebackground=self.bg,
                                width=10,
                                command=lambda: threading.Thread(target=self.debug).start())
        debugButton.pack(pady=(10, 10), side=tk.BOTTOM)

        searchLabel = tk.Label(self, bg=self.bg, text="Course Search")
        searchLabel.pack()

        self.widgets[CourseSearch] = CourseSearch(self, head)
        self.widgets[CourseSearch].pack(pady=(10, 10))

        searchButton = tk.Button(self,
                                 text="Search",
                                 relief=standardRelief,
                                 bg="White",
                                 activebackground=self.bg,
                                 width=10,
                                 command=lambda: threading.Thread(target=self.search_course).start())
        searchButton.pack(pady=(10, 10))

        selectLabel = tk.Label(self, bg=self.bg, text="Course Select")
        selectLabel.pack()

        self.widgets[SelectBox] = SelectBox(
            self, self.head, relief=standardRelief)
        self.widgets[SelectBox].pack(pady=(10, 10))

    def __repr__(self):
        location = self.pack_info()()
        return f"<Controls>"

    def debug(self) -> None:
        print(Course.courses)

    def search_course(self) -> None:
        courseSearch = self.widgets[CourseSearch]
        code = courseSearch.get().upper()
        if courseSearch.valid:
            self.course = Course.getCourse(code)
            self.head.page_refresh()

    def update(self) -> None:
        for (key, widget) in self.widgets.items():
            try:
                widget.refresh()
            except:
                pass


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
        # self.text.set("Course Code")
        # debug
        self.text.set("csse1001")
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


class SelectBox(tk.Frame):
    def __init__(self, master, head, *args, **kwargs):
        super(self.__class__, self).__init__(
            master=master, *args, **kwargs)
        self.master = master
        self.head = head
        self.widgets = {}

        self.entry_text = tk.StringVar()
        self.entry_text.trace('w', self.on_change)

        self.selected = None
        self.list = []

        entry = tk.Entry(self, relief=standardRelief,
                         textvariable=self.entry_text)
        entry.pack()

        self.widgets[tk.Listbox] = tk.Listbox(
            self, relief=standardRelief, selectmode=tk.SINGLE)
        self.widgets[tk.Listbox].pack()
        self.widgets[tk.Listbox].bind('<Double-Button-1>', self.on_select)

        self.update_list(self.list)

    def on_change(self, *args):
        # print(args)

        value = self.entry_text.get()
        value = value.strip().lower()

        # get data from the list
        if value == '':
            data = self.list
        else:
            data = []
            for item in self.list:
                if value in item.lower():
                    data.append(item)
        # update data in listbox
        self.update_list(data)

    def on_select(self, event):
        listbox = self.widgets[tk.Listbox]
        cur = listbox.curselection()
        selected = listbox.get(cur) if cur != () else None
        print(
            f"Selected: {selected}")
        if selected is not None:
            self.entry_text.set(selected)

    def update_list(self, data):
        listbox = self.widgets[tk.Listbox]
        # delete previous data
        listbox.delete(0, 'end')
        # sorting data
        data = sorted(data, key=str.lower)
        # put new data
        for item in data:
            listbox.insert('end', item)

    def refresh(self):
        self.list = Course.getCourseNames()
        self.update_list(self.list)

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

    def draw_default_widgets(self, colour) -> None:
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

    def create_label(self, x: int, y: int, text: str, tags=()) -> None:
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
