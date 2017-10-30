import sys

import course_dictionary
# import williamju_scheduler


def main(argv):
    test = course_dictionary.create_course_dict()
    #Test to see if all prereqs are in the file.
    # prereq_list = [single_course for vals in test.values()
    #                for some_prereqs in vals.prereqs for single_course in some_prereqs]
    # for prereq in prereq_list:
    #     if prereq not in test:
    #         print(prereq)
    # for key in test:
    #     #Test to see if every course has a term and credits.
    #     if not test[key].terms or not test[key].credits:
    #         print(key)
    #     #Test to see if a course's prereqs include the course itself
    #     if key in [course for prereq in test[key].prereqs for course in prereq]:
    #         print(key)
    # Prints all the CS courses.
    for key in test:
        if key.program == 'CS':
            print(key, test[key])
    print(15 + int(test[("CS", "4260")].credits))
    # williamju_scheduler.course_scheduler (test, [("CS", "major")], [])
    # Prints the entire dictionary.
    # course_dictionary.print_dict(test)
    # print(test[('CS', 'open3')])
    # print('Done')

if __name__ == "__main__":
    main(sys.argv)