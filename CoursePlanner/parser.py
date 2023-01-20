import re
from typing import List
from sys import stderr
#########################################
#   Parser to parse a logic statement   #
#########################################

"""
The logic parser

A cluster of functions used to breakdown a string that contains logical operators
i.e. AND, OR, commas, parentheses
"""
# regex for matching Course codes
re_course_code = re.compile(r'[A-Z]{4}\d{4}')
# regex for matching logical operators
re_non_course_code = re.compile(r'((and)|(or)|(\()|(\)))')

_results : List[str]= ['']

def __error(loc : str, work_array: List[str], item: str) -> None:
    """
    Simple error message

    :param loc: The calling sfunction
    :param work_array: the work to be done for debugging
    :param item: the item being parsed
    """
    print((f'Sorry something went wrong in the {loc},'
                'below are variable values for debugging'), file=stderr)
    print('Final Options:  ', _results, file=stderr)
    print('Work array ended at: ', work_array, file=stderr)
    print('The current item was: ', item, file=stderr)
    exit()

def __logical_AND(inp: str) -> List[str]:
    """
    Private Method
    split a string with containing a logical 'AND'
    Handles parentheses maintaing correct order of operations

    :param inp: a string to remove parentheses from

    :return: A list of strings that contain the components split by AND
    """
    # some string that theoertically should not be found in the input
    token = "0xDEADBEEF_"
    # find all of the top level parentheses
    parentheses_blocks = re.findall(r'\((?:[^()]*|\([^()]*\))*\)', inp)
    # replace all of the top level bracket sections with token's
    for index in range(len(parentheses_blocks)):
        inp = inp.replace(parentheses_blocks[index], token)

    # split content in required Courses by Logical AND
    components = re.split(' AND ', inp)

    # if the item is an token replace it with the token contents otherwise
    # return the item
    tokenNum = 0
    for index, item in enumerate(components):
        while item.find(token) != -1:
                    contents = parentheses_blocks[tokenNum][1:-1]
                    # replace the token with the contents of the parentheses
                    item = item.replace(token, contents, 1)
                    tokenNum += 1
        components[index] = item

    assert tokenNum == len(parentheses_blocks), "Failed to find a token"

    return components

def __logical_OR(work_array: list) -> None:
    """
    Private Method
    return the two sides of an OR operator and solve the logic,
    duplicate the existing items in the result as there is a branched path
    Do not have to worry about parentheses due to order of operations

    :param work_array: the current work 'stack'
    """
    # tracker for which iteration we are on
    num = 0
    # Note, this does require calculating the same item multiple times,
    # TODO: implement a caching mechanism

    # duplicate final array enough times so each option appears in the right spot
    new_results = _results * len(work_array)
    # duplicate the work array items so that they appear on each instance of the final product
    work_array = work_array * len(_results)
    # while there are still options
    while len(work_array) != 0:
        working_item = work_array[0]
        if (
            # if the item is just a Course code
            (len(working_item) == 8 and re_course_code.search(working_item))
            or
            # if there is no further parentheses_breakdown item add it to the list
            (working_item.find(' AND ') == -1 and working_item.find(' OR ') == -1)
        ):
            # either set that option to the item
            if len(new_results[num]) == 0:
                new_results[num] = working_item
            # or add it to the end if one exists already in that line
            else:
                new_results[num] += f',{working_item}'

        # if the working item contains a nested AND function
        # but not an OR function try breaking it down,
        elif working_item.find(' AND ') != -1:
            work_array_and = __logical_AND(working_item[1:-1])
            for item in work_array_and:
                # FIXME if there are further nested entries throw an error
                # as I am too lazy to try and get it to sort out the rest atm,
                if re_non_course_code.search(item):
                    raise Exception('Required Courses are too complicated'
                                    +' to parse\n For support please add'
                                    + 'a feature request on Github with'
                                    + 'the course course name')
                else:
                    # either set that option to the item
                    if len(new_results[num]) == 0:
                        new_results[num] = item
                    # or add it to the end if one exists already in that line
                    else:
                        new_results[num] += f',{item}'
        else:
            # failsafe
            __error("__logical_OR", work_array, working_item)
        num += 1
        # remove item from the process queue
        work_array.remove(working_item)

    # set the master list to be the different branches of the process completed above
    _results = [item for item in new_results]

def __parse(inp: str) -> None:
    """
    Private Method
    seperate a string by logical operator or add the result to the final options if it is a course code \[A-Z]{4}\d{4}\\

    :param work_array: the current work 'stack'
    """
    # do an initial parse for any AND's
    # if none exist item is the same as [inp]
    work_array : List[str] = __logical_AND(inp)
    # while there are still options
    while len(work_array) != 0:
        working_item = work_array[0]
        # if the current item matches a Course code add it to the final options list(s)
        if len(working_item) == 8 and re_course_code.search(working_item):
            # if this is the first item to be computer make the array that item
            if _results[0] == '':
                _results = [working_item]
            else:
                _results = [
                    item + f',{working_item}' for item in _results]
        # if the current item contains an OR logical operator send it to the OR function to process
        elif working_item.find(' OR ') != -1:
            component = re.split(' OR ', working_item)
            __logical_OR(component)
        else:
            # failsafe
            __error("__parse", work_array, working_item)
        work_array.remove(working_item)

def parse_prerequisites(content: str | None) -> List[str]:
    """
    Find the prerequsite combinations available for a given course from website data

    :param content: The content to parse
    :return: A copy of a list of the different possible combinations
    """
    # set the final result list to empty
    _results = ['']
    # TODO: caching system
    if content is None:
        return _results
    # starts the process
    __parse(content)
    return list(_results)

# ʕ •ᴥ•ʔ