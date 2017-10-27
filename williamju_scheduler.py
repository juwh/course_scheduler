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
    """
    state = state_init(course_descriptions, goal_conditions)
    while set(state) != set(initial_state):


def state_init (course_descriptions, goal_conditions):
    """
    Creates a stack of stacks of composed of prerequisites for the goal conditions.
    :param course_descriptions: course catalog dictionary
    :param goal_conditions: courses that must be included in the generated schedule
    :return: stack with prerequisites to goal_conditions appended
    """
    frontier = []
    for course in goal_conditions:
        for prereq in course_descriptions[course].prereqs:
            frontier.append(prereq)
    return frontier

def operated_state (operator, state, operators, terms):
    """
    Expands the course at the top of the frontier stack to include the top course
    prerequisites with the operator.
    :param operator:
    :param state:
    :param operators:
    :param terms:
    :return: updated frontier variable with the operator applied.
    """
def generate_operator (prereqs, course, term, credits):
    Operator = namedtuple('Operator', 'pre_conditions, post_conditions, ScheduledTerm, credits')

def valid_term (course, constraints):
