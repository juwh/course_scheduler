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
    state_paths = state_init(course_descriptions, goal_conditions)
    current_state = state_paths[len(state_paths)-1] if len(state_paths) != 0 else []
    print(current_state)
    print(is_higher_requirement(('CS', 'major')))
    # take the first state (goal conditions)

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

def is_higher_requirement (course):
    return not course[1].isnumeric()

def state_init (course_descriptions, goal_conditions):
    """
    Creates a stack of stacks of composed of prerequisites for the goal conditions.
    :param course_descriptions: course catalog dictionary
    :param goal_conditions: courses that must be included in the generated schedule
    :return: stack with prerequisites to goal_conditions appended
    """
    state_paths = []
    for goal in goal_conditions:
        # for each possible (disjunction) set of prereqs
        for prereqs in course_descriptions[goal].prereqs:
            state_instance = goal_conditions.copy()
            state_instance.remove(goal)
            state_instance += list(prereqs)
            state_paths.append(state_instance)
    return state_paths

def main(argv):
    test = course_dictionary.create_course_dict()
    course_scheduler(test, [('CS', 'major'), ('CS', '4269')], [])

if __name__ == "__main__":
    main(sys.argv)