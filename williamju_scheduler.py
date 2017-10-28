import re
import course_dictionary
from collections import namedtuple

def course_scheduler (course_descriptions, goal_conditions, initial_state):
    # current state
    # get prereq options
    # decide semester for expanded state and if valid
        # find the latest point in which the expanded course can be added
            # look through current stack of operators
                # contains current iteration of scheduled courses
                # and find the earliest instance of
    # stack of states, each expansion loads all possible expansions of prereqs into the stack
        # continue to evaluate the top of the stack until a failure (can't add prereq)
        # pop this state and evaluate the next one
    state_paths = []
    for goal in goal_conditions:
        # for each possible (disjunction) set of prereqs
        for prereqs in course_descriptions[goal].prereqs:
            state_instance = goal_conditions.copy()
            state_instance.remove(goal)
            state_instance.append(prereqs)
            state_paths.append(state_instance)
    return state_paths


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

def main(argv):
    test = course_dictionary.create_course_dict()
    print(course_scheduler(test, [('CS', 'major')], []))