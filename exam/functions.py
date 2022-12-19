import datetime
from django.utils.timezone import make_aware
from django.utils.translation import gettext_lazy as _

from .models import Result, StudentGroup, Course, Term, Grade

def get_timeover(group, course):
    """Tells if given group have run out of time to finish given course"""
    term = Term.objects.filter(group=group, course=course).first()
    if term.time < make_aware(datetime.datetime.now()):
        return True
    else:
        return False

def test_mark(courses, student):
    """Return list of strings representing status corresponding to each course for a given student"""
    out = []
    for course in courses:
        group = StudentGroup.objects.filter(students=student, courses=course).first()
        timeover = get_timeover(group, course)
        results = sorted(Result.objects.filter(course=course, student=student), key = lambda result:result.current_score)
        if len(results) == 0 and timeover:
            out.append(_("Failed"))
            continue
        elif len(results) == 0:
            out.append(_("Unfinished"))
            continue
        result = results[-1]
        if result.passed == True:
            out.append(_("Passed"))
        elif len(results) >= course.attempt_amount or timeover:
            out.append(_("Failed"))
        else:
            out.append(_("Unfinished"))
    return out

def course_mark(course, students, timeover):
    """Returns list of stings representing status corresponding to each student for a given course"""
    out = []
    for student in students:
        results = sorted(Result.objects.filter(course=course, student=student), key = lambda result:result.current_score)
        if len(results) == 0 and timeover:
            out.append(_("Failed"))
            continue
        elif len(results) == 0:
            out.append(_("Unfinished"))
            continue
        result = results[-1]
        if result.passed == True:
            out.append(_("Passed"))
        elif len(results) >= course.attempt_amount or timeover:
            out.append(_("Failed"))
        else:
            out.append(_("Unfinished"))
    return out

def student_grades(courses, student):
    """Return list of strings representing grades corresponding to each course for a given student"""
    out = []
    grades = sorted(Grade.objects.filter(platform=student.platform_set.first()), key= lambda grade:grade.bar, reverse=True)
    for course in courses:
        course_marked = False
        results = sorted(Result.objects.filter(course=course, student=student), key = lambda result:result.current_score)
        if len(results) == 0:
            out.append(_("None"))
            continue
        result = results[-1]
        score = (result.current_score*100)/course.question_amount
        if len(grades) == 0:
            out.append(round(score))
            continue
        for grade in grades:
            if score > grade.bar:
                out.append(grade.name)
                course_marked = True
                break
        if not course_marked:
            out.append(_("None"))
    return out

def course_grades(course, students):
    """Returns list of stings representing grades corresponding to each student for a given course"""
    out = []
    grades = sorted(Grade.objects.filter(platform=course.platform), key= lambda grade:grade.bar, reverse=True)
    for student in students:
        student_marked = False
        results = sorted(Result.objects.filter(course=course, student=student), key = lambda result:result.current_score)
        if len(results) == 0:
            out.append(_("None"))
            continue
        result = results[-1]
        score = (result.current_score*100)/course.question_amount
        if len(grades) == 0:
            out.append(round(score))
            continue
        for grade in grades:
            if score > grade.bar:
                out.append(grade.name)
                student_marked = True
                break
        if not student_marked:
            out.append(_("None"))
    return out
        
def get_courses_for_student(student):
    """Returns a tuple with a tuple representing data for all courses attached to student
    formatted to be acepted by page and list of all test marks that correspond to courses"""
    test_marks = []
    courses = []
    course_info = []
    index = 0
    groups = StudentGroup.objects.filter(students=student)
    for group in groups:
        group_courses = Course.objects.filter(studentgroup=group)
        test_marks.extend(test_mark(group_courses, student))
        for course in group_courses:
            courses.append(course)
            index += 1
            course_info += [(course.pk, course.name, course.category,index)]
    courses = set(courses)
    return (course_info, test_marks, courses)

def get_categories(courses):
        """Returns a set of all categories found in courses"""
        categories = []
        for course in courses:
            try:
                categories.append(course[2])
            except:
                categories.append(course.category)
        return set(categories)

def get_grade_data(platform):
        grades = Grade.objects.filter(platform=platform)
        if len(grades) == 0:
            return False
        return True