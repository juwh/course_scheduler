import re
import course_dictionary
from collections import namedtuple

def course_scheduler (course_descriptions, goal_conditions, initial_state):
    """
    Creates a course schedule from goal conditions and an initial state.
    Keys: namedtuple of the form ('program, designation')
    Values: namedtuple of the form('name, prereqs, credits')
            prereqs is a tuple of prereqs where each prereq has the same form as the keys

    Operates by taking a tuple of goal conditions, evaluating in order of the tuple,
    by expanding the prerequisites to fulfill the course

    Two key pieces of information stored:
    State in the state space of the regression planner (conjunction of courses and/or higher-
    level requirements
    List of operators OR list of scheduled courses
    Search is reflected by a frontier

    Operations:
    stack variable created, take goal conditions and append the prereqs to the stack
    now consider the stack variable (while the current state of the stack does not equal initial)
    pop first condition, check if higher level requirement (a.isdigit()), generate operator

    definition_operator takes operator and current state and generates next state which is appended
    to the stack

    Ideas:
    secondary stack "orders" the course/HLR that we are expanding
    the secondary stack should not replace HLR or courses anyways and continues to push
    prereqs to the top of the stack
    IF the course is not valid, the added course is popped and the next prereq is considered (next OR
    if dysjunction includes multiple entries)
    """
    Operator = namedtuple('Operator', 'pre_conditions, post_conditions, ScheduledTerm, credits')

    solution = {}
    # just add the goals without their prereqs
    for goalCourse in goal_conditions:
        courseInfo = course_descriptions[goalCourse]
        # terms should contain a single semester, and year,
        # not a list of possible semesters
        solution[goalCourse] = course_dictionary.CourseInfo(courseInfo.credits, ('Fall', 'Senior'), courseInfo.prereqs)
        print("***************student solution returning solution:************")
        print(solution)
    return solution
