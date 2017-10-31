"""
Name: William Ju
Help Declarations: Used constants and classes given via the autograder.

The course_scheduler function is a two part heuristic depth first regression planner. The function's primary
operation is the generation and exploration of state paths. The states are represented as a conjunction of
courses that must be fulfilled for the path to succeed. These states are stored as a stack to allow for natural
depth-first search to occur. The primary loop of the scheduler ends once the current state is empty. This can
occur either by the popping of all possible states, meaning that all paths were exhausted without a valid solution,
or by expanding all the states to the point of no prerequisites. This should eventually end with an empty current
state. An operator stack is associated with each state. This stack can be used to generate the course schedule
and is a representation of the schedule at a current state. If a state is popped, its associated operator stack
is also removed. States and operator stacks are linked as tuples within a tuple stack. The goal conditions and
operator stack are initialized before running through the primary loop. The initial state removes all instances of
contained courses in the current state as these are not rescheduled. The primary loop expands the top course of
the state stack and adds all possible paths as determined by the disjunction of prerequisites. Once the schedule
finishes with a valid schedule, the second part of filling the schedule to fulfill the minimum credit hours
requirement occurs. The schedule is then sorted by term order and by alphabetical order before being returned.
Currently the scheduler counts a singular course multiple times as fulfilling elective courses. This will have to
be improved in the next submission.

The course scheduler utilizes a heuristic aiming to minimize the number of potential prerequisites and the number
of prerequisite layers. This is primarily done by taking the front value of the course designation (4 of 4260)
which represents a general measure of prerequisite layers and summing each front value with all prerequisites of
a disjunction. This sum provides a general idea of the required prerequisites necessary to completely fulfill the
considered course. We therefore first consider the prerequisite set that holds the smallest sum value to try to
minimize having to consider other potential paths (higher chance of path success).
"""

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


def course_scheduler(course_descriptions, goal_conditions, initial_state):
    """

    :param course_descriptions:
    :param goal_conditions:
    :param initial_state:
    :return:
    """
    tuple_stack = state_init(course_descriptions, goal_conditions, initial_state)
    final_operator_stack = []
    # take the top tuple
    top_tuple = tuple_stack[len(tuple_stack) - 1] if len(tuple_stack) != 0 else ()
    # take the first state
    operated_state = []
    if top_tuple:
        operated_state = top_tuple[0] if len(top_tuple[0]) != 0 else []
        final_operator_stack = top_tuple[1]
    # check if stack of states is empty (tried all options)
    while operated_state:
        # get the top course of the top state
        top_course = operated_state[len(operated_state) - 1]
        # check if the top course exists in the initial state
        if not initial_state.count(top_course):
            # get a valid term for the top course
            operator_schedule = generate_operator_schedule(final_operator_stack)
            scheduled = in_schedule(operator_schedule, top_course)
            if scheduled:
                for operator in final_operator_stack:
                    if operator.EFF == top_course:
                        final_operator_stack.remove(operator)
                operator_schedule = generate_operator_schedule(final_operator_stack)
            valid_term = scheduled_term(course_descriptions, top_course, operator_schedule)
            if valid_term:
                # there is a valid term so for each possible prereqs options
                # replace the top course being considered and add it to state_stack
                operated_state_copy = operated_state.copy()
                operated_state_copy.pop()
                top_course_prereqs = course_descriptions[top_course].prereqs
                tuple_stack.pop()
                if top_course_prereqs:
                    tuple_stack = prereq_heuristic(course_descriptions, tuple_stack, final_operator_stack,
                                                   operated_state_copy, top_course_prereqs, top_course, valid_term)
                else:
                    state_add = operated_state_copy.copy()
                    operator_add = Operator((), top_course, valid_term, course_descriptions[top_course].credits)
                    new_operator_stack = final_operator_stack.copy()
                    new_operator_stack.append(operator_add)
                    tuple_stack.append((state_add, new_operator_stack))

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
            final_operator_stack = top_tuple[1]
    if top_tuple:
        regression_schedule_hours = generate_schedule_hours(generate_operator_schedule(final_operator_stack))
        final_operator_stack = fill_terms(course_descriptions, regression_schedule_hours, final_operator_stack)
    return generate_scheduler_output(final_operator_stack)


def prereq_heuristic(course_descriptions, tuple_stack, operator_stack, state, prerequisites, course, term):
    """

    :param course_descriptions:
    :param tuple_stack:
    :param operator_stack:
    :param state:
    :param prerequisites:
    :param course:
    :param term:
    :return:
    """
    unordered_heuristic_prereqs = []
    for prereqs in prerequisites:
        heuristic_sum = 0
        for course_tuple in prereqs:
            if not is_higher_requirement((course_tuple[0], course_tuple[1])):
                course_designation_top_value = int(course_tuple[1][0])
                heuristic_sum += course_designation_top_value
        unordered_heuristic_prereqs.append((heuristic_sum, prereqs))
    reverse_ordered_heuristic_prereqs = reversed(sorted(unordered_heuristic_prereqs))
    for heuristic_tuple in reverse_ordered_heuristic_prereqs:
        heuristic_prereqs = heuristic_tuple[1]
        state_add = state.copy()
        state_add += list(heuristic_prereqs)
        operator_add = Operator(heuristic_prereqs, course, term,
                                course_descriptions[course].credits)
        new_operator_stack = operator_stack.copy()
        new_operator_stack.append(operator_add)
        tuple_stack.append((state_add, new_operator_stack))
    return tuple_stack


def fill_terms(course_descriptions, schedule_hours, operator_stack):
    """

    :param course_descriptions:
    :param schedule_hours:
    :param operator_stack:
    :return:
    """
    course_list = generate_course_list(operator_stack)
    for idx in range(len(schedule_hours)):
        min_credits = MIN_CREDITS_PER_SUMMER_TERM if (idx + 1) % 3 == 0 else MIN_CREDITS_PER_NON_SUMMER_TERM
        max_credits = MAX_CREDITS_PER_SUMMER_TERM if (idx + 1) % 3 == 0 else MAX_CREDITS_PER_NON_SUMMER_TERM
        if schedule_hours[idx] > 0:
            while schedule_hours[idx] < min_credits:
                for course in course_descriptions:
                    course_description = course_descriptions[course]
                    if not course_list.count(course) and course_description.prereqs == () \
                            and schedule_hours[idx] + int(course_description.credits) <= max_credits:
                        operator_add = Operator(course_description.prereqs, (course.program, course.designation),
                                                Term.initFromTermNo(idx + 1), course_description.credits)
                        operator_stack.append(operator_add)
                        course_list.append(course)
                        schedule_hours[idx] += int(course_description.credits)
                        break
    return operator_stack


def generate_scheduler_output(operator_stack):
    """

    :param operator_stack:
    :return:
    """
    sorted_dictionary = {}
    unsorted_schedule = generate_operator_schedule(operator_stack)
    for term in unsorted_schedule:
        sorted_term = sorted(term)
        for operator in sorted_term:
            course_key = Course(operator.EFF[0], operator.EFF[1])
            course_value = CourseInfo(operator.credits,
                                      (operator.ScheduledTerm.semester.name,
                                       operator.ScheduledTerm.year.name), operator.PRE)
            sorted_dictionary[course_key] = course_value
    return sorted_dictionary


def state_init(course_descriptions, goal_conditions, initial_state):
    """

    :param course_descriptions:
    :param goal_conditions:
    :param initial_state:
    :return:
    """
    tuple_stack = []
    for goal in goal_conditions:
        # for each possible (disjunction) set of prereqs
        if not initial_state.count(goal):
            if course_descriptions[goal].prereqs:
                for prereqs in course_descriptions[goal].prereqs:
                    state_instance = goal_conditions.copy()
                    state_instance.remove(goal)
                    state_instance += list(prereqs)
                    operator = Operator(prereqs, goal, Term.initFromTermNo(MAX_NUMBER_OF_TERMS),
                                        course_descriptions[goal].credits)
                    operator_state_tuple = state_instance, [operator]
                    tuple_stack.append(operator_state_tuple)
            else:
                state_instance = goal_conditions.copy()
                state_instance.remove(goal)
                operator = Operator((), goal, Term.initFromTermNo(MAX_NUMBER_OF_TERMS),
                                    course_descriptions[goal].credits)
                operator_state_tuple = state_instance, [operator]
                tuple_stack.append(operator_state_tuple)
    return tuple_stack


def scheduled_term(course_descriptions, scheduled_course, operator_schedule):
    """

    :param course_descriptions:
    :param scheduled_course:
    :param operator_schedule:
    :return:
    """
    schedule_hours = generate_schedule_hours(operator_schedule)
    # first check for prereq constraints
    for term in operator_schedule:
        for operator in term:
            for prereq in operator.PRE:
                if prereq == scheduled_course:
                    if is_higher_requirement(operator.EFF):
                        constrained_term = apply_constraints(course_descriptions[scheduled_course],
                                                             schedule_hours, operator_schedule.index(term))
                        if constrained_term:
                            return Term.initFromTermNo(constrained_term)
                        else:
                            return None
                    else:
                        constrained_term = apply_constraints(course_descriptions[scheduled_course],
                                                             schedule_hours, operator_schedule.index(term) - 1)
                        if constrained_term:
                            return Term.initFromTermNo(constrained_term)
                        else:
                            return None
    # if no prereq constraint apply, find the first non-18+ term
    current_term = MAX_NUMBER_OF_TERMS - 1
    constrained_term = apply_constraints(course_descriptions[scheduled_course],
                                         schedule_hours, current_term)
    if constrained_term:
        return Term.initFromTermNo(constrained_term)
    else:
        return None


def apply_constraints(course_description, schedule_hours, current_term):
    """

    :param course_description:
    :param schedule_hours:
    :param current_term:
    :return:
    """
    while current_term >= 0:
        max_credits = MAX_CREDITS_PER_SUMMER_TERM if (current_term + 1) % 3 == 0 else MAX_CREDITS_PER_NON_SUMMER_TERM
        if schedule_hours[current_term] + int(course_description.credits) <= max_credits:
            for available_term in course_description.terms:
                if Term.initFromTermNo(current_term + 1).semester.name == available_term:
                    return current_term + 1
        current_term -= 1
    return None


def is_higher_requirement(course):
    """

    :param course:
    :return:
    """
    return not course[1].isnumeric()


def in_schedule(operator_schedule, course):
    """

    :param operator_schedule:
    :param course:
    :return:
    """
    for term in operator_schedule:
        for operator in term:
            # course already scheduled in earliest necessary term
            if operator.EFF == course:
                return operator.ScheduledTerm
    return None


def generate_schedule(operator_stack):
    """

    :param operator_stack:
    :return:
    """
    # list of 11 terms (lists) each containing scheduled course
    schedule = [[] for _ in range(MAX_NUMBER_OF_TERMS)]
    for operator in operator_stack:
        schedule[operator.ScheduledTerm.termNo - 1].append(operator.EFF)
    return schedule


def generate_operator_schedule(operator_stack):
    """

    :param operator_stack:
    :return:
    """
    # list of 11 terms (lists) each containing scheduled course
    schedule = [[] for _ in range(MAX_NUMBER_OF_TERMS)]
    for operator in operator_stack:
        schedule[operator.ScheduledTerm.termNo - 1].append(operator)
    return schedule


def generate_schedule_hours(schedule):
    """

    :param schedule:
    :return:
    """
    schedule_hours = []
    for term in schedule:
        schedule_hours.append(0)
        for operator in term:
            schedule_hours[schedule.index(term)] += int(operator.credits)
    return schedule_hours


def generate_course_list(operator_stack):
    """

    :param operator_stack:
    :return:
    """
    course_list = []
    for operator in operator_stack:
        course_list.append(operator.EFF)
    return course_list
