from operator import attrgetter
from exam.models import Result


def get_maximum_result(student, course):
        """returns the result with the highest score from all results
        that given student made while doing exams related to a given course"""
        results = Result.objects.filter(course=course, student=student)
        if results:
            result = max(results, key=attrgetter("current_score")).current_score
            return result
        return 0

def initialize_course_information(course):
    """Creates a dictionary with initial values to be altered further down
    in preparation for course results context"""
    return {"pk" : course.pk,
            "name" : course.name,
            "passed_students" : 0,
            "failed_students" : 0,
            "current_students" : 0,
            "passed_results" : 0,
            "failed_results" : 0,
            "student_amount" : 0
            }

def get_result_data(course_information, course):
    """Adds information about the amount of passing and failing
       results to the page context"""
    results = Result.objects.filter(course=course)
    for result in results:
        if result.passed == True:
            course_information["passed_results"] += 1
        else:
            course_information["failed_results"] += 1
    return course_information