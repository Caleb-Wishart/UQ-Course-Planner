from __future__ import annotations

from collections import deque
from typing import List
import re
import json

# from .scraper import fetch_HTML, get_Field_Contents
# from .parser import parse_prerequisites
from scraper import fetch_HTML, get_Field_Contents
from parser import parse_prerequisites

default_description = (
    "Course Description Placeholder Text\n"
    "Try pressing Send 2 Web on the Course Search page\n"
    "Line 3\n"
    "Line 4\n"
    "Line 5\n"
    "Line 6\n"
    "Line 7"
    )

#########################################
#    Classes for real world concepts    #
#########################################

class Course:
    """
    The Course class

    A simulation of a realworld course, contains information on the course
    i.e. code, description, prerequisites
    & a cluster of functions used to update the information and find a
    course object

    """
    courses = {}

    re_course_code = re.compile(r'[A-Z]{4}\d{4}(?!.)')

    def __init__(self, code: str, scrape: bool = True):
        """
        Initialise the Course and scrape the web to find the information

        :param code: the course code used to scrape the web and for reference
        """
        # Course Code
        self.code : str = code
        # attributes
        if scrape:
            (soup, self.status_code) = fetch_HTML(self.code)
        else:
            (soup, self.status_code) = (None, 404)

        # lists of attributes to search
        search_fields = ["course-prerequisite", "course-summary"]
        fields = {key: get_Field_Contents(
            soup, key, self.code) for key in search_fields}

        self.recommended = []
        self.companion = []
        self.incompatible = []

        self.prerequisite = parse_prerequisites(
            fields["course-prerequisite"])

        self.description = fields["course-summary"] if fields["course-summary"] is not None else default_description

        self.prerequisite_tree = None

        Course.courses[self.code] = self

    def __repr__(self):
        return f"<{self.code}: Prerequisites: {self.prerequisite}>"

    def expand_prerequisites(self) -> None:
        if self.prerequisite_tree is None:
            tree = deque()
            tree.append(Course.getPrerequisites(self))

    @staticmethod
    def getCourse(key: str) -> Course | None:
        try:
            return Course.courses[key]
        except KeyError as e:
            if re.match(Course.re_course_code, key):
                return Course(key)
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
        return [course.code for course in Course.courses.values()]

    @staticmethod
    def dump() -> str:
        return json.dumps([course.__dict__ for course in Course.courses])

    @staticmethod
    def load(raw : str) -> None:
        data = json.loads(raw)
        for course in data:
            if 'code' not in course:
                continue
            c = Course(course['code'], scrape=False)
            for key in course.keys():
                # if the key exists set it
                if key in c.__dict__.keys():
                    c.__setattr__(key, course[key])


if __name__ == "__main__":
    with open("save/data.json") as f:
        Course.load(f.read())
    for c in Course.getCourseNames():
        print(Course.getCourse(c))

# ʕ •ᴥ•ʔ
