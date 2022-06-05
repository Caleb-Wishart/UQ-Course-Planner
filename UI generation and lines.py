import tkinter as tk

# a course class (one for each item) [prerequisite variable to be removed in __init__ (pre...)]
class course():
    def __init__(self,code=None,semester=1,prerequisite=[]):
        # attributes
        self.code = code
        self.semester = semester
        # empty arrays to be changes after script integration
        self.prerequisite = prerequisite
        self.recommended = []
        self.companion = []
        self.incompatible = []

# a class for node lines or travel paths for the connections
class line_node():
    def __init__(self, xpos=0, ypos=0, sem=0, pos=0):
        # attributes
        self.used = False
        self.xpos = xpos
        self.ypos = ypos
        self.number = (sem,pos)

# a class for label nodes for the path connections
class label_node():
    def __init__(self, xpos = 0,ypos=0,parent_course='',number=0):
        # attributes
        self.used = False
        self.xpos = xpos
        self.ypos = ypos
        self.coords = (xpos,ypos)
        self.parent_course = parent_course
        self.number = number

# a custom canvas label with certain attributes and values
class canvas_label():
    
    def __init__(self, course_item=course(), xpos=0, ypos=0):
        super().__init__()

        self.width = 80  # max number of pixels wide
        self.height = 40  # max number of pixels high

        # standard values
        self.course = course_item
        self.xpos = xpos
        self.ypos = ypos
        self.text = self.course.code

        # path connection nodes
        num_nodes = 4
            # Outbound
        self.nodesOut = [label_node(xpos + self.width, ypos + (self.height -6) / num_nodes * num,self.text,num) for num in range(1,num_nodes+1)]
            # inbound
        self.nodesIn = [label_node(xpos, ypos + (self.height -6) / num_nodes * num,self.text,num) for num in range(1,num_nodes+1)]

        # central node for location
        self.nodeC = (xpos + self.width/2, ypos + self.width/2)

        # actual label
        self.tk_item = self.__custom_label()
        self.tk_item.place(x=self.xpos,y=self.ypos,height=self.height,width=self.width)

    # creates a custom tkinter label widget
    def __custom_label(self):
        background = '#d9d9d9' #grey
        textColour = '#000000' #black
        border_type = 'groove'

        return tk.Label(text=self.text,bg=background,fg=textColour,relief=border_type)
    
# object canvas for display purposes
class objectCanvas(tk.Canvas):
    def __init__(self, parent=None,course_list=[]):
        super().__init__(master=parent, bg='grey')

        # function calls
        self.generate_labels(course_list)
        self.generate_lines()

    # generates labels for each item
    def generate_labels(self,course_list):
        # standard values
        xbase = 50
        ybase = 50
        xmove = 140
        ymove = 80
        num_nodes = 4

        # creates the labels and adds them to an array
        self.labels = [canvas_label(    # custom widget class
                course, (xbase + xmove * (course.semester -1)), # sends a course class object, the x position [generated with a base and offset]
                # the y position generated with a base and offset where the offset is determined by getting the index in the list and finding its position in that semester by
                # subtracting the number of courses that come before it e.g if sem 2 pos 2, (assuming 3 course 1st sem) it would interpret as 
                # index = 5, num of courses in previous semster = 3 so multiply offset by 5-3 (2)
                (ybase + ymove * (index - len( [x for x in course_list if x.semester < course.semester] ) ) ) ) 
            for index, course in enumerate(course_list) ] # loop through each item

        # if there is a label generated make corresponding travel nodes
        if len(self.labels) > 0:
            label_width = self.labels[0].width
            label_height = self.labels[0].height

            # create an array holding custom node classes
            self.verticle_nodes = [line_node(
                # x value composed of base and width, then semester offset
                # and finally break the gap between the labels down into the requiired number of positions (based on number of nodes set above)
                xbase + label_width + xmove * (semester) + (xmove - label_width-20)/num_nodes*num, 
                0, semester+1, num) # y value, semester and node number for that semester
                for semester in range(len(course_list)) # loop through each item and... 
                for num in range(1,num_nodes+1)] # add the required number of nodes
            
            # debugging tool to illustrate above nodes as lines [uses the same principles]
            # [(lambda x: self.create_line(x,20,x,300)) (xbase + label_width + xmove * (semester) + (xmove - label_width-20)/num_nodes*num)
            #     for semester in range(len(course_list) - 1) for num in range(1,num_nodes+1)]

            # create an array holding custom node classes
            self.horizontal_nodes = [line_node(0, # class call and x value
                # y value composed of base and height, then course number offset
                # and finally break the gap between the labels down into the requiired number of positions (based on number of nodes set above)
                (ybase + label_height + ymove * (course_num) + (ymove - label_height-10)/num_nodes*num),
                course_num+1, num) # course_number and node number for that semester
                
                # loop through a certain number of times creating nodes based on the largest number of courses in a semester in the plan
                # largest number found by getting the maximum value from a list comprhension that holds the number of times each semester appears in a list
                # generated by another list comprehension that just holds all of the semester in the list of courses and searches for every semester
                for course_num in range(max(
                        [
                            [x.semester for x in course_list].count(search_term)
                                for search_term in range(
                                    max([x.semester for x in course_list])
                                    )
                        ]
                    ))
                for num in range(1,num_nodes+1)] # add the required number of nodes
            
            # debugging tool to illustrate above nodes as lines [uses the same principles as above]
            # [(lambda x: self.create_line(0,x,600,x,fill='light cyan')) (ybase + label_height + ymove * (course_num) + (ymove - label_height-10)/num_nodes*num)
            #     for course_num in range(max([[x.semester for x in course_list].count(_max) for _max in range(max([x.semester for x in course_list]))])) for num in range(1,num_nodes+1)]

    # draw line from label code to course code if label = a prereq
    # the most nested loops you have ever seen
    def generate_lines(self):
        for major_label in self.labels: # get one label
            if len(major_label.course.prerequisite) > 0: # only proceed if one exists
                for minor_label in self.labels: # get second label
                    if minor_label.course.code in major_label.course.prerequisite:  # check if second label is in prerequisites
                        for major_node in major_label.nodesIn: # get first node
                            if not major_node.used: # ensure its not used
                                for minor_node in minor_label.nodesOut: # get second node
                                    if not minor_node.used: # check its not used
                                        if minor_label.course.semester + 1 == major_label.course.semester: # if in sequential semesters
                                            if major_node.ypos == minor_node.ypos:  # if they are on the same y-level
                                                self.create_line(minor_node.coords,major_node.coords,fill='red') # create line using direct coordinates 
                                                major_node.used, minor_node.used = True,True # mark as used

                                                print('No itermediate for {} to {} || used minor {} and major {}'.format(minor_label.text,
                                                    major_label.text,minor_node.number,major_node.number),end='\n\n')

                                                break # break out of minor_node search when line is created
                                            else: # if they aren't on the same level
                                                # check through verticle nodes backwards to preference closer nodes to lines that have to go to other locations
                                                for v_node in self.verticle_nodes[::-1]:  
                                                    # check node isn't used and that the node is on the right semester
                                                    if not v_node.used and v_node.number[0] == minor_label.course.semester: 
                                                        self.create_line(minor_node.coords,(v_node.xpos,minor_node.ypos), # create line using coordinates of lines and v-line
                                                            (v_node.xpos,major_node.ypos),major_node.coords,fill='red')
                                                        major_node.used, minor_node.used, v_node.used = True,True,True # mark as used

                                                        print('Itermediate used for {} to {} || used minor {} and major {} || used v_node {}'.format(minor_label.text,
                                                            major_label.text,minor_node.number,major_node.number,v_node.number),end='\n\n')

                                                        break # out of v_node search when line created
                                                break # break out of minor_node search when line is created
                                        else: # if they aren't on sequential semesters
                                            for v_node_minor in self.verticle_nodes:  # check through verticle nodes
                                                    # check node isn't used and that the node is on the right semester
                                                    if not v_node_minor.used and v_node_minor.number[0] == minor_label.course.semester: 
                                                        for h_node in self.horizontal_nodes:
                                                            if not h_node.used: 
                                                                for v_node_major in self.verticle_nodes:  # check through verticle nodes
                                                                    # check node isn't used and that the node is on the right semester
                                                                    if not v_node_major.used and v_node_major.number[0] == major_label.course.semester-1: 
                                                                        # create line using coordinates of lines, v-line and h-line 
                                                                        # from label to v-line to h-line to h-line to v-line to label
                                                                        self.create_line(minor_node.coords,(v_node_minor.xpos,minor_node.ypos),
                                                                            (v_node_minor.xpos,h_node.ypos),(v_node_major.xpos,h_node.ypos), 
                                                                            (v_node_major.xpos,major_node.ypos),major_node.coords,fill='red')

                                                                        major_node.used, minor_node.used = True,True # mark as used
                                                                        v_node_minor.used, v_node_major.used, h_node.used = True,True,True # mark as used

                                                                        print('Itermediate used for {} to {} || used minor {} and major {} || used minor v_node {} || used h_node {} || used major v_node {}'.format(minor_label.text, major_label.text,minor_node.number,major_node.number,v_node_minor.number,h_node.number, v_node_major.number),end='\n\n')  
                                                                        break # out of v_node search when line created 
                                                                break # out of h_node search when line created 
                                                        break # out of v_node search when line created 
                                            break # break out of minor_node search when line is created
                                break # break out of major_node search when line is created or when minor_nodes run out

# creates the application
class Application():

    def __init__(self, master=None):
        # Window Managment
        master.title('Lines experimentation')
        master.geometry('700x400')
        master.resizable(0,0)
        
        # creates a test array of items with set prerequisites for testing
        test_items = [
            course('AAAA0000',1),
            course('AAAA1111',1),
            course('AAAA2222',1),
            course('BBBB0000',2,prerequisite=['AAAA0000','AAAA2222']),
            course('BBBB1111',2,prerequisite=['AAAA1111']),
            course('CCCC0000',3,prerequisite=['AAAA0000']),
            course('CCCC1111',3),
            course('DDDD0000',4,prerequisite=['AAAA2222','BBBB1111','CCCC1111'])
            ]
        # creating the canvas
        canvas = objectCanvas(master,test_items)
        canvas.pack(fill=tk.BOTH, expand=True)

# call
if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master=root)
    root.mainloop()