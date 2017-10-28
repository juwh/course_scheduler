import sys
import course_dictionary
from collections import namedtuple
from enum import IntEnum

MAX_NUMBER_OF_TERMS = 11
MAX_CREDITS_PER_NON_SUMMER_TERM = 18
MIN_CREDITS_PER_NON_SUMMER_TERM = 12
MAX_CREDITS_PER_SUMMER_TERM = 6
MIN_CREDITS_PER_SUMMER_TERM = 0

Course = namedtuple('Course', 'program, designation')
CourseInfo = namedtuple('CourseInfo', 'credits, terms, prereqs')
Operator = namedtuple('Operator', 'PRE, EFF, ScheduledTerm, credits')

class ScheduledCourse:
    def __init__(self, course, courseInfo, term):
        self.course = course
        self.courseInfo = courseInfo
        self.term = term

    def __hash__(self):
        return hash((self.course, self.term))

    def __eq__(self, other):
        return other and self.course == other.course and self.term == other.term

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        # return "<ScheduledCourse course:%s term:%s>" % (self.course, self.term)
        return "(%s, %s)" % (self.course, self.term)

    def __str__(self):
        return "From str method of ScheduledCourse: course is %s, term is %s" % (self.course, self.term)

class Semester(IntEnum):
  Fall = 1
  Spring = 2
  Summer = 3

class Year(IntEnum):
  Frosh = 0
  Sophomore = 1
  Junior = 2
  Senior = 3

class Term:
    def __init__(self, semester, year):
        self.semester = semester
        self.year = year
        semesterNo = Semester(semester)
        yearNo = Year(year)
        self.termNo = int(yearNo) * 3 + int(semesterNo)

    # Basically a second constructor
    @classmethod
    def initFromTermNo(clazz, termNo):
        # intentional integer division
        yearNo = int(int(termNo - 1) / int(3))
        semesterNo = termNo - (3 * yearNo)
        semester = Semester(semesterNo)
        year = Year(yearNo)
        return clazz(semester, year)

    def __hash__(self):
        return hash((self.termNo))

    def __eq__(self, other):
        return other and self.termNo == other.termNo

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        # return "<Term semester:%s year:%s>" % (self.semester, self.year)
        return "(%s, %s)" % (self.semester, self.year)

    def __str__(self):
        # return "From str method of Term: semester is %s, year is %s" % (self.semester, self.year)
        return "(%s, %s)" % (self.semester, self.year)

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
    operator_stack, state_stack = state_init(course_descriptions, goal_conditions)
    print(state_stack)
    print(operator_stack)
    print(is_higher_requirement(('CS', 'major')))
    print(Semester(3).name)
    # take the first state (goal conditions)
    operator_state = state_stack[len(state_stack)-1] if len(state_stack) != 0 else []
    # check if stack of states is empty (tried all options)
    while not operator_state:
        print(operator_state)
        # get the top course of the top state
        top_course = operator_state[len(operator_state)-1]
        # check if the top course exists in the initial state
        if not initial_state.count(top_course):
            # get a valid term for the top course
            valid_term = scheduled_term(course_descriptions, top_course, operator_stack)
            if valid_term:
                # there is a valid term so for each possible prereqs options
                # replace the top course being considered and add it to state_stack
                operator_state.pop()
                top_course_prereqs = course_descriptions[top_course].prereqs
                if top_course_prereqs:
                    state_pop = state_stack.pop()
                    for prereqs in top_course_prereqs:
                        state_add = state_pop.copy()
                        state_add += list(prereqs)
                        state_stack.append(state_add)
            else:
                # no valid option so pop the state from the state_stack; leads to the next possible
                # option for a prereq completion
                state_stack.pop()
                if len(state_stack) > 0:
                    operator_stack = backtrack_operator_stack(operator_stack,
                                                              state_stack[len(state_stack)-1])
        else:
            # remove if course already fulfilled by initial state
            operator_state.pop()
        operator_state = state_stack[len(state_stack) - 1] if len(state_stack) != 0 else []

    # take the top condition
    # for the condition to
        # create an operator (latest term) if the condition is not in the initial state; otherwise, "remove" the
        # course that can be found in the initial state (this would differentiate from the initial state equality
        # to end the regression scheduler while loop, moving to an empty frontier requirement)
            # latest term is dependent on maximum credit hours, moves behind higher req (determined by looking through
            # prereqs of scheduled terms going forwards freshman year fall; the course must fall behind the first
            # instance of a higher requirement)
                # if no higher requirement is found through the scheduled courses list, simply place at latest
                # (Senior Spring)

    # in the case that a course reappears as part of the prereqs for another course,
    # identify the earliest point in which that prereq must occur and delete other instances
    # not a concern until a prereq that has been scheduled reappears later

def backtrack_operator_stack(operator_stack, top_course):
    return None

def scheduled_term (course_descriptions, course, operator_stack):
    return None

def is_higher_requirement (course):
    return not course[1].isnumeric()

def state_init (course_descriptions, goal_conditions):
    """
    Creates a stack of stacks of composed of prerequisites for the goal conditions.
    :param course_descriptions: course catalog dictionary
    :param goal_conditions: courses that must be included in the generated schedule
    :return: stack with prerequisites to goal_conditions appended
    """
    state_stack = []
    for goal in goal_conditions:
        # for each possible (disjunction) set of prereqs
        for prereqs in course_descriptions[goal].prereqs:
            state_instance = goal_conditions.copy()
            state_instance.remove(goal)
            state_instance += list(prereqs)
            state_stack.append(state_instance)
    top_course = goal_conditions.copy().pop()
    top_course_description = course_descriptions[top_course]
    top_course_prereqs = top_course_description.prereqs
    top_operator = Operator(top_course_prereqs[len(top_course_prereqs)-1] if len(top_course_prereqs) != 0 else [],
                            top_course, Term.initFromTermNo(MAX_NUMBER_OF_TERMS), top_course_description.credits)
    operator_stack = [top_operator]
    return operator_stack, state_stack

def main(argv):
    test = course_dictionary.create_course_dict()
    course_scheduler(test, [('CS', 'major'), ('CS', '4269')], [])

if __name__ == "__main__":
    main(sys.argv)