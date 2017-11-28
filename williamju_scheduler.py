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
be improved in the next submission. This scheduler includes summer terms.

The course scheduler utilizes a heuristic aiming to minimize the number of potential prerequisites and the number
of prerequisite layers. This is primarily done by taking the front value of the course designation (4 of 4260)
which represents a general measure of prerequisite layers and summing each front value with all prerequisites of
a disjunction. This sum provides a general idea of the required prerequisites necessary to completely fulfill the
considered course. We therefore first consider the prerequisite set that holds the smallest sum value to try to
minimize having to consider other potential paths (higher chance of path success).

Currently the scheduler has had little trouble constructing paths for conditions in which I believed a schedule to
exist. The project specification was largely adhered to; the operator format did not use a tuple for the PRE, EFF.

1. Goal: [('CS', '1101')] Initial: [('CS', '1101')]

Purpose: Scheduling course already in initial state
Valid plan found: Empty dictionary
Wait time estimate: ~1 second

2. Goal: [('CS', '1101')] Initial: []

Purpose: Scheduling single course, fill terms test
Valid plan found: Yes
Wait time estimate: ~1 second

3. Goal: [('CS', '2231'), ('CS', '3251'), ('CS', 'statsprobability')]
   Initial: [('MATH', '2810'), ('MATH', '2820'), ('MATH', '3640')]

Purpose: Scheduling with higher requirement fulfilled by initial state
Valid plan found: Yes
Wait time estimate: ~1 second

4. Goal: [('CS', 'major'), ('CS', '2201')] Initial: []

Purpose: Course overlap scheduling
Valid plan found: Yes
Wait time estimate: < 2 seconds

5. Goal: [('CS', 'major'), ('ANTH', '4345'), ('ARTS', '3600'), ('BME', '4500'),
                ('BUS', '2300'), ('CE', '3705'), ('LAT', '3140'), ('JAPN', '3891')]
   Initial: []

Purpose: Improbable conditions scheduling
Valid plan found: No
Wait time estimate: 10+ minutes

6. Goal: [('CS', 'major'), ('JAPN', '3891')] Initial: [('CS', '1101'), ('JAPN', '1101')]

Purpose: Somewhat difficult scheduling
Valid plan found: Yes
Wait time estimate: < 2 seconds

7. Goal: [] Initial: []

Purpose: Empty conditions
Valid plan found: Yes
Wait time estimate: ~1 second

8. Goal: [('ANTH', '4345'), ('ARTS', '3600'), ('BME', '4500'),
                ('BUS', '2300'), ('CE', '3705'), ('LAT', '3140'), ('JAPN', '3891')]
   Initial: []

Purpose: Relatively difficult scheduling
Valid plan found: Yes
Wait time estimate: < 2 seconds
"""

from collections import namedtuple
from enum import IntEnum

SUMMER_TERMS = False
NUMBER_OF_SEMESTERS = 3 if SUMMER_TERMS else 2
MAX_NUMBER_OF_TERMS = 11 if SUMMER_TERMS else 8
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
        self.termNo = int(yearNo) * NUMBER_OF_SEMESTERS + int(semesterNo)

    # Basically a second constructor
    @classmethod
    def initFromTermNo(clazz, termNo):
        # intentional integer division
        yearNo = int(int(termNo - 1) / int(NUMBER_OF_SEMESTERS))
        semesterNo = termNo - (NUMBER_OF_SEMESTERS * yearNo)
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
    Holds the primary search loop and builds the state and operator stack while searching
    for the goal state that fulfills all goal conditions. Initializes start with state_init,
    finds a valid term for the considered course, then calls fill term function to fulfill
    minimum credit requirements. Then calls output creation function.
    :param course_descriptions: dictionary of offered Vanderbilt courses and related information
    :param goal_conditions: list of courses required in a valid schedule
    :param initial_state: list of courses already fulfilled, not scheduled
    :return: dictionary of scheduled courses for a solution or empty dictionary
    """
    # initialize the tuple stack (global variable)
    tuple_stack = state_init(course_descriptions, goal_conditions, initial_state)
    final_operator_stack = []
    # take the top tuple
    top_tuple = tuple_stack[len(tuple_stack) - 1] if len(tuple_stack) != 0 else ()
    operated_state = []
    # empty check
    if top_tuple:
        # take the first state
        operated_state = top_tuple[0] if len(top_tuple[0]) != 0 else []
        final_operator_stack = top_tuple[1]
    # check if stack of states is empty (tried all options), or complete
    while operated_state:
        # get the top course of the top state
        top_course = operated_state[len(operated_state) - 1]
        # check if the top course exists in the initial state
        if not initial_state.count(top_course):
            operator_schedule = generate_operator_schedule(final_operator_stack)
            # check if the course has already been scheduled
            scheduled = in_schedule(operator_schedule, top_course)
            if scheduled:
                for operator in final_operator_stack:
                    if operator.EFF == top_course:
                        # with the removal of the duplicate course, the insertion action
                        # will either place it in the same place or a new valid location
                        final_operator_stack.remove(operator)
                # update the operator_schedule for use
                operator_schedule = generate_operator_schedule(final_operator_stack)
            # get a valid term for the top course
            valid_term = scheduled_term(course_descriptions, top_course, operator_schedule)
            if valid_term:
                # data structure copies
                operated_state_copy = operated_state.copy()
                operated_state_copy.pop()
                top_course_prereqs = course_descriptions[top_course].prereqs
                # removal of the top state tuple to append expanded tuples
                tuple_stack.pop()
                # if there is prereq branching, we can apply a heuristic
                if top_course_prereqs:
                    tuple_stack = prereq_heuristic(course_descriptions, tuple_stack, final_operator_stack,
                                                   operated_state_copy, top_course_prereqs, top_course, valid_term)
                # otherwise simply add to valid location
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
            # update states and operator stack
            operated_state = top_tuple[0] if len(top_tuple[0]) != 0 else []
            final_operator_stack = top_tuple[1]
    if top_tuple:
        # generates the final operator stack after filling terms to minimum credit hours
        regression_schedule_hours = generate_schedule_hours(generate_operator_schedule(final_operator_stack))
        final_operator_stack = fill_terms(course_descriptions, regression_schedule_hours, final_operator_stack)
    # returns the dictionary output from the operator stack
    return generate_scheduler_output(final_operator_stack)


def prereq_heuristic(course_descriptions, tuple_stack, operator_stack, state, prerequisites, course, term):
    """
    Function that selectively expands a selected course into prerequisites. Calculates a heuristic value to
    potentially minimize prerequisite paths then creates a sorted list to expand the tuple_stack in optimized
    order.
    :param course_descriptions: course_descriptions: dictionary of offered Vanderbilt courses and related information
    :param tuple_stack: stack list data structure that holds tuples of the state and an associated operator stack
    :param operator_stack: stack list data structure that holds operators representing scheduled courses of the current state
    :param state: current state in the search being considered
    :param prerequisites: prerequisites in DNF form of the course being considered
    :param course: top course in the current state, being considered for expansion
    :param term: calculated valid term to be added in the operator
    :return: updated tuple_stack with heuristic course prereq expansion
    """
    unordered_heuristic_prereqs = []
    # per prereq disjunction
    for prereqs in prerequisites:
        # reset our sum
        heuristic_sum = 0
        # check that the course is not a higher requirement (no front number)
        for course_tuple in prereqs:
            if not is_higher_requirement((course_tuple[0], course_tuple[1])):
                # add front value
                course_designation_top_value = int(course_tuple[1][0])
                heuristic_sum += course_designation_top_value
        # add prereq with sum to be sorted by sum
        unordered_heuristic_prereqs.append((heuristic_sum, prereqs))
    # reverse to get lowest heuristic prereq to top of stack
    reverse_ordered_heuristic_prereqs = reversed(sorted(unordered_heuristic_prereqs))
    for heuristic_tuple in reverse_ordered_heuristic_prereqs:
        # create tuple and add to stack per prereq
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

    :param course_descriptions: course_descriptions: dictionary of offered Vanderbilt courses and related information
    :param schedule_hours: list of integers holding currently scheduled credit hours of each term associated by the index
    :param operator_stack: stack list data structure that holds operators representing scheduled courses of the current state
    :return: updated operator stack with filler operators to fulfill credit minimum
    """
    # generate course list to easily check if a considered course is already scheduled
    course_list = generate_course_list(operator_stack)
    for idx in range(len(schedule_hours)):
        # assign credit boundaries depending on term
        min_credits = MIN_CREDITS_PER_NON_SUMMER_TERM
        max_credits = MAX_CREDITS_PER_NON_SUMMER_TERM
        if SUMMER_TERMS:
            min_credits = MIN_CREDITS_PER_SUMMER_TERM if (idx + 1) % NUMBER_OF_SEMESTERS == 0 \
                else MIN_CREDITS_PER_NON_SUMMER_TERM
            max_credits = MAX_CREDITS_PER_SUMMER_TERM if (idx + 1) % NUMBER_OF_SEMESTERS == 0 \
                else MAX_CREDITS_PER_NON_SUMMER_TERM
        if schedule_hours[idx] > 0:
            # continue to add course operator while not fulfilling constraint
            while schedule_hours[idx] < min_credits:
                for course in course_descriptions:
                    course_description = course_descriptions[course]
                    if not course_list.count(course) and course_description.prereqs == () \
                            and schedule_hours[idx] + int(course_description.credits) <= max_credits \
                            and course_description.terms.count(Term.initFromTermNo(idx + 1).semester.name):
                        operator_add = Operator(course_description.prereqs, (course.program, course.designation),
                                                Term.initFromTermNo(idx + 1), course_description.credits)
                        operator_stack.append(operator_add)
                        course_list.append(course)
                        schedule_hours[idx] += int(course_description.credits)
                        break
    return operator_stack


def generate_scheduler_output(operator_stack):
    """
    Takes the final operator stack, orders by term then by alphabet.
    :param operator_stack: stack list data structure that holds operators representing scheduled courses of the current state
    :return: solution dictionary sorted by term and alphabetically, includes prereqs
    """
    sorted_dictionary = {}
    # generate an operator schedule to organize by term
    unsorted_schedule = generate_operator_schedule(operator_stack)
    for term in unsorted_schedule:
        # sort by alphabetical order
        sorted_term = sorted(term)
        # move to dictionary format
        for operator in sorted_term:
            course_key = Course(operator.EFF[0], operator.EFF[1])
            course_value = CourseInfo(operator.credits,
                                      (operator.ScheduledTerm.semester.name,
                                       operator.ScheduledTerm.year.name), operator.PRE)
            sorted_dictionary[course_key] = course_value
    return sorted_dictionary


def state_init(course_descriptions, goal_conditions, initial_state):
    """
    Initializes the goal conditions, operator stack to a tuple appened into a tuple stack. Initialization advances
    the state by one step.
    :param course_descriptions: course_descriptions: dictionary of offered Vanderbilt courses and related information
    :param goal_conditions: list of courses required in a valid schedule
    :param initial_state: list of courses already fulfilled, not scheduled
    :return: tuple_stack with the first top course expanded in the top state and the first operator added to the operator stack
    """
    tuple_stack = []
    # per goal course
    for goal in goal_conditions:
        # check if in initial state
        if not initial_state.count(goal):
            if course_descriptions[goal].prereqs:
                # per prereq add a tuple instance with appropriate operator stack
                for prereqs in course_descriptions[goal].prereqs:
                    state_instance = goal_conditions.copy()
                    state_instance.remove(goal)
                    state_instance += list(prereqs)
                    operator = Operator(prereqs, goal, Term.initFromTermNo(MAX_NUMBER_OF_TERMS),
                                        course_descriptions[goal].credits)
                    operator_state_tuple = state_instance, [operator]
                    tuple_stack.append(operator_state_tuple)
            else:
                # since this is the first step, we know we can schedule at the latest position
                state_instance = goal_conditions.copy()
                state_instance.remove(goal)
                operator = Operator((), goal, Term.initFromTermNo(MAX_NUMBER_OF_TERMS),
                                    course_descriptions[goal].credits)
                operator_state_tuple = state_instance, [operator]
                tuple_stack.append(operator_state_tuple)
    return tuple_stack


def scheduled_term(course_descriptions, scheduled_course, operator_schedule):
    """
    Finds the latest valid term for a course first by identifying prereq positioning then applying a credit hour
    constraint (via function)
    :param course_descriptions: course_descriptions: dictionary of offered Vanderbilt courses and related information
    :param scheduled_course: course being considered for valid term
    :param operator_schedule: list of list of operators, each list representing a term
    :return: the valid term right behind a higher requirement or None if nonexistent
    """
    schedule_hours = generate_schedule_hours(operator_schedule)
    # first check for prereq constraints
    for term in operator_schedule:
        for operator in term:
            for prereq in operator.PRE:
                if prereq == scheduled_course:
                    # a course that is a prereq of a higher requirement can be scheduled in the same term
                    # as the higher requirement
                    if is_higher_requirement(operator.EFF):
                        # get final term after applying credit hour constraints
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
    From the current latest term, this function applied the maximum credit hour constraint to find a valid term
    based on the current state of scheduled hours.
    :param course_description: course_descriptions: dictionary of offered Vanderbilt courses and related information
    :param schedule_hours: list of integers holding currently scheduled credit hours of each term associated by the index
    :param current_term: course being constrained to hour requirements
    :return: first valid term with credit hour constraints applied
    """
    # loop until out of valid terms to place
    while current_term >= 0:
        # credit hour boundary dependent on term (Summer or not)
        max_credits = MAX_CREDITS_PER_NON_SUMMER_TERM
        if SUMMER_TERMS:
            max_credits = MAX_CREDITS_PER_SUMMER_TERM if (current_term + 1) % NUMBER_OF_SEMESTERS == 0 \
                else MAX_CREDITS_PER_NON_SUMMER_TERM
        # see if addition of course violates limit, then move to next term
        if schedule_hours[current_term] + int(course_description.credits) <= max_credits:
            for available_term in course_description.terms:
                if Term.initFromTermNo(current_term + 1).semester.name == available_term:
                    return current_term + 1
        current_term -= 1
    return None


def is_higher_requirement(course):
    """
    Checks if the course parameter is a higher requirement type.
    :param course: course being checked if higher requirement
    :return: boolean whether course is a higher requirement type
    """
    return not course[1].isnumeric()


def in_schedule(operator_schedule, course):
    """
    Checks if the course parameter is found in the current schedule.
    :param operator_schedule: list of list of operators, each list representing a term
    :param course: course being checked if already in the schedule
    :return: boolean whether course is already scheduled
    """
    for term in operator_schedule:
        for operator in term:
            # course already scheduled in earliest necessary term
            if operator.EFF == course:
                return operator.ScheduledTerm
    return None


def generate_schedule(operator_stack):
    """
    Constructs a list of lists of course tuples. Each term is ordered by the index of the top list.
    :param operator_stack: stack list data structure that holds operators representing scheduled courses of the current state
    :return: schedule (list of lists of courses) of regular tuple courses
    """
    # list of 11 terms (lists) each containing scheduled course
    schedule = [[] for _ in range(MAX_NUMBER_OF_TERMS)]
    for operator in operator_stack:
        schedule[operator.ScheduledTerm.termNo - 1].append(operator.EFF)
    return schedule


def generate_operator_schedule(operator_stack):
    """
    Constructs a list of lists of operators for scheduled courses. Each term is ordered by the index of the top list.
    :param operator_stack: stack list data structure that holds operators representing scheduled courses of the current state
    :return: schedule (list of lists of courses) of operators
    """
    # list of 11 terms (lists) each containing scheduled course
    schedule = [[] for _ in range(MAX_NUMBER_OF_TERMS)]
    for operator in operator_stack:
        schedule[operator.ScheduledTerm.termNo - 1].append(operator)
    return schedule


def generate_schedule_hours(schedule):
    """
    Constructs a list of integers holding the total scheduled credit hours per term, associated by index.
    :param schedule:
    :return: schedule (list of integers) of scheduled total credit hours
    """
    schedule_hours = []
    for term in schedule:
        schedule_hours.append(0)
        for operator in term:
            schedule_hours[schedule.index(term)] += int(operator.credits)
    return schedule_hours


def generate_course_list(operator_stack):
    """
    Instead of a list of lists as with regular schedules, this function simply generates a list of currently scheduled
    courses (in operator form).
    :param operator_stack: stack list data structure that holds operators representing scheduled courses of the current state
    :return: plain list of courses from operator stack
    """
    course_list = []
    for operator in operator_stack:
        course_list.append(operator.EFF)
    return course_list

"""
1.

{}

2.

{Course(program='AADS', designation='1001') CourseInfo(credits='1', terms=('Spring', 'Senior'), prereqs=())
Course(program='AADS', designation='1010') CourseInfo(credits='3', terms=('Spring', 'Senior'), prereqs=())
Course(program='AADS', designation='1506') CourseInfo(credits='3', terms=('Spring', 'Senior'), prereqs=())
Course(program='AADS', designation='3850') CourseInfo(credits=3, terms=('Spring', 'Senior'), prereqs=())
Course(program='CS', designation='1101') CourseInfo(credits='3', terms=('Spring', 'Senior'), prereqs=())}

3.

{Course(program='CS', designation='1101') CourseInfo(credits='3', terms=('Summer', 'Junior'), prereqs=())
Course(program='AADS', designation='1001') CourseInfo(credits='1', terms=('Fall', 'Senior'), prereqs=())
Course(program='AADS', designation='1010') CourseInfo(credits='3', terms=('Fall', 'Senior'), prereqs=())
Course(program='AADS', designation='1506') CourseInfo(credits='3', terms=('Fall', 'Senior'), prereqs=())
Course(program='AADS', designation='3850') CourseInfo(credits=3, terms=('Fall', 'Senior'), prereqs=())
Course(program='CS', designation='2201') CourseInfo(credits='3', terms=('Fall', 'Senior'), prereqs=(('CS', '1101'),))
Course(program='AADS', designation='1706') CourseInfo(credits='3', terms=('Spring', 'Senior'), prereqs=())
Course(program='AADS', designation='2166') CourseInfo(credits='3', terms=('Spring', 'Senior'), prereqs=())
Course(program='CS', designation='2231') CourseInfo(credits='3', terms=('Spring', 'Senior'), prereqs=(('CS', '2201'),))
Course(program='CS', designation='3251') CourseInfo(credits='3', terms=('Spring', 'Senior'), prereqs=(('CS', '2201'),))
Course(program='CS', designation='statsprobability') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('MATH', '3640'),))}

4.

{Course(program='AADS', designation='1001') CourseInfo(credits='1', terms=('Fall', 'Frosh'), prereqs=())
Course(program='AADS', designation='1010') CourseInfo(credits='3', terms=('Fall', 'Frosh'), prereqs=())
Course(program='AADS', designation='1506') CourseInfo(credits='3', terms=('Fall', 'Frosh'), prereqs=())
Course(program='AADS', designation='3850') CourseInfo(credits=3, terms=('Fall', 'Frosh'), prereqs=())
Course(program='MATH', designation='1200') CourseInfo(credits='3', terms=('Fall', 'Frosh'), prereqs=())
Course(program='AADS', designation='1706') CourseInfo(credits='3', terms=('Spring', 'Frosh'), prereqs=())
Course(program='AADS', designation='2166') CourseInfo(credits='3', terms=('Spring', 'Frosh'), prereqs=())
Course(program='AADS', designation='2168') CourseInfo(credits='3', terms=('Spring', 'Frosh'), prereqs=())
Course(program='MATH', designation='1201') CourseInfo(credits='3', terms=('Spring', 'Frosh'), prereqs=(('MATH', '1200'),))
Course(program='MATH', designation='1301') CourseInfo(credits='4', terms=('Summer', 'Frosh'), prereqs=(('MATH', '1201'),))
Course(program='AADS', designation='2178') CourseInfo(credits='3', terms=('Fall', 'Sophomore'), prereqs=())
Course(program='AADS', designation='2214') CourseInfo(credits='3', terms=('Fall', 'Sophomore'), prereqs=())
Course(program='CS', designation='1101') CourseInfo(credits='3', terms=('Fall', 'Sophomore'), prereqs=())
Course(program='MATH', designation='2300') CourseInfo(credits='3', terms=('Fall', 'Sophomore'), prereqs=(('MATH', '1301'),))
Course(program='ARTS', designation='1102') CourseInfo(credits='3', terms=('Spring', 'Sophomore'), prereqs=())
Course(program='BSCI', designation='1100') CourseInfo(credits='3', terms=('Spring', 'Sophomore'), prereqs=())
Course(program='MATH', designation='1300') CourseInfo(credits='4', terms=('Spring', 'Sophomore'), prereqs=())
Course(program='CS', designation='2201') CourseInfo(credits='3', terms=('Spring', 'Sophomore'), prereqs=(('CS', '1101'),))
Course(program='MATH', designation='2420') CourseInfo(credits='3', terms=('Spring', 'Sophomore'), prereqs=(('MATH', '2300'),))
Course(program='MATH', designation='2810') CourseInfo(credits='3', terms=('Summer', 'Sophomore'), prereqs=(('MATH', '2300'),))
Course(program='ES', designation='1401') CourseInfo(credits='1', terms=('Fall', 'Junior'), prereqs=())
Course(program='SOC', designation='3702') CourseInfo(credits='3', terms=('Fall', 'Junior'), prereqs=())
Course(program='ARTS', designation='2101') CourseInfo(credits='3', terms=('Fall', 'Junior'), prereqs=(('ARTS', '1102'),))
Course(program='CS', designation='2231') CourseInfo(credits='3', terms=('Fall', 'Junior'), prereqs=(('CS', '2201'),))
Course(program='CS', designation='3251') CourseInfo(credits='3', terms=('Fall', 'Junior'), prereqs=(('CS', '2201'),))
Course(program='MATH', designation='2410') CourseInfo(credits='3', terms=('Fall', 'Junior'), prereqs=(('MATH', '2300'),))
Course(program='ENGL', designation='1250W') CourseInfo(credits='3', terms=('Spring', 'Junior'), prereqs=())
Course(program='EUS', designation='2203') CourseInfo(credits='3', terms=('Spring', 'Junior'), prereqs=())
Course(program='CS', designation='3270') CourseInfo(credits='3', terms=('Spring', 'Junior'), prereqs=(('CS', '2231'),))
Course(program='CS', designation='3281') CourseInfo(credits='3', terms=('Spring', 'Junior'), prereqs=(('CS', '2231'), ('CS', '3251')))
Course(program='MATH', designation='2400') CourseInfo(credits='4', terms=('Spring', 'Junior'), prereqs=(('MATH', '2300'),))
Course(program='CS', designation='1103') CourseInfo(credits='3', terms=('Summer', 'Junior'), prereqs=())
Course(program='PSY', designation='1200') CourseInfo(credits='3', terms=('Summer', 'Junior'), prereqs=())
Course(program='CS', designation='2212') CourseInfo(credits='3', terms=('Fall', 'Senior'), prereqs=())
Course(program='EECE', designation='2116') CourseInfo(credits='3', terms=('Fall', 'Senior'), prereqs=())
Course(program='ES', designation='1402') CourseInfo(credits='1', terms=('Fall', 'Senior'), prereqs=())
Course(program='ES', designation='1403') CourseInfo(credits='1', terms=('Fall', 'Senior'), prereqs=())
Course(program='BME', designation='4900W') CourseInfo(credits='3', terms=('Fall', 'Senior'), prereqs=(('BME', '3100'),))
Course(program='BME', designation='3100') CourseInfo(credits='3', terms=('Fall', 'Senior'), prereqs=(('CS', '1103'),))
Course(program='CS', designation='3259') CourseInfo(credits='3', terms=('Fall', 'Senior'), prereqs=(('CS', '2201'), ('MATH', '2400')))
Course(program='CS', designation='4959') CourseInfo(credits='1', terms=('Fall', 'Senior'), prereqs=(('CS', '3281'),))
Course(program='AADS', designation='3104W') CourseInfo(credits='3', terms=('Spring', 'Senior'), prereqs=())
Course(program='AMER', designation='1002W') CourseInfo(credits='3', terms=('Spring', 'Senior'), prereqs=())
Course(program='BSCI', designation='1100L') CourseInfo(credits='1', terms=('Spring', 'Senior'), prereqs=())
Course(program='CS', designation='1151') CourseInfo(credits='3', terms=('Spring', 'Senior'), prereqs=())
Course(program='EECE', designation='2116L') CourseInfo(credits='1', terms=('Spring', 'Senior'), prereqs=())
Course(program='CS', designation='writingrequirement') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('AADS', '3104W'),))
Course(program='CS', designation='open1') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('AMER', '1002W'),))
Course(program='CS', designation='open2') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('AMER', '1002W'),))
Course(program='CS', designation='open3') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('AMER', '1002W'),))
Course(program='CS', designation='open4') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('AMER', '1002W'),))
Course(program='CS', designation='open5') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('AMER', '1002W'),))
Course(program='CS', designation='open6') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('AMER', '1002W'),))
Course(program='CS', designation='liberalother') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('ARTS', '1102'), ('ARTS', '2101')))
Course(program='CS', designation='techelectives1') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('BME', '4900W'),))
Course(program='CS', designation='techelectives2') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('BME', '4900W'),))
Course(program='CS', designation='scienceb') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('BSCI', '1100'),))
Course(program='CS', designation='sciencec') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('BSCI', '1100'),))
Course(program='CS', designation='sciencelab') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('BSCI', '1100'), ('BSCI', '1100L')))
Course(program='CS', designation='core') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('CS', '1101'), ('CS', '2201'), ('CS', '3251'), ('CS', '3270'), ('EECE', '2116'), ('EECE', '2116L'), ('CS', '2231'), ('CS', '3281'), ('CS', '2212'), ('CS', '3250')))
Course(program='CS', designation='3250') CourseInfo(credits='3', terms=('Spring', 'Senior'), prereqs=(('CS', '2201'), ('CS', '2212')))
Course(program='CS', designation='3252') CourseInfo(credits='3', terms=('Spring', 'Senior'), prereqs=(('CS', '2212'),))
Course(program='CS', designation='depthothera') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('CS', '3252'),))
Course(program='CS', designation='depthotherb') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('CS', '3252'),))
Course(program='CS', designation='depthotherc') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('CS', '3252'),))
Course(program='CS', designation='depthproject') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('CS', '3259'),))
Course(program='CS', designation='mathematics') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('CS', 'calculus'), ('CS', 'statsprobability'), ('CS', 'mathelective')))
Course(program='CS', designation='depth') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('CS', 'depthproject'), ('CS', 'depthothera'), ('CS', 'depthotherb'), ('CS', 'depthotherc')))
Course(program='CS', designation='liberalarts') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('CS', 'liberalhum'), ('CS', 'liberalsoc'), ('CS', 'liberalother')))
Course(program='CS', designation='major') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('CS', 'mathematics'), ('CS', 'sciencelab'), ('CS', 'scienceb'), ('CS', 'sciencec'), ('CS', 'esintro'), ('CS', 'liberalarts'), ('CS', 'core'), ('CS', 'depth'), ('CS', '4959'), ('CS', 'techelectives'), ('CS', '1151'), ('CS', 'openelectives'), ('CS', 'writingrequirement')))
Course(program='CS', designation='openelectives') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('CS', 'open1'), ('CS', 'open2'), ('CS', 'open3'), ('CS', 'open4'), ('CS', 'open5'), ('CS', 'open6')))
Course(program='CS', designation='techelectives') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('CS', 'techelectives1'), ('CS', 'techelectives2')))
Course(program='CS', designation='liberalhum') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('ENGL', '1250W'), ('EUS', '2203')))
Course(program='CS', designation='esintro') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('ES', '1401'), ('ES', '1402'), ('ES', '1403')))
Course(program='CS', designation='calculus') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('MATH', '1300'), ('MATH', '1301'), ('MATH', '2300'), ('MATH', '2410')))
Course(program='CS', designation='mathelective') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('MATH', '2420'),))
Course(program='CS', designation='statsprobability') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('MATH', '2810'),))
Course(program='CS', designation='liberalsoc') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('PSY', '1200'), ('SOC', '3702')))}

5.

{}

6.

{Course(program='AADS', designation='1001') CourseInfo(credits='1', terms=('Fall', 'Frosh'), prereqs=())
Course(program='AADS', designation='1010') CourseInfo(credits='3', terms=('Fall', 'Frosh'), prereqs=())
Course(program='AADS', designation='1506') CourseInfo(credits='3', terms=('Fall', 'Frosh'), prereqs=())
Course(program='AADS', designation='3850') CourseInfo(credits=3, terms=('Fall', 'Frosh'), prereqs=())
Course(program='MATH', designation='1300') CourseInfo(credits='4', terms=('Fall', 'Frosh'), prereqs=())
Course(program='AADS', designation='1706') CourseInfo(credits='3', terms=('Spring', 'Frosh'), prereqs=())
Course(program='JAPN', designation='1102') CourseInfo(credits='5', terms=('Spring', 'Frosh'), prereqs=(('JAPN', '1101'),))
Course(program='MATH', designation='1301') CourseInfo(credits='4', terms=('Spring', 'Frosh'), prereqs=(('MATH', '1300'),))
Course(program='BSCI', designation='1100') CourseInfo(credits='3', terms=('Summer', 'Frosh'), prereqs=())
Course(program='MATH', designation='2300') CourseInfo(credits='3', terms=('Summer', 'Frosh'), prereqs=(('MATH', '1301'),))
Course(program='ES', designation='1401') CourseInfo(credits='1', terms=('Fall', 'Sophomore'), prereqs=())
Course(program='ES', designation='1402') CourseInfo(credits='1', terms=('Fall', 'Sophomore'), prereqs=())
Course(program='MATH', designation='1200') CourseInfo(credits='3', terms=('Fall', 'Sophomore'), prereqs=())
Course(program='JAPN', designation='2201') CourseInfo(credits='5', terms=('Fall', 'Sophomore'), prereqs=(('JAPN', '1102'),))
Course(program='MATH', designation='2420') CourseInfo(credits='3', terms=('Fall', 'Sophomore'), prereqs=(('MATH', '2300'),))
Course(program='ARTS', designation='1102') CourseInfo(credits='3', terms=('Spring', 'Sophomore'), prereqs=())
Course(program='ENGL', designation='1250W') CourseInfo(credits='3', terms=('Spring', 'Sophomore'), prereqs=())
Course(program='CS', designation='2201') CourseInfo(credits='3', terms=('Spring', 'Sophomore'), prereqs=(('CS', '1101'),))
Course(program='JAPN', designation='2202') CourseInfo(credits='5', terms=('Spring', 'Sophomore'), prereqs=(('JAPN', '2201'),))
Course(program='MATH', designation='1201') CourseInfo(credits='3', terms=('Spring', 'Sophomore'), prereqs=(('MATH', '1200'),))
Course(program='MATH', designation='2810') CourseInfo(credits='3', terms=('Summer', 'Sophomore'), prereqs=(('MATH', '2300'),))
Course(program='SOC', designation='3702') CourseInfo(credits='3', terms=('Fall', 'Junior'), prereqs=())
Course(program='ARTS', designation='2101') CourseInfo(credits='3', terms=('Fall', 'Junior'), prereqs=(('ARTS', '1102'),))
Course(program='CS', designation='2231') CourseInfo(credits='3', terms=('Fall', 'Junior'), prereqs=(('CS', '2201'),))
Course(program='CS', designation='3251') CourseInfo(credits='3', terms=('Fall', 'Junior'), prereqs=(('CS', '2201'),))
Course(program='JAPN', designation='3301') CourseInfo(credits='3', terms=('Fall', 'Junior'), prereqs=(('JAPN', '2202'),))
Course(program='MATH', designation='2410') CourseInfo(credits='3', terms=('Fall', 'Junior'), prereqs=(('MATH', '2300'),))
Course(program='BSCI', designation='1100L') CourseInfo(credits='1', terms=('Spring', 'Junior'), prereqs=())
Course(program='EUS', designation='2203') CourseInfo(credits='3', terms=('Spring', 'Junior'), prereqs=())
Course(program='CS', designation='3270') CourseInfo(credits='3', terms=('Spring', 'Junior'), prereqs=(('CS', '2231'),))
Course(program='CS', designation='3281') CourseInfo(credits='3', terms=('Spring', 'Junior'), prereqs=(('CS', '2231'), ('CS', '3251')))
Course(program='JAPN', designation='3302') CourseInfo(credits='3', terms=('Spring', 'Junior'), prereqs=(('JAPN', '3301'),))
Course(program='MATH', designation='2400') CourseInfo(credits='4', terms=('Spring', 'Junior'), prereqs=(('MATH', '2300'),))
Course(program='CS', designation='1103') CourseInfo(credits='3', terms=('Summer', 'Junior'), prereqs=())
Course(program='PSY', designation='1200') CourseInfo(credits='3', terms=('Summer', 'Junior'), prereqs=())
Course(program='CS', designation='2212') CourseInfo(credits='3', terms=('Fall', 'Senior'), prereqs=())
Course(program='EECE', designation='2116') CourseInfo(credits='3', terms=('Fall', 'Senior'), prereqs=())
Course(program='EECE', designation='2116L') CourseInfo(credits='1', terms=('Fall', 'Senior'), prereqs=())
Course(program='ES', designation='1403') CourseInfo(credits='1', terms=('Fall', 'Senior'), prereqs=())
Course(program='BME', designation='4900W') CourseInfo(credits='3', terms=('Fall', 'Senior'), prereqs=(('BME', '3100'),))
Course(program='BME', designation='3100') CourseInfo(credits='3', terms=('Fall', 'Senior'), prereqs=(('CS', '1103'),))
Course(program='CS', designation='3259') CourseInfo(credits='3', terms=('Fall', 'Senior'), prereqs=(('CS', '2201'), ('MATH', '2400')))
Course(program='CS', designation='4959') CourseInfo(credits='1', terms=('Fall', 'Senior'), prereqs=(('CS', '3281'),))
Course(program='AADS', designation='3104W') CourseInfo(credits='3', terms=('Spring', 'Senior'), prereqs=())
Course(program='AMER', designation='1002W') CourseInfo(credits='3', terms=('Spring', 'Senior'), prereqs=())
Course(program='CS', designation='1151') CourseInfo(credits='3', terms=('Spring', 'Senior'), prereqs=())
Course(program='CS', designation='writingrequirement') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('AADS', '3104W'),))
Course(program='CS', designation='open1') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('AMER', '1002W'),))
Course(program='CS', designation='open2') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('AMER', '1002W'),))
Course(program='CS', designation='open3') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('AMER', '1002W'),))
Course(program='CS', designation='open4') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('AMER', '1002W'),))
Course(program='CS', designation='open5') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('AMER', '1002W'),))
Course(program='CS', designation='open6') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('AMER', '1002W'),))
Course(program='CS', designation='liberalother') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('ARTS', '1102'), ('ARTS', '2101')))
Course(program='CS', designation='techelectives1') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('BME', '4900W'),))
Course(program='CS', designation='techelectives2') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('BME', '4900W'),))
Course(program='CS', designation='scienceb') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('BSCI', '1100'),))
Course(program='CS', designation='sciencec') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('BSCI', '1100'),))
Course(program='CS', designation='sciencelab') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('BSCI', '1100'), ('BSCI', '1100L')))
Course(program='CS', designation='core') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('CS', '1101'), ('CS', '2201'), ('CS', '3251'), ('CS', '3270'), ('EECE', '2116'), ('EECE', '2116L'), ('CS', '2231'), ('CS', '3281'), ('CS', '2212'), ('CS', '3250')))
Course(program='CS', designation='3250') CourseInfo(credits='3', terms=('Spring', 'Senior'), prereqs=(('CS', '2201'), ('CS', '2212')))
Course(program='CS', designation='3252') CourseInfo(credits='3', terms=('Spring', 'Senior'), prereqs=(('CS', '2212'),))
Course(program='CS', designation='depthothera') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('CS', '3252'),))
Course(program='CS', designation='depthotherb') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('CS', '3252'),))
Course(program='CS', designation='depthotherc') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('CS', '3252'),))
Course(program='CS', designation='depthproject') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('CS', '3259'),))
Course(program='CS', designation='mathematics') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('CS', 'calculus'), ('CS', 'statsprobability'), ('CS', 'mathelective')))
Course(program='CS', designation='depth') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('CS', 'depthproject'), ('CS', 'depthothera'), ('CS', 'depthotherb'), ('CS', 'depthotherc')))
Course(program='CS', designation='liberalarts') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('CS', 'liberalhum'), ('CS', 'liberalsoc'), ('CS', 'liberalother')))
Course(program='CS', designation='major') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('CS', 'mathematics'), ('CS', 'sciencelab'), ('CS', 'scienceb'), ('CS', 'sciencec'), ('CS', 'esintro'), ('CS', 'liberalarts'), ('CS', 'core'), ('CS', 'depth'), ('CS', '4959'), ('CS', 'techelectives'), ('CS', '1151'), ('CS', 'openelectives'), ('CS', 'writingrequirement')))
Course(program='CS', designation='openelectives') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('CS', 'open1'), ('CS', 'open2'), ('CS', 'open3'), ('CS', 'open4'), ('CS', 'open5'), ('CS', 'open6')))
Course(program='CS', designation='techelectives') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('CS', 'techelectives1'), ('CS', 'techelectives2')))
Course(program='CS', designation='liberalhum') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('ENGL', '1250W'), ('EUS', '2203')))
Course(program='CS', designation='esintro') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('ES', '1401'), ('ES', '1402'), ('ES', '1403')))
Course(program='JAPN', designation='3891') CourseInfo(credits='3', terms=('Spring', 'Senior'), prereqs=(('JAPN', '3302'),))
Course(program='CS', designation='calculus') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('MATH', '1300'), ('MATH', '1301'), ('MATH', '2300'), ('MATH', '2410')))
Course(program='CS', designation='mathelective') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('MATH', '2420'),))
Course(program='CS', designation='statsprobability') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('MATH', '2810'),))
Course(program='CS', designation='liberalsoc') CourseInfo(credits='0', terms=('Spring', 'Senior'), prereqs=(('PSY', '1200'), ('SOC', '3702')))}

7.

{}

8.

{Course(program='AADS', designation='1001') CourseInfo(credits='1', terms=('Fall', 'Frosh'), prereqs=())
Course(program='AADS', designation='1010') CourseInfo(credits='3', terms=('Fall', 'Frosh'), prereqs=())
Course(program='AADS', designation='3850') CourseInfo(credits=3, terms=('Fall', 'Frosh'), prereqs=())
Course(program='JAPN', designation='1101') CourseInfo(credits='5', terms=('Fall', 'Frosh'), prereqs=())
Course(program='AADS', designation='1506') CourseInfo(credits='3', terms=('Spring', 'Frosh'), prereqs=())
Course(program='BSCI', designation='1100') CourseInfo(credits='3', terms=('Spring', 'Frosh'), prereqs=())
Course(program='MATH', designation='1200') CourseInfo(credits='3', terms=('Spring', 'Frosh'), prereqs=())
Course(program='JAPN', designation='1102') CourseInfo(credits='5', terms=('Spring', 'Frosh'), prereqs=(('JAPN', '1101'),))
Course(program='ARTS', designation='1102') CourseInfo(credits='3', terms=('Summer', 'Frosh'), prereqs=())
Course(program='CHEM', designation='1601') CourseInfo(credits='3', terms=('Summer', 'Frosh'), prereqs=())
Course(program='ARTS', designation='1600') CourseInfo(credits='3', terms=('Fall', 'Sophomore'), prereqs=(('ARTS', '1102'),))
Course(program='ANTH', designation='4345') CourseInfo(credits='3', terms=('Fall', 'Sophomore'), prereqs=(('BSCI', '1100'),))
Course(program='BSCI', designation='1510') CourseInfo(credits='3', terms=('Fall', 'Sophomore'), prereqs=(('CHEM', '1601'),))
Course(program='JAPN', designation='2201') CourseInfo(credits='5', terms=('Fall', 'Sophomore'), prereqs=(('JAPN', '1102'),))
Course(program='MATH', designation='1201') CourseInfo(credits='3', terms=('Fall', 'Sophomore'), prereqs=(('MATH', '1200'),))
Course(program='PHYS', designation='1601') CourseInfo(credits='3', terms=('Spring', 'Sophomore'), prereqs=())
Course(program='JAPN', designation='2202') CourseInfo(credits='5', terms=('Spring', 'Sophomore'), prereqs=(('JAPN', '2201'),))
Course(program='MATH', designation='1301') CourseInfo(credits='4', terms=('Spring', 'Sophomore'), prereqs=(('MATH', '1201'),))
Course(program='CS', designation='1103') CourseInfo(credits='3', terms=('Summer', 'Sophomore'), prereqs=())
Course(program='MATH', designation='2300') CourseInfo(credits='3', terms=('Summer', 'Sophomore'), prereqs=(('MATH', '1301'),))
Course(program='ECON', designation='1010') CourseInfo(credits='3', terms=('Fall', 'Junior'), prereqs=())
Course(program='MATH', designation='1100') CourseInfo(credits='4', terms=('Fall', 'Junior'), prereqs=())
Course(program='JAPN', designation='3301') CourseInfo(credits='3', terms=('Fall', 'Junior'), prereqs=(('JAPN', '2202'),))
Course(program='MATH', designation='2400') CourseInfo(credits='4', terms=('Fall', 'Junior'), prereqs=(('MATH', '2300'),))
Course(program='BME', designation='2100') CourseInfo(credits='3', terms=('Fall', 'Junior'), prereqs=(('PHYS', '1601'), ('MATH', '1301'), ('CS', '1103')))
Course(program='LAT', designation='2202') CourseInfo(credits='3', terms=('Spring', 'Junior'), prereqs=())
Course(program='ECON', designation='1020') CourseInfo(credits='3', terms=('Spring', 'Junior'), prereqs=(('ECON', '1010'),))
Course(program='JAPN', designation='3302') CourseInfo(credits='3', terms=('Spring', 'Junior'), prereqs=(('JAPN', '3301'),))
Course(program='ECON', designation='1500') CourseInfo(credits='3', terms=('Spring', 'Junior'), prereqs=(('MATH', '1100'),))
Course(program='MATH', designation='2420') CourseInfo(credits='3', terms=('Summer', 'Junior'), prereqs=(('MATH', '2300'),))
Course(program='ME', designation='2190') CourseInfo(credits='3', terms=('Summer', 'Junior'), prereqs=(('PHYS', '1601'),))
Course(program='PHYS', designation='1602') CourseInfo(credits='3', terms=('Fall', 'Senior'), prereqs=())
Course(program='ARTS', designation='2600') CourseInfo(credits='3', terms=('Fall', 'Senior'), prereqs=(('ARTS', '1600'),))
Course(program='BME', designation='3000') CourseInfo(credits='3', terms=('Fall', 'Senior'), prereqs=(('BME', '2100'), ('MATH', '2400')))
Course(program='BUS', designation='2300') CourseInfo(credits=3, terms=('Fall', 'Senior'), prereqs=(('ECON', '1020'), ('ECON', '1500')))
Course(program='LAT', designation='3140') CourseInfo(credits='3', terms=('Fall', 'Senior'), prereqs=(('LAT', '2202'),))
Course(program='CE', designation='3700') CourseInfo(credits='3', terms=('Fall', 'Senior'), prereqs=(('ME', '2190'), ('MATH', '2420')))
Course(program='ARTS', designation='3600') CourseInfo(credits='3', terms=('Spring', 'Senior'), prereqs=(('ARTS', '2600'),))
Course(program='BME', designation='4500') CourseInfo(credits='3', terms=('Spring', 'Senior'), prereqs=(('BSCI', '1510'), ('BME', '3000')))
Course(program='CE', designation='3705') CourseInfo(credits='3', terms=('Spring', 'Senior'), prereqs=(('CHEM', '1601'), ('PHYS', '1601'), ('PHYS', '1602'), ('MATH', '2420'), ('CE', '3700')))
Course(program='JAPN', designation='3891') CourseInfo(credits='3', terms=('Spring', 'Senior'), prereqs=(('JAPN', '3302'),))}

"""