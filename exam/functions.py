from .models import Result, StudentGroup, Course


def test_mark(courses, student):
    """Return list of strings representing status corresponding to each course for a given student"""
    out = []
    for course in courses:
        results = Result.objects.filter(course=course, student=student)
        test_marked = False
        for result in results:
            if result.passed == True and test_marked == False:
                out.append("Zaliczony")
                test_marked = True
        if test_marked == False and len(results) >= course.attempt_amount:
            out.append("Niezaliczony")
        elif test_marked == False:
            out.append("Jeszcze nie ukończony")
    return out

def course_mark(course, students):
    """Returns list of stings representing status corresponding to each student for a given course"""
    out = []
    for student in students:
        results = Result.objects.filter(course=course, student=student)
        test_marked = False
        for result in results:
            if result.passed == True and test_marked == False:
                out.append("Zaliczony")
                test_marked = True
        if test_marked == False and len(results) >= course.attempt_amount:
            out.append("Niezaliczony")
        elif test_marked == False:
            out.append("Jeszcze nie ukończony")
    return out
        
def get_courses_for_student(student):
    """Returns a tuple with a tuple representing data for all courses attached to student
    formatted to be acepted by page and list of all test marks that correspond to courses"""
    test_marks = []
    courses = []
    index = 0
    groups = StudentGroup.objects.filter(students=student)
    for group in groups:
        group_courses = Course.objects.filter(studentgroup=group)
        test_marks.extend(test_mark(group_courses, student))
        for course in group_courses:
            index += 1
            courses += [(course.pk, course.name, course.category,index)]
    return (courses, test_marks)

def get_categories(courses):
        """Returns a set of all categories found in courses"""
        categories = []
        for course in courses:
            try:
                categories.append(course[2])
            except:
                categories.append(course.category)
        return set(categories)