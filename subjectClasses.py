from .scraper import *
from .appSettings import *

#########################################
#    Classes for real world concepts    #
#########################################


class Semester():
    """The semester class

        A simulation of a realworld semester, contains courses in a python list
        & a cluster of functions used to edit a semester list

    Parameters:
        num (int): the semester number
            DEFAULT VALUE: 1 to prevent NULL semesters
    """

    def __init__(self, num: int = 1):
        self.semester_number = num
        # the list holds the Course objects
        self.courses = []

    def __repr__(self):
        return f'<SemesterClass: Contains: {self.courses}>'
    # add the specified Course object to the list

    def add_course(self, course) -> None:
        """Adds a course object to the semester.courses list
        Parameters:
            course (cls): course to add
        """
        self.courses.append(course)

    # remove the last Course from the list
    def pop_course(self) -> None:
        """Removes the last course object from the list"""
        self.courses.pop()

    # the position in the array that a new Course would be if added
    @property
    def new_course_location(self):
        """Returns the next available location for a course in the semester"""
        return len(self.courses)

    def remove_course(self, code: str) -> None:
        """Removes a course object from the semester.courses list
        Parameters:
            code (str): code of the course to remove
        """
        for course in self.courses:
            if course.code == code:
                del self.courses[self.courses.index(course)]
                break


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

    def __init__(self, parentPage, controller, code: str = "Enter Course Code", parent_semester=Semester()):
        self.parentPage = parentPage
        self.controller = controller
        # Course Code
        self.code = code
        self.old_code = code
        self.first_test = True
        # attributes
        self.WebGet = WebsiteScraper()
        self.Parser = LogicParser()

        # parent Semester for association and what number it is
        self.parent_semester = parent_semester
        self.semester_number = self.parent_semester.semester_number

        # the location in the array that this Course sits
        self.location = self.parent_semester.new_course_location

        # default code
        # !!! Not related to actual website codes !!!
        self.status_code = 200
        # lists of attributes to search
        self.prerequisite = []
        self.recommended = []
        self.companion = []
        self.incompatible = []
        self.description = "Course Description Placeholder Text\nTry pressing Send 2 Web on the Course Search page\nLine 3\nLine 4\nLine 5\nLine 6\nLine 7"

        self.course_prerequisite_tree = deque()

        # associated prerequisite data
        self.prereq_for = []

    def __repr__(self):
        return f'<CourseClass: {self.code}: Prerequisites: {self.prerequisite}>'

    def update_course_info(self, widgit_page_ID: str) -> None:
        """Update the course information by sending a web query and parsing the result
        Parameters:
            widgit_page_ID (str): reference to the status_bar to edit the message of
        """
        # if false do nothing
        if self.old_code != self.code or self.first_test:
            widgit_page_ID.web_query_status.update_scraping_message(self.code)
            soup_object = self.WebGet.fetch_HTML(self.code, year)

            # check if Course exists by searching for course-notfound tag
            try:
                soup_object.find(id='course-notfound').string
                self.status_code = 404
            except:
                self.status_code = 200
            # if all good find items
            if self.status_code == 200:
                widgit_page_ID.web_query_status.update_parsing_message(
                    self.code)
                # following the syntax of parse(the modified result of (the contents of the tag in the BS4 object))
                # if the tag doesnt exist, an error throws and we just return an empty list indicating no items
                try:
                    self.prerequisite = self.Parser.prerequisite_combinations_list(
                        self.WebGet.input_validation(
                            soup_object.find(id='course-prerequisite').string,
                            self.code))
                except:
                    self.prerequisite = []
                # try:
                #     self.recommended = self.Parser.prerequisite_combinations_list(self.WebGet.input_validation(soup_object.find(id='course-recommended-prerequisite').string,self.code))
                # except:
                #     self.recommended = []
                # try:
                #     self.companion = self.Parser.prerequisite_combinations_list(self.WebGet.input_validation(soup_object.find(id='course-companion').string,self.code))
                # except:
                #     self.companion = []
                # try:
                #     self.incompatible = self.Parser.prerequisite_combinations_list(self.WebGet.input_validation(soup_object.find(id='course-incompatible').string,self.code))
                # except:
                #     self.incompatible = []
                try:
                    self.description = soup_object.find(
                        id='course-summary').string
                except:
                    self.description = 'No description given'

                # remove item from null_semester
                if self.code in [c.code for c in self.parentPage.null_semester.courses]:
                    self.parentPage.null_semester.remove_course(self.code)
                    self.controller.course_list = [
                        course for course in self.controller.course_list if course.code != self.code]

                # add to list if not alreadty present
                if self not in self.controller.course_list:
                    self.controller.course_list.append(self)

            elif self.status_code == 404:
                # remove item if possible
                self.controller.course_list = [
                    course for course in self.controller.course_list if course.code != self.code]

            self.old_code = self.code
            self.first_test = False

            status = 0
            for code in set(','.join(self.prerequisite).split(',')):
                if len(code) == 8:  # check its a code and not null
                    for sem in self.parentPage.semesters:
                        for item in sem.courses:
                            if item.code == code:
                                status = 1
                                if status:
                                    break
                        if status:
                            break
                    # which means item doesn't exist yet
                    if not status:
                        # check if code is already present
                        if code not in [course.code for course in self.parentPage.null_semester.courses]:
                            self.parentPage.null_semester.add_course(Course(
                                self.parentPage, self.controller, code=code, parent_semester=self.parentPage.null_semester))
                    status = 0  # reset
            self.parentPage.update_master_course_list()
            widgit_page_ID.web_query_status.update_waiting_message()
        # end if statement

    def map_preprequisite_tree(self, widgit_page_ID: str) -> None:
        """Maps the prerequisites onto a canvas
        Parameters:
            widgit_page_ID (str): reference to the status_bar to edit the message of
        """
        # remove existing items
        self.course_prerequisite_tree.clear()
        self.course_prerequisite_tree = list(self.course_prerequisite_tree)
        # add the Course items for the prereqs
        # transform into set then list again to remove duplicate items
        self.course_prerequisite_tree.append(
            list(set([self.course_from_code(code)
                      for item in self.prerequisite
                      for code in item.split(',')
                      if self.course_from_code(code) != None])))
        # check if there are any prereqs to start with
        if len(self.course_prerequisite_tree[0]) != 0:
            # start at the top, get the nest level and loop through, ends when no prereqs found
            for nest_level, prerequisite_group in enumerate(self.course_prerequisite_tree):
                self.course_prerequisite_tree.append([])
                # for each course in a layer
                for course in prerequisite_group:
                    # update prerequisites if recursive searching
                    if recursive_searching:
                        course.update_course_info(widgit_page_ID)
                    # for each course_code in the course prerequisites
                    for code in set([code for item in course.prerequisite for code in item.split(',')]):
                        current_course = self.course_from_code(code)
                        if current_course != None:
                            # append to the next level down
                            self.course_prerequisite_tree[nest_level +
                                                          1].append(current_course)

                # if we haven't added any new Courses
                if len(self.course_prerequisite_tree[nest_level+1]) == 0:
                    break
        # remove empty list at the end
        self.course_prerequisite_tree.pop()
        # add self to the left
        self.course_prerequisite_tree = deque(self.course_prerequisite_tree)
        self.course_prerequisite_tree.appendleft([self])
        # remove excess items
        layers = [list(set([course.code for course in column]))
                  for column in self.course_prerequisite_tree]
        item_layers = [
            [self.course_from_code(item) for item in layer if item not in
                [items for layer in layers[position+1:] for items in layer]
             ] for position, layer in enumerate(layers)
        ]
        items_to_remove = []
        for position, (tree_layer, label_layer) in enumerate(zip(self.course_prerequisite_tree, item_layers)):
            for course_item in tree_layer:
                if course_item not in label_layer:
                    for prerequisite_item in [self.course_from_code(code) for code in set([code for item in course_item.prerequisite for code in item.split(',')])]:
                        items_to_remove.append(
                            (position + 1, prerequisite_item))
            # remove cases where item appears multiple times in the first layer it appears
            for course_item in set(tree_layer):
                if course_item in label_layer:
                    for i in range(tree_layer.count(course_item)-1):
                        items_to_remove.append(
                            (position, course_item))

        for (pos, course) in items_to_remove:
            self.course_prerequisite_tree[pos].remove(course)

        self.course_prerequisite_tree.reverse()

    def course_from_code(self, code: str):
        """Get a course object from the master list from a code
        Parameters:
            code (str): code of the course to find

        Returns:
            Course object or None
        """
        try:
            return [course for course in self.controller.course_list if course.code == code][0]
        except:
            return None

    # end func
# end class
