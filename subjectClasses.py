from sys import stderr
from scraper import *

#########################################
#    Classes for real world concepts    #
#########################################

# a semester class to group course objects
class semester():
    # the semester number
    # DEFAULT = 1 to prevent NULL semesters
    def __init__(self,num=1):
        self.semester_number = num
        # the list holds the course objects
        self.courses = []
    
    # add the specified course object to the list
    def addCourse(self,course):
        self.courses.append(course)

    # remove the last course from the list
    def popCourse(self):
        self.courses.pop()

    # the position in the array that a new course would be if added
    def newCourseLocation(self):
        return len(self.courses)

    def removeCourse(self,code):
        for course in self.courses:
            if course.code == code:
                del self.courses[self.courses.index(course)]
                break

# a course class (one for each item)
class course():
    # the course code for the object and parent_semester object for association
    # DEFAULT: code (user prompt), parent_semester (prevents no association)
    def __init__(self,parentPage,controller,code="Enter Course Code",parent_semester=semester()):
        self.parentPage = parentPage
        self.controller = controller
        # course Code
        self.code = code
        self.old_code = code
        self.firstTest = True
        # attributes
        self.webGet = websiteScraper()
        self.parser = logicParser()

        # parent semester for association and what number it is
        self.parent_semester = parent_semester
        self.semester_number = self.parent_semester.semester_number
        
        # the location in the array that this course sits
        self.location = self.parent_semester.newCourseLocation()
        
        # default code 
        # !!! Not related to actual website codes !!!
        self.status_code = 200
        # lists of attributes to search
        self.prerequisite = []
        self.recommended = []
        self.companion = []
        self.incompatible = []
        self.description = "Course Description Placeholder Text\nLine 2\nLine 3\nLine 4\nLine 5\nLine 6\nLine 7"

        # associated prerequisite data
        self.num_prereq_has = 0
        self.num_prereq_of = 0
           
    def update(self):
        if self.old_code != self.code or self.firstTest:        
            soup_object = self.webGet.fetchHTML(self.code,year)

            # check if course exists by searching for course-notfound tag
            try: 
                soup_object.find(id='course-notfound').string
                self.status_code = 404
            except:
                self.status_code = 200
            if self.status_code == 200:
                # following the syntax of parse(the modified result of (the contents of the tag in the BS4 object))
                # if the tag doesnt exist, an error throws and we just return an empty list indicating no items
                try:
                    self.prerequisite = self.parser.combinationsList(self.webGet.inputModification(soup_object.find(id='course-prerequisite').string,self.code))
                except:
                    self.prerequisite = []
                # try:
                #     self.recommended = self.parser.combinationsList(self.webGet.inputModification(soup_object.find(id='course-recommended-prerequisite').string,self.code))
                # except:
                #     self.recommended = []
                # try:
                #     self.companion = self.parser.combinationsList(self.webGet.inputModification(soup_object.find(id='course-companion').string,self.code))
                # except:
                #     self.companion = []
                # try:
                #     self.incompatible = self.parser.combinationsList(self.webGet.inputModification(soup_object.find(id='course-incompatible').string,self.code))
                # except:
                #     self.incompatible = []
                try:
                    self.description = soup_object.find(id='course-summary').string
                except:
                    self.description = 'No description given'
                
                self.controller.courseList.append(self)
            elif self.status_code == 404:
                # remove item if possible
                try:
                    self.controller.courseList.remove(self)
                except:
                    # do nothing as if item isn't in list we don't need to remove anything
                    pass

            self.old_code = self.code
            self.firstTest = False

            # remove remove item from null_semester
            if self.code in [c.code for c in self.parentPage.null_semester.courses]:
                self.parentPage.null_semester.removeCourse(self.code)

            status = 0
            for code in set(','.join(self.prerequisite).split(',')):
                if len(code) == 8: # check its a code and not null
                    print(code,end=line_ending)
                    self.num_prereq_has += 1
                    for sem in self.parentPage.semesters:
                        for item in sem.courses:
                            if item.code == code:
                                item.addPreFor()
                                status = 1
                                if status:
                                    break
                        if status:
                                break
                    # which means item doesn't exist
                    if not status:
                        self.parentPage.null_semester.addCourse(course(self.parentPage,self.controller,code=code,parent_semester=self.parentPage.null_semester))
                    status = 0
            # update in master list

    def addPreFor(self):
        self.num_prereq_of += 1