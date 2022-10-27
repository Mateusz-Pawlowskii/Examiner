from .models import Result

def test_mark(courses, student):
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
        