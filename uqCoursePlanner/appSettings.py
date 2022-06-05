#########################################
#              GLOBAL IMPORTS           #
#########################################

from sys import stderr
from collections import deque

#########################################
#         MISC GLOBAL VARIABLES         #
#########################################

#### Q.O.L variables ####
line_ending = '\n------------------------\n'
# taken to subjectClasses -> customWidgets -> main

#### LOGGING ####
# verbose_output forces error_logs ON when True
verbose_output = True

error_logs = True

##### SCRAPER SETTINGS ####

# email for bug reports / requests
email = 'cw.online.acc@outlook.com'

# year to look for in URL
year = '2020'

#### USER SETTINGS ####
recursive_searching = True

course_per_new_semester = 1

#########################################
#        CUSTOM GLOBAL FUNCTIONS        #
#########################################
def endPrint(*args,**kwargs):
    print(*args,**kwargs,end=line_ending)

# *args are values, **kwargs are print options
def verbosePrint(*args,**kwargs):
    if verbose_output:
        endPrint(*args,**kwargs) 

def errorPrint(*args, **kargs):
    if error_logs or verbose_output:
        endPrint(*args,**kargs)  