import course_dictionary

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
    """
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
