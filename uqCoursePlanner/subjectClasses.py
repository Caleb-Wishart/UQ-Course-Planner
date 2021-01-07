
from collections import deque
from .scraper import LogicParser, WebsiteScraper
from .appSettings import year, default_description
#########################################
#    Classes for real world concepts    #
#########################################


class Course():
    """The Course class

        A simulation of a realworld course, contains information on the course
        i.e. code, description, prerequisites
        & a cluster of functions used to update the information and find a course object

    Parameters:
        parentApp (cls): Parent application for reference.
        controller (tk.Tk()): tkinter Tk class
        code (str): the course code used to scrape the web and for reference
            DEFAULT VALUE: for something to show on a label
        parent_semester (semester()): used for reference
            DEFAULT VALUE: assigns a semester
    """

    def __init__(self, code: str = None):
        # Course Code
        self.code = code
        # attributes

        (soup, self.status_code) = WebsiteScraper.fetch_HTML(self.code, year)

        # lists of attributes to search
        search_fields = ["course-prerequisite", "course-summary"]
        fields = {key: WebsiteScraper.get_Field_Contents(
            soup, key, self.code) for key in search_fields}

        self.recommended = []
        self.companion = []
        self.incompatible = []

        self.prerequisite = LogicParser().prerequisite_combinations_list(
            fields["course-prerequisite"])
        self.description = fields["course-summary"] if fields["course-summary"] is not None else default_description

        self.course_prerequisite_tree = deque()

    def __repr__(self):
        return f"<CourseClass: {self.code}: Prerequisites: {self.prerequisite}>"

    def expand_prerequisites(self):
        pass
    # end func
# end class
