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
    tuple_stack = state_init(course_descriptions, goal_conditions)
    final_operator_stack = []
    print(tuple_stack)
    print(is_higher_requirement(('CS', 'major')))
    print(Semester(3).name)
    # take the top tuple
    top_tuple = tuple_stack[len(tuple_stack)-1] if len(tuple_stack) != 0 else ()
    # take the first state
    operated_state = []
    if top_tuple:
        operated_state = top_tuple[0] if len(top_tuple[0]) != 0 else []
    # check if stack of states is empty (tried all options)
    """
    top_course = operated_state[len(operated_state) - 1]
    final_operator_stack = top_tuple[1]
    valid_term = scheduled_term(course_descriptions, top_course, final_operator_stack)
    print(top_course)
    print(final_operator_stack)
    print(valid_term)
    """
    while operated_state:
        #print(operated_state)
        # get the top course of the top state
        top_course = operated_state[len(operated_state)-1]
        final_operator_stack = top_tuple[1]
        print(generate_schedule_hours(generate_operator_schedule(final_operator_stack)))
        # check if the top course exists in the initial state
        if not initial_state.count(top_course):
            # get a valid term for the top course
            operator_schedule = generate_operator_schedule(final_operator_stack)
            scheduled = in_schedule(operator_schedule)
            if scheduled:
                valid_term = scheduled_term(course_descriptions, top_course, operator_schedule)
                print(top_course)
                print(valid_term)
                if valid_term:
                    # there is a valid term so for each possible prereqs options
                    # replace the top course being considered and add it to state_stack
                    operated_state.pop()
                    top_course_prereqs = course_descriptions[top_course].prereqs
                    tuple_stack.pop()
                    if top_course_prereqs:
                        for prereqs in top_course_prereqs:
                            state_add = operated_state.copy()
                            state_add += list(prereqs)
                            operator_add = Operator(prereqs, top_course, valid_term,
                                                    course_descriptions[top_course].credits)
                            final_operator_stack.append(operator_add)
                            tuple_stack.append((state_add, final_operator_stack))
                    else:
                        state_add = operated_state.copy()
                        operator_add = Operator((), top_course, valid_term, course_descriptions[top_course].credits)
                        final_operator_stack.append(operator_add)
                        tuple_stack.append((state_add, final_operator_stack))

                else:
                    # no valid option so pop the state from the state_stack; leads to the next possible
                    # option for a prereq completion
                    tuple_stack.pop()
        else:
            # remove if course already fulfilled by initial state
            operated_state.pop()
        # take the top tuple
        top_tuple = tuple_stack[len(tuple_stack) - 1] if len(tuple_stack) != 0 else ()
        # take the first state
        operated_state = []
        if top_tuple:
            operated_state = top_tuple[0] if len(top_tuple[0]) != 0 else []

    """
    keep a list of scheduled courses
    keep a stack of operators
    keep a stack of states
        
    every iteration
        take the top state from state_stack
            take the top condition from operated_state
                create an operator (latest term) if the condition is not in the initial state; otherwise, "remove" the
                course that can be found in the initial state (this would differentiate from the initial state equality
                to end the regression scheduler while loop, moving to an empty frontier requirement)
                    latest term is dependent on maximum credit hours
                    moves behind higher req (determined by looking through prereqs of scheduled terms going forwards 
                    freshman year fall; the course must fall behind the first instance of a higher requirement)
                        if the course finds itself before a higher requirement, it is placed in that term again
                        if the course is repeated after the first occurrence of a higher requirement, it should be
                        removed and inserted in the valid location
                        if no higher requirement is found through the scheduled courses list, simply place at latest
                        (Senior Spring)
                if no valid term exists, pop the state and try the next state (next option from a disjunction)
                    need to clear operator stack and scheduled courses
                        per operator,  
    
    match every state with an operator stack

    in the case that a course reappears as part of the prereqs for another course,
    identify the earliest point in which that prereq must occur and delete other instances
    not a concern until a prereq that has been scheduled reappears later
    """

def scheduled_term (course_descriptions, scheduled_course, operator_schedule):
    schedule_hours = generate_schedule_hours(operator_schedule)
    # first check for prereq constraints
    for term in operator_schedule:
        for operator in term:
            # course already scheduled in earliest necessary term
            if operator.EFF == scheduled_course:
                return apply_max_hours(course_descriptions[scheduled_course], schedule_hours, operator_schedule.index(term))
            else:
                for prereq in operator.PRE:
                    if prereq == scheduled_course:
                        if is_higher_requirement(operator.EFF):
                            return Term.initFromTermNo(operator_schedule.index(term)+1)
                        else:
                            if operator_schedule.index(term) > 0:
                                current_term = operator_schedule.index(term)
                                while current_term > 0:
                                    if schedule_hours[current_term] + int(
                                            course_descriptions[scheduled_course].credits) <= 18:
                                        return Term.initFromTermNo(current_term)
                                    current_term -= 1
                                return None
                            else:
                                return None
    current_term = MAX_NUMBER_OF_TERMS - 1
    while current_term > 0:
        if schedule_hours[current_term] + int(course_descriptions[scheduled_course].credits) <= 18:
            return Term.initFromTermNo(current_term+1)
        current_term -= 1
    return None

def in_schedule (operator_schedule, course):
    for term in operator_schedule:
        for operator in term:
            # course already scheduled in earliest necessary term
            if operator.EFF == course:
                return operator.ScheduledTerm
    return None

def apply_max_hours (course_description, schedule_hours, current_term):
    while current_term > 0:
        if schedule_hours[current_term] + int(course_description.credits) <= 18:
            return Term.initFromTermNo(current_term+1)
        current_term -= 1
    return None

def generate_schedule_hours (schedule):
    schedule_hours = []
    for term in schedule:
        schedule_hours.append(0)
        for operator in term:
            schedule_hours[schedule.index(term)] += int(operator.credits)
    return schedule_hours

def generate_schedule (operator_stack):
    # list of 11 terms (lists) each containing scheduled course
    schedule = [[] for _ in range(MAX_NUMBER_OF_TERMS)]
    for operator in operator_stack:
        schedule[operator.ScheduledTerm.termNo - 1].append(operator.EFF)
    return schedule

def generate_operator_schedule (operator_stack):
    # list of 11 terms (lists) each containing scheduled course
    schedule = [[] for _ in range(MAX_NUMBER_OF_TERMS)]
    for operator in operator_stack:
        schedule[operator.ScheduledTerm.termNo-1].append(operator)
    return schedule

def is_higher_requirement (course):
    return not course[1].isnumeric()

def state_init (course_descriptions, goal_conditions):
    """
    Creates a stack of stacks of composed of prerequisites for the goal conditions.
    :param course_descriptions: course catalog dictionary
    :param goal_conditions: courses that must be included in the generated schedule
    :return: stack with prerequisites to goal_conditions appended
    """
    tuple_stack = []
    for goal in goal_conditions:
        # for each possible (disjunction) set of prereqs
        for prereqs in course_descriptions[goal].prereqs:
            state_instance = goal_conditions.copy()
            state_instance.remove(goal)
            state_instance += list(prereqs)
            operator = Operator(prereqs, goal, Term.initFromTermNo(MAX_NUMBER_OF_TERMS),
                                course_descriptions[goal].credits)
            operator_state_tuple = state_instance, [operator]
            tuple_stack.append(operator_state_tuple)
    return tuple_stack

def main(argv):
    test = course_dictionary.create_course_dict()
    course_scheduler(test, [('CS', 'major'), ('CS', '4269')], [])

if __name__ == "__main__":
    main(sys.argv)