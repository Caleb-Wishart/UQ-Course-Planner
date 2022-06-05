from .scraper import *
from .appSettings import *

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
        self.description = "Course Description Placeholder Text\nTry pressing Send 2 Web on the Course Search page\nLine 3\nLine 4\nLine 5\nLine 6\nLine 7"

        self.prerequisiteMap = deque()

        # associated prerequisite data
        self.prereq_for = []

    def updateCourseInfo(self,widgitPageID):
        # if false do nothing
        if self.old_code != self.code or self.firstTest:
            widgitPageID.webQueryStatus.updateScraping(self.code)
            soup_object = self.webGet.fetchHTML(self.code,year)

            # check if course exists by searching for course-notfound tag
            try:
                soup_object.find(id='course-notfound').string
                self.status_code = 404
            except:
                self.status_code = 200
            # if all good find items
            if self.status_code == 200:
                widgitPageID.webQueryStatus.updateParsing(self.code)
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

                # remove item from null_semester
                if self.code in [c.code for c in self.parentPage.null_semester.courses]:
                    self.parentPage.null_semester.removeCourse(self.code)
                    self.controller.courseList = [course for course in self.controller.courseList if course.code != self.code]

                # add to list if not alreadty present
                if self not in self.controller.courseList:
                    self.controller.courseList.append(self)

            elif self.status_code == 404:
                # remove item if possible
                self.controller.courseList = [course for course in self.controller.courseList if course.code != self.code]

            self.old_code = self.code
            self.firstTest = False

            status = 0
            for code in set(','.join(self.prerequisite).split(',')):
                if len(code) == 8: # check its a code and not null
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
                            self.parentPage.null_semester.addCourse(course(self.parentPage,self.controller,code=code,parent_semester=self.parentPage.null_semester))
                    status = 0 # reset
            self.parentPage.updateMasterCourseList()
            widgitPageID.webQueryStatus.updateNormal()
        # end if statement

    def prerequisiteMapping(self,widgitPageID):
        # remove existing items
        self.prerequisiteMap.clear()
        self.prerequisiteMap = list(self.prerequisiteMap)
        # add the course items for the prereqs
        # transform into set then list again to remove duplicate items
        self.prerequisiteMap.append(
            list(set([self.courseFromCode(code)
                for item in self.prerequisite
                    for code in item.split(',')
                if self.courseFromCode(code) != None])))
        # check if there are any prereqs to start with
        if len(self.prerequisiteMap[0]) != 0:
            # start at the top, get the nest level and loop through, ends when no prereqs found
            for nestLevel, prereqGroup in enumerate(self.prerequisiteMap):
                self.prerequisiteMap.append([])
                for course in prereqGroup:
                    if recursive_searching:
                        course.updateCourseInfo(widgitPageID)
                    # for code in course.prerequisite: # this code can be uncommented when creating a system to deal with alternate options
                    for code in set([code for item in course.prerequisite for code in item.split(',')]):
                        if self.courseFromCode(code) != None:
                            self.prerequisiteMap[nestLevel+1].append(self.courseFromCode(code))
                # if we haven't added any new courses
                if len(self.prerequisiteMap[nestLevel+1]) == 0:
                    break
        # remove empty list at the end
        self.prerequisiteMap.pop()
        # add self to the left
        self.prerequisiteMap = deque(self.prerequisiteMap)
        self.prerequisiteMap.appendleft([self])

    def courseFromCode(self,code):
        try:
            return [course for course in self.controller.courseList if course.code == code][0]
        except:
            return None

    # end func
# end class