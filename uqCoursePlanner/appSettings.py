#########################################
#              GLOBAL IMPORTS           #
#########################################

from sys import stderr
from collections import deque

#########################################
#         MISC GLOBAL VARIABLES         #
#########################################
#### USER SETTINGS ####

#### Q.O.L variables ####
line_ending = "\n------------------------------------------------\n"
line_segment = "------------------------------------------------"
# taken to subjectClasses -> customWidgets -> main

#### APP DATA ####
Appversion = "0.3.0"

#### LOGGING ####
# verbose_output forces error_logs ON when True
verbose_output = True

error_logs = True

##### SCRAPER SETTINGS ####

# email for bug reports / requests
email = "cw.online.acc@outlook.com"

# year to look for in URL
year = "2021"

#### USER SETTINGS ####
recursive_searching = True

Course_per_new_Semester = 1

default_description = "Course Description Placeholder Text\nTry pressing Send 2 Web on the Course Search page\nLine 3\nLine 4\nLine 5\nLine 6\nLine 7"

#########################################
#        CUSTOM GLOBAL FUNCTIONS        #
#########################################


def end_print(*args, **kwargs):
    """A custom print function that has a seperator"""
    if "end" in kwargs:
        print(*args, **kwargs)
    else:
        print(*args, **kwargs, end=line_ending)

# *args are values, **kwargs are print options
#  white, black, red, blue, green, yellow, magenta, and cyan


def verbose_print(*args, **kwargs):
    """A custom print function used for selective output"""
    if verbose_output:
        end_print(*args, **kwargs)


def error_print(*args, **kargs):
    """A custom print function used for selective output"""
    if error_logs or verbose_output:
        end_print(*args, **kargs)
