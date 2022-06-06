
from __future__ import annotations

from collections import deque
import re
import threading
from typing import List

from .scraper import Scraper
from .parser import Parser

default_description = "Course Description Placeholder Text\nTry pressing Send 2 Web on the Course Search page\nLine 3\nLine 4\nLine 5\nLine 6\nLine 7"
#########################################
#    Classes for real world concepts    #
#########################################


class Course():
    """The Course class

        A simulation of a realworld course, contains information on the course
        i.e. code, description, prerequisites
        & a cluster of functions used to update the information and find a
        course object

    Parameters:
        parentApp (cls): Parent application for reference.
        controller (tk.Tk()): tkinter Tk class
        code (str): the course code used to scrape the web and for reference
            DEFAULT VALUE: for something to show on a label
        parent_semester (semester()): used for reference
            DEFAULT VALUE: assigns a semester
    """
    courses = {}
    coursesLock = threading.Lock()

    re_course_code = re.compile(r'[A-Z]{4}\d{4}(?!.)')

    def __init__(self, code: str):
        # Course Code
        self.code = code

        # attributes
        (soup, self.status_code) = Scraper.fetch_HTML(self.code)

        # lists of attributes to search
        search_fields = ["course-prerequisite", "course-summary"]
        fields = {key: Scraper.get_Field_Contents(
            soup, key, self.code) for key in search_fields}

        self.recommended = []
        self.companion = []
        self.incompatible = []

        self.prerequisite = Parser().parse_prerequisites(
            fields["course-prerequisite"])
        self.description = fields["course-summary"] if fields["course-summary"] is not None else default_description

        self.prerequisite_tree = None
        self.searchMark = 0

        Course.courses[self.code] = self

    def __repr__(self):
        return f"<{self.code}: Prerequisites: {self.prerequisite}>"

    def expand_prerequisites(self) -> None:
        if self.prerequisite_tree is None:
            tree = deque()
            tree.append(Course.getPrerequisites(self))

    @staticmethod
    def getCourse(key) -> Course | None:
        with Course.coursesLock:
            try:
                return Course.courses[key]
            except KeyError as e:
                if re.match(Course.re_course_code, key):
                    Course.courses[key] = Course(key)
                    return Course.courses[key]
                else:
                    return None

    @property
    def hasPrerequisite(self) -> bool:
        return True if len(self.prerequisite) else False

    @staticmethod
    def getPrerequisites(course) -> List[Course]:
        return list({Course.getCourse(key.strip())
                     for item in course.prerequisite for key in item.split(',')})

    @staticmethod
    def getCourseNames() -> List[str]:
        with Course.coursesLock:
            return [course.code for course in Course.courses.values()]
    # end func
# end class
