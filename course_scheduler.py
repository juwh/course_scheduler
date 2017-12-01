import sys

import course_dictionary
import williamju_scheduler


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
    # for key in test:
    #     if key.program == 'CS':
    #         print(key, test[key])
    #print(test[("ANTH", "4154")].prereqs)
    # Test 2, usual 0 credit semesters
    #solution = williamju_scheduler.course_scheduler (test, [("CS", "2231"), ("CS", "3251"), ("CS", "statsprobability")], [('MATH', '2810'), ("MATH", "2820"), ("MATH", "3640")])
    #solution = williamju_scheduler.course_scheduler(test, [("CS", "major"), ("CS", "2201")], [])
    # solution = williamju_scheduler.course_scheduler(test, [("CS", "major"), ("CS", "4269")], [])
    # Test 3, usual 0 credit semesters
    #solution = williamju_scheduler.course_scheduler(test, [("CS", "core"), ("CS", "1101")], [])
    # Test 6, no errors
    #solution = williamju_scheduler.course_scheduler(test, [("CS", "major"), ('JAPN', '3891')], [('CS', '1101'), ('JAPN', '1101')])
    # Test 8, no errors
    solution = williamju_scheduler.course_scheduler(test, [("CS", "major"), ('JAPN', '2201')], [])
    # Test 7, usual 0 credit semesters
    #solution = williamju_scheduler.course_scheduler(test, [("CS", "mathematics")], [])
    #solution = williamju_scheduler.course_scheduler(test, [("BME", "4900W")], [])
    # Test 4, no errors
    #solution = williamju_scheduler.course_scheduler(test, [("CS", "major")], [('CS', '1101')])
    # Test 5
    #solution = williamju_scheduler.course_scheduler(test, [("CS", "major"), ('ANTH', '4345'), ('ARTS', '3600'), ('ASTR', '3600'), ('BME', '4500'), ('BUS', '2300'), ('CE', '3705')], [])
    # Test 1, usual 0 credit semesters
    #solution = williamju_scheduler.course_scheduler(test, [("CS", "1101")], [])
    # Test 0
    #solution = williamju_scheduler.course_scheduler(test, [("CS", "1101")], [("CS", "1101")])
    #solution = williamju_scheduler.course_scheduler(test, [('ANTH', '4345'), ('ARTS', '3600'), ('BME', '4500'), ('BUS', '2300'), ('CE', '3705'), ('LAT', '3140'), ('JAPN', '3891')], [])
    for course in solution:
        print(course, solution[course])
    #print(solution)
    # Prints the entire dictionary.
    #course_dictionary.print_dict(test)
    # print(test[('CS', 'open3')])
    # print('Done')

if __name__ == "__main__":
    main(sys.argv)